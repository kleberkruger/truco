"""Máquina de estado passiva do jogo de Truco.

Esta classe não possui loops nem faz I/O.  Cada método avança o estado do
jogo e retorna um objeto de estado (definido em `estados.py`) que o frontend
ativo deve consumir e exibir.

Fluxo típico de uso pelo frontend:
    1. partida = Partida(config)
    2. estado = partida.iniciar_mao()
    3. while not isinstance(estado, EstadoFimPartida):
           frontend.exibir(estado)
           if isinstance(estado, EstadoPedirCarta):
               carta = frontend.escolher_carta(estado)
               estado = partida.jogar_carta(ComandoCarta(carta))
           elif isinstance(estado, EstadoPedirDecisaoTruco):
               decisao = frontend.pedir_decisao(estado)
               estado = partida.responder_truco(decisao)
           else:
               estado = partida.proximo()
"""

import random

from baralho import Baralho, Carta
from jogador import (
    Jogador,
    JogadorHumano,
    JogadorIA,
    JogadorHumanoFrontend,
    JogadaCarta,
    JogadaTruco,
    JogadaCorrer,
)
from estados import (
    Lado,
    FaseMao,
    ConfiguracaoJogo,
    EstadoPlacar,
    EstadoInicioMao,
    EstadoCartasMao,
    EstadoInicioRodada,
    EstadoPedirCarta,
    EstadoCartaJogada,
    EstadoVencedorRodada,
    EstadoPropostaTruco,
    EstadoPedirDecisaoTruco,
    EstadoRespostaTruco,
    EstadoResultadoMao,
    EstadoFimPartida,
    ComandoCarta,
    ComandoDecisaoTruco,
    ComandoPropostaTruco,
)


class Partida:
    """Máquina de estado passiva que gerencia uma partida de Truco.

    O frontend é o agente ativo: ele chama os métodos desta classe para
    avançar o jogo e exibe os estados retornados.

    :param config: Configuração da partida (nomes, dificuldade, baralho).
    :param frontend: Protocolo opcional injetado no JogadorHumano.
    """

    def __init__(self, config: ConfiguracaoJogo, frontend: JogadorHumanoFrontend | None = None):
        self._config = config
        self._baralho = Baralho(config.baralho_limpo)

        # Criar jogadores
        self._humano = JogadorHumano(config.nome_humano, frontend) if frontend else JogadorHumano(config.nome_humano, None)  # type: ignore[arg-type]
        self._ia = JogadorIA(config.nome_ia, config.dificuldade)

        self._pontos_a = 0  # humano
        self._pontos_b = 0  # IA
        self._numero_mao = 0

        # Estado da mão atual
        self._fase_mao = FaseMao.EM_ANDAMENTO
        self._rodadas_a = 0
        self._rodadas_b = 0
        self._pontuacao_mao = 1
        self._numero_rodada = 0
        self._jogador_inicial: Jogador | None = None
        self._jogador_atual: Jogador | None = None
        self._maior_carta: Carta | None = None
        self._vencedor_rodada: Jogador | None = None
        self._cartas_jogadas: int = 0
        self._vira: Carta | None = None
        self._primeiro_vencedor_rodada2: Lado | None = None

        # Estado interno: qual estado retornar no próximo proximo()
        self._proximo_estado = None
        
        # Truco: quem propôs a última proposta (para saber quem ganha se o outro correr)
        self._propositor_atual: Jogador | None = None
        self._pontuacao_proposta_pendente: int | None = None

    # ------------------------------------------------------------------
    # Métodos públicos — chamados pelo frontend ativo
    # ------------------------------------------------------------------

    def iniciar_mao(self):
        """Inicia uma nova mão e retorna o estado inicial."""
        self._numero_mao += 1
        self._fase_mao = FaseMao.EM_ANDAMENTO
        self._rodadas_a = 0
        self._rodadas_b = 0
        self._pontuacao_mao = 1
        self._primeiro_vencedor_rodada2 = None

        # Determinar jogador inicial (alterna a cada mão)
        self._jogador_inicial = self._humano if self._numero_mao % 2 == 1 else self._ia

        # Distribuir cartas
        cartas, vira = self._baralho.distribuir_cartas(jogadores_por_equipe=1)
        self._vira = vira
        self._humano.iniciar_mao(cartas[0], vira)
        self._ia.iniciar_mao(cartas[1], vira)

        # O primeiro estado a exibir é o início da mão
        self._proximo_estado = EstadoInicioMao(self._numero_mao)
        return self._proximo_estado

    def jogar_carta(self, comando: ComandoCarta):
        """Registra a carta jogada pelo humano e avança o estado."""
        carta = comando.carta

        # Remover carta da mão do humano
        idx = self._humano.cartas.index(carta)
        self._humano.cartas.pop(idx)

        # Avaliar a jogada
        self._avaliar_jogada(self._humano, carta)

        # Avançar jogador
        self._cartas_jogadas += 1
        if self._cartas_jogadas >= 2:
            # Rodada completa — calcular vencedor
            self._finalizar_rodada()
        else:
            # IA joga automaticamente
            self._ia_joga()

        return self._proximo_estado

    def responder_truco(self, comando: ComandoDecisaoTruco):
        """Processa a resposta do humano a uma proposta de truco."""
        if comando.aceita:
            if comando.pontuacao_contra_oferta:
                # Contra-oferta: atualizar pontuação da mão
                self._pontuacao_mao = comando.pontuacao_contra_oferta
                self._proximo_estado = EstadoRespostaTruco(
                    aceita=True,
                    pontuacao_contra_oferta=comando.pontuacao_contra_oferta,
                )
            else:
                # Aceita a proposta
                self._pontuacao_mao = self._obter_pontuacao_proposta_atual()
                self._proximo_estado = EstadoRespostaTruco(
                    aceita=True,
                    pontuacao_contra_oferta=None,
                )
        else:
            # Correu — mão finalizada para o oponente
            self._fase_mao = FaseMao.FINALIZADA
            if self._obter_propositor() is self._ia:
                # IA propôs, humano correu — IA ganha
                self._pontos_b += self._pontuacao_mao
                self._proximo_estado = EstadoResultadoMao(
                    lado_ganhador=Lado.LADO_B,
                    pontos=self._pontuacao_mao,
                    nome_a=self._config.nome_humano,
                    nome_b=self._config.nome_ia,
                )
            else:
                # Humano propôs, IA correu — humano ganha
                self._pontos_a += self._pontuacao_mao
                self._proximo_estado = EstadoResultadoMao(
                    lado_ganhador=Lado.LADO_A,
                    pontos=self._pontuacao_mao,
                    nome_a=self._config.nome_humano,
                    nome_b=self._config.nome_ia,
                )

        return self._proximo_estado

    def propor_truco(self, comando: ComandoPropostaTruco):
        """Humano propõe truco/seis/nove/doze.
        
        :param comando: Comando com a pontuação proposta (3, 6, 9 ou 12).
        :return: Estado da proposta do humano (EstadoPropostaTruco).
            O frontend deve chamar processar_resposta_proposta_truco() em seguida
            para obter a decisão da IA.
        """
        pontuacao_proposta = comando.pontuacao_proposta
        
        # Validação: a proposta deve ser maior que a pontuação atual
        if pontuacao_proposta <= self._pontuacao_mao:
            self._preparar_pedir_carta()
            return self._proximo_estado
        
        # Validação: a proposta deve ser um valor válido
        if pontuacao_proposta not in (3, 6, 9, 12):
            self._preparar_pedir_carta()
            return self._proximo_estado
        
        # Registrar que o humano propôs
        self._propositor_atual = self._humano
        self._pontuacao_proposta_pendente = pontuacao_proposta
        
        self._proximo_estado = EstadoPropostaTruco(
            nome_propositor=self._config.nome_humano,
            pontuacao_atual=self._pontuacao_mao,
            pontuacao_proposta=pontuacao_proposta,
        )
        return self._proximo_estado
    
    def processar_resposta_proposta_truco(self):
        """Processa a resposta da IA após uma proposta de truco do humano.
        
        :return: Estado resultante da decisão da IA (EstadoRespostaTruco ou EstadoResultadoMao).
        """
        assert self._pontuacao_proposta_pendente is not None
        pontuacao_proposta = self._pontuacao_proposta_pendente
        self._pontuacao_proposta_pendente = None
        return self._ia_decide_truco(pontuacao_proposta)

    def proximo(self):
        """Avança para o próximo estado quando não há interação necessária."""
        return self._proximo_estado

    # ------------------------------------------------------------------
    # Métodos de consulta — o frontend pode ler o estado a qualquer momento
    # ------------------------------------------------------------------

    def get_placar(self) -> EstadoPlacar:
        """Retorna o placar atual."""
        return EstadoPlacar(
            pontos_a=self._pontos_a,
            pontos_b=self._pontos_b,
            nome_a=self._config.nome_humano,
            nome_b=self._config.nome_ia,
        )

    def get_cartas_humano(self) -> EstadoCartasMao:
        """Retorna as cartas do jogador humano e a carta virada."""
        return EstadoCartasMao(
            cartas=self._humano.cartas,
            vira=self._vira,
        )

    def is_partida_finalizada(self) -> bool:
        """Retorna True se algum lado atingiu 12 pontos."""
        return self._pontos_a >= 12 or self._pontos_b >= 12

    def is_mao_finalizada(self) -> bool:
        """Retorna True se a mão atual foi finalizada."""
        return self._fase_mao == FaseMao.FINALIZADA

    def get_fim_partida(self) -> EstadoFimPartida:
        """Retorna o estado de fim de partida."""
        lado_ganhador = Lado.LADO_A if self._pontos_a >= 12 else Lado.LADO_B
        return EstadoFimPartida(
            lado_ganhador=lado_ganhador,
            pontos_a=self._pontos_a,
            pontos_b=self._pontos_b,
            nome_a=self._config.nome_humano,
            nome_b=self._config.nome_ia,
        )

    # ------------------------------------------------------------------
    # Lógica interna da máquina de estado
    # ------------------------------------------------------------------

    def _ia_joga(self):
        """IA joga automaticamente quando é a vez dela.
        
        Após jogar, verifica se a IA quer propor truco antes de pedir
        a carta ao humano.
        """
        vencidas = self._rodadas_b
        jogada = self._ia.jogar(self._numero_rodada, vencidas, self._maior_carta)
        carta = jogada.carta if isinstance(jogada, JogadaCarta) else None

        if carta is not None:
            self._avaliar_jogada(self._ia, carta)
            self._cartas_jogadas += 1

            if self._cartas_jogadas >= 2:
                self._finalizar_rodada()
            else:
                # Verificar se a IA quer propor truco antes de pedir carta ao humano
                proposta = self.verificar_proposta_ia()
                if proposta is not None:
                    # IA propôs truco — o próximo estado é EstadoPedirDecisaoTruco
                    # O frontend vai exibir a proposta e pedir a decisão do humano
                    return
                # Sem proposta — pedir carta ao humano normalmente
                self._preparar_pedir_carta()

    def _avaliar_jogada(self, jogador: Jogador, carta: Carta):
        """Avalia se a carta jogada é a maior da mesa."""
        # Retornar estado da carta jogada
        self._proximo_estado = EstadoCartaJogada(
            nome_jogador=jogador.nome,
            carta=carta,
        )

        if self._maior_carta is None or carta > self._maior_carta:
            self._maior_carta = carta
            self._vencedor_rodada = jogador
        elif carta == self._maior_carta:
            self._vencedor_rodada = None  # empate

    def _finalizar_rodada(self):
        """Finaliza a rodada atual e pontua."""
        # Determinar lado vencedor
        if self._vencedor_rodada is self._humano:
            self._rodadas_a += 1
            lado_vencedor = Lado.LADO_A
        elif self._vencedor_rodada is self._ia:
            self._rodadas_b += 1
            lado_vencedor = Lado.LADO_B
        else:
            lado_vencedor = None

        # Estado do vencedor da rodada
        self._proximo_estado = EstadoVencedorRodada(
            nome_vencedor=self._vencedor_rodada.nome if self._vencedor_rodada else None,
            lado_vencedor=lado_vencedor,
        )

        # Verificar se a mão terminou
        if self._verificar_fim_mao(lado_vencedor):
            return

        # Preparar próxima rodada
        self._numero_rodada += 1
        self._maior_carta = None
        self._vencedor_rodada = None
        self._cartas_jogadas = 0

        # Determinar jogador inicial da próxima rodada
        if self._vencedor_rodada is not None:
            self._jogador_inicial = self._vencedor_rodada

        self._preparar_proxima_rodada()

    def _verificar_fim_mao(self, lado_vencedor: Lado | None) -> bool:
        """Verifica se a mão terminou após a rodada atual. Retorna True se terminou."""
        # Após rodada 1: continua sempre
        if self._numero_rodada == 1:
            return False

        if self._rodadas_a >= 2:
            self._finalizar_mao(Lado.LADO_A)
            return True
        if self._rodadas_b >= 2:
            self._finalizar_mao(Lado.LADO_B)
            return True

        # Após rodada 2: quem lidera ganha
        if self._numero_rodada == 2:
            if self._rodadas_a == 1 and self._rodadas_b == 0:
                self._finalizar_mao(Lado.LADO_A)
                return True
            if self._rodadas_a == 0 and self._rodadas_b == 1:
                self._finalizar_mao(Lado.LADO_B)
                return True
            self._primeiro_vencedor_rodada2 = lado_vencedor
            return False

        # Rodada 3
        if self._numero_rodada == 3:
            if self._rodadas_a > self._rodadas_b:
                self._finalizar_mao(Lado.LADO_A)
            elif self._rodadas_b > self._rodadas_a:
                self._finalizar_mao(Lado.LADO_B)
            else:
                # Empate 1x1x1 — quem ganhou após rodada 2 decide
                lado = self._primeiro_vencedor_rodada2 if self._primeiro_vencedor_rodada2 else Lado.LADO_A
                self._finalizar_mao(lado)
            return True

        return False

    def _finalizar_mao(self, lado_ganhador: Lado):
        """Finaliza a mão e pontua."""
        self._fase_mao = FaseMao.FINALIZADA
        if lado_ganhador == Lado.LADO_A:
            self._pontos_a += self._pontuacao_mao
        else:
            self._pontos_b += self._pontuacao_mao

        self._proximo_estado = EstadoResultadoMao(
            lado_ganhador=lado_ganhador,
            pontos=self._pontuacao_mao,
            nome_a=self._config.nome_humano,
            nome_b=self._config.nome_ia,
        )

    def _preparar_proxima_rodada(self):
        """Prepara o estado para o início da próxima rodada."""
        jogador = self._jogador_inicial
        self._jogador_atual = jogador

        if jogador is self._humano:
            # Humano joga primeiro — pedir carta
            self._preparar_pedir_carta()
        else:
            # IA joga primeiro
            self._proximo_estado = EstadoInicioRodada(
                numero_rodada=self._numero_rodada,
                nome_jogador=jogador.nome,
                vez_humano=False,
            )
            self._ia_joga()

    def _preparar_pedir_carta(self):
        """Prepara o estado para pedir uma carta ao humano."""
        self._proximo_estado = EstadoPedirCarta(
            cartas_disponiveis=self._humano.cartas,
            numero_rodada=self._numero_rodada,
            rodadas_vencidas=self._rodadas_a,
            maior_carta_mesa=self._maior_carta,
            vira=self._vira,
            pontuacao_mao=self._pontuacao_mao,
        )

    # ------------------------------------------------------------------
    # Truco / Seis / Nove / Doze
    # ------------------------------------------------------------------

    def _obter_pontuacao_proposta_atual(self) -> int:
        """Retorna a pontuação proposta atual (usada quando humano aceita)."""
        return self._pontuacao_mao

    def _obter_propositor(self) -> Jogador:
        """Retorna quem fez a última proposta de truco."""
        return self._propositor_atual if self._propositor_atual is not None else self._ia

    def _ia_decide_truco(self, pontuacao_proposta: int):
        """IA decide se aceita ou corre de uma proposta do humano."""
        decisao = self._ia.decidir_proposta(self._pontuacao_mao, pontuacao_proposta)

        if isinstance(decisao, JogadaCorrer):
            # IA correu — humano ganha a mão
            self._fase_mao = FaseMao.FINALIZADA
            self._pontos_a += self._pontuacao_mao
            return EstadoResultadoMao(
                lado_ganhador=Lado.LADO_A,
                pontos=self._pontuacao_mao,
                nome_a=self._config.nome_humano,
                nome_b=self._config.nome_ia,
            )
        else:
            # IA aceitou ou contra-ofereceu
            if isinstance(decisao, JogadaTruco):
                self._pontuacao_mao = decisao.pontuacao_alvo
            return EstadoRespostaTruco(
                aceita=True,
                pontuacao_contra_oferta=decisao.pontuacao_alvo if isinstance(decisao, JogadaTruco) else None,
            )

    # ------------------------------------------------------------------
    # Proposta de truco pela IA
    # ------------------------------------------------------------------

    @property
    def tem_proposta_pendente(self) -> bool:
        """Indica se há uma proposta de truco pendente aguardando resposta da IA.
        
        Usado pelo frontend para saber se deve chamar processar_resposta_proposta_truco().
        """
        return self._pontuacao_proposta_pendente is not None

    def verificar_proposta_ia(self) -> EstadoPedirDecisaoTruco | None:
        """Verifica se a IA quer propor truco após uma jogada.
        
        A IA considera:
        1. A força da mão atual (cartas restantes).
        2. O contexto do jogo (rodadas vencidas, número da rodada).
        3. Um elemento de blefe (probabilidade baixa de propor com mão fraca).
        
        :return: EstadoPedirDecisaoTruco se a IA propuser, None caso contrário.
        """
        if self._pontuacao_mao >= 12:
            return None
        
        # Não propor se já houver uma proposta pendente
        if self._pontuacao_proposta_pendente is not None:
            return None
        
        forca_mao = self._ia.forca_mao()
        
        # Fator de contexto: a IA é mais propensa a propor se está vencendo rodadas
        rodadas_vantagem = self._rodadas_b - self._rodadas_a
        fator_contexto = rodadas_vantagem * 0.1  # +0.1 por rodada a favor
        
        # Probabilidade base de propor truco
        probabilidade = forca_mao + fator_contexto
        
        # Elemento de blefe: mesmo com mão fraca, a IA pode tentar blefar
        # (probabilidade de 10% para blefar)
        if random.random() < 0.1:
            probabilidade = max(probabilidade, 0.5)
        
        # Decisão: propor se a probabilidade ajustada for > 0.6
        if probabilidade > 0.6:
            proximas = [p for p in (3, 6, 9, 12) if p > self._pontuacao_mao]
            if proximas:
                # IA escolhe o nível de proposta baseado na força
                if forca_mao > 0.8:
                    proposta = proximas[-1]  # vai até o máximo
                else:
                    proposta = proximas[0]   # só sobe um nível
                
                self._propositor_atual = self._ia
                self._proximo_estado = EstadoPedirDecisaoTruco(
                    pontuacao_atual=self._pontuacao_mao,
                    pontuacao_proposta=proposta,
                )
                return self._proximo_estado
        
        return None

    @property
    def humano(self) -> JogadorHumano:
        return self._humano

    @property
    def ia(self) -> JogadorIA:
        return self._ia
