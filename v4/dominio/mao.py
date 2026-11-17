"""Mão: gerencia uma mão individual de Truco.

Uma mão consiste em até 3 vazas, com possibilidade de truco
e decisão de mão de onze. Esta classe é uma máquina de estados
passiva — não faz I/O nem controla fluxo externo.
"""

from dominio.baralho import Baralho
from dominio.carta import Carta
from dominio.equipe import Equipe
from dominio.estado import EstadoPartida
from dominio.jogador import Jogador
from dominio.vaza import Jogada, ResultadoVaza


class Mao:
    """Gerencia uma mão de Truco com suas vazas e apostas.

    A mão é passiva: cada método avança o estado e retorna
    um resultado que o orquestrador (Sessão) deve consumir.

    Args:
        equipes: Tupla com as duas equipes.
        baralho: Baralho compartilhado entre mãos.
        indice_mao: Índice do primeiro jogador desta mão.
    """

    def __init__(
        self,
        equipes: tuple[Equipe, Equipe],
        baralho: Baralho,
        indice_mao: int,
    ) -> None:
        self._equipes = equipes
        self._baralho = baralho
        self._jogadores: tuple[Jogador, ...] = tuple(
            j for par in zip(equipes[0].jogadores, equipes[1].jogadores)
            for j in par
        )
        self._indice_mao = indice_mao
        self._indice_turno = indice_mao

        self.vira: Carta | None = None
        self.valor_mao = 1
        self._estado = EstadoPartida.AGUARDANDO
        self._jogadas_atuais: list[Jogada] = []
        self._resultados: list[ResultadoVaza] = []
        self._ultimo_aumentou: int | None = None
        self._pedido: tuple[int, int] | None = None
        self._mao_onze: int | None = None

    @property
    def estado(self) -> EstadoPartida:
        return self._estado

    @property
    def jogador_da_vez(self) -> Jogador | None:
        if self._estado != EstadoPartida.JOGANDO:
            return None
        return self._jogadores[self._indice_turno]

    @property
    def pedido_pendente(self) -> tuple[int, int] | None:
        return self._pedido

    @property
    def mao_de_onze(self) -> int | None:
        return self._mao_onze

    @property
    def resultados(self) -> tuple[ResultadoVaza, ...]:
        return tuple(self._resultados)

    @property
    def jogadas_atuais(self) -> tuple[Jogada, ...]:
        return tuple(self._jogadas_atuais)

    def indice_equipe(self, jogador: Jogador) -> int:
        for idx, equipe in enumerate(self._equipes):
            if jogador in equipe.jogadores:
                return idx
        raise ValueError('Jogador não participa desta partida')

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    def iniciar(self) -> None:
        """Distribui cartas e prepara a mão para jogar."""
        if self._estado != EstadoPartida.AGUARDANDO:
            raise ValueError('Mão já iniciada')

        jogadores_por_equipe = len(self._equipes[0])
        maos, self.vira = self._baralho.distribuir(jogadores_por_equipe)

        for jogador, cartas in zip(self._jogadores, maos):
            jogador.receber_cartas(cartas)

        self._estado = EstadoPartida.JOGANDO

        # Verificar mão de onze
        # (será configurado pela Partida após criar a mão)

    # ------------------------------------------------------------------
    # Jogadas
    # ------------------------------------------------------------------

    def jogar(self, jogador: Jogador, indice_carta: int) -> ResultadoVaza | None:
        """Registra uma jogada e retorna o resultado da vaza se completa."""
        if self._estado != EstadoPartida.JOGANDO:
            raise ValueError('Não é possível jogar neste momento')
        if jogador is not self.jogador_da_vez:
            raise ValueError('Não é a vez deste jogador')

        carta = jogador.jogar(indice_carta)
        self._jogadas_atuais.append(Jogada(jogador, carta))
        self._indice_turno = (self._indice_turno + 1) % len(self._jogadores)

        if len(self._jogadas_atuais) < len(self._jogadores):
            return None

        return self._fechar_vaza()

    def _fechar_vaza(self) -> ResultadoVaza:
        """Calcula o vencedor da vaza e atualiza o estado."""
        maior_forca = max(j.carta.forca for j in self._jogadas_atuais)
        melhores = [j for j in self._jogadas_atuais if j.carta.forca == maior_forca]

        equipes_vencedoras = {
            self.indice_equipe(j.jogador) for j in melhores
        }
        vencedor = next(iter(equipes_vencedoras)) if len(equipes_vencedoras) == 1 else None

        resultado = ResultadoVaza(
            numero=len(self._resultados) + 1,
            equipe_vencedora=vencedor,
            jogadas=tuple(self._jogadas_atuais),
        )
        self._resultados.append(resultado)
        self._jogadas_atuais.clear()

        # Verificar se a mão terminou
        ganhador_mao = self._ganhador_mao()
        if ganhador_mao is not None:
            return resultado

        # Definir quem começa a próxima vaza
        if vencedor is not None:
            # Vencedor da vaza começa
            melhor_jogador = melhores[0].jogador
            self._indice_turno = self._jogadores.index(melhor_jogador)
        else:
            # Empate: quem começou a vaza começa a próxima
            self._indice_turno = self._jogadores.index(
                self._resultados[-1].jogadas[0].jogador
            )

        return resultado

    def _ganhador_mao(self) -> int | None:
        """Determina se a mão já tem um ganhador.

        Regras do Truco Paulista:
        - Uma equipe que ganha 2 vazas vence a mão.
        - Se cada equipe ganha 1 vaza (1×1), joga-se a vaza 3 de desempate.
        - Após 3 vazas, a equipe que ganhou a terceira vaza vence.
        - Se a terceira vaza empatar, favorece quem ganhou a primeira vaza não empatada.
        - Se todas empatarem, favorece a equipe do jogador da mão.

        Retorna o índice da equipe vencedora ou None se a mão continua.
        """
        r = [v.equipe_vencedora for v in self._resultados]

        if len(r) == 1:
            return None

        # Após 2 vazas — conta quantas cada equipe ganhou
        if len(r) == 2:
            # Filtra apenas vazas decididas (não empatadas)
            decididas = [eq for eq in r if eq is not None]
            if len(decididas) == 0:
                # Ambas empatadas — continua
                return None
            if len(decididas) == 1:
                # Uma empatou, uma decidiu — continua (precisa de 2 para ganhar)
                return None
            # Ambas decididas: mesma equipe ganhou 2?
            if decididas[0] == decididas[1]:
                # Mesma equipe ganhou as duas vazas decididas
                return decididas[0]
            # Cada equipe ganhou uma — vaza de desempate!
            return None

        # Após 3 vazas
        if len(r) == 3:
            if r[2] is not None:
                # Terceira vaza decidida — quem ganhou a vaza 3 vence
                return r[2]
            # Terceira empatou: favorece quem ganhou a primeira vaza não empatada
            for eq in r:
                if eq is not None:
                    return eq
            # Todas empatadas: favorece equipe do jogador da mão
            return self.indice_equipe(
                self._jogadores[self._indice_mao]
            )

        return None

    # ------------------------------------------------------------------
    # Truco / Aposta
    # ------------------------------------------------------------------

    def pode_correr(self, jogador: Jogador) -> bool:
        """Verifica se o jogador pode correr a mão atual."""
        if self._estado != EstadoPartida.JOGANDO:
            return False
        if jogador is not self.jogador_da_vez:
            return False
        if self._mao_onze is not None:
            return False
        return True

    def correr(self, jogador: Jogador) -> int:
        """Jogador corre a mão atual, concedendo-a à equipe adversária.

        Retorna o índice da equipe vencedora (a adversária).
        """
        if not self.pode_correr(jogador):
            raise ValueError('Não é possível correr neste momento')
        equipe = self.indice_equipe(jogador)
        return 1 - equipe

    def pode_pedir_aumento(self, jogador: Jogador) -> bool:
        """Verifica se o jogador pode pedir truco."""
        if self._estado != EstadoPartida.JOGANDO:
            return False
        if jogador is not self.jogador_da_vez:
            return False
        if self._mao_onze is not None:
            return False
        if self.valor_mao >= 12:
            return False
        equipe = self.indice_equipe(jogador)
        if self._ultimo_aumentou == equipe:
            return False
        return True

    def pedir_aumento(self, jogador: Jogador) -> int:
        """Pede aumento de aposta. Retorna o novo valor."""
        if self._estado != EstadoPartida.JOGANDO:
            raise ValueError('Não é possível pedir aumento agora')
        if jogador is not self.jogador_da_vez:
            raise ValueError('Somente o jogador da vez pode pedir aumento')
        if self._mao_onze is not None:
            raise ValueError('Não se pode pedir truco na mão de onze')
        if self.valor_mao >= 12:
            raise ValueError('A mão já vale 12 pontos')

        equipe = self.indice_equipe(jogador)
        if self._ultimo_aumentou == equipe:
            raise ValueError('Somente a equipe adversária pode aumentar novamente')

        novo = {1: 3, 3: 6, 6: 9, 9: 12}[self.valor_mao]
        self._pedido = (equipe, novo)
        self._estado = EstadoPartida.PEDIDO_PENDENTE
        return novo

    def responder_aumento(self, jogador: Jogador, aceitar: bool) -> int | None:
        """Responde a um pedido de aumento.

        Retorna:
            - None se aceitou (mão continua)
            - índice da equipe vencedora se correu
        """
        if self._estado != EstadoPartida.PEDIDO_PENDENTE:
            raise ValueError('Não há pedido pendente')
        if self._pedido is None:
            raise ValueError('Não há pedido pendente')

        solicitante, novo_valor = self._pedido
        equipe = self.indice_equipe(jogador)
        if equipe == solicitante:
            raise ValueError('A própria equipe não pode responder ao pedido')

        self._pedido = None
        if aceitar:
            self.valor_mao = novo_valor
            self._ultimo_aumentou = solicitante
            self._estado = EstadoPartida.JOGANDO
            return None
        else:
            # Quem pediu ganha a mão
            return solicitante

    def contra_aumentar(self, jogador: Jogador) -> int:
        """Contra-aumenta uma aposta pendente (ex: truco → seis)."""
        if self._estado != EstadoPartida.PEDIDO_PENDENTE:
            raise ValueError('Não há pedido pendente')
        if self._pedido is None:
            raise ValueError('Não há pedido pendente')

        solicitante, valor_proposto = self._pedido
        equipe = self.indice_equipe(jogador)
        if equipe == solicitante:
            raise ValueError('Somente a equipe adversária pode aumentar')
        if valor_proposto >= 12:
            raise ValueError('A aposta já atingiu 12 pontos')

        proximo = {3: 6, 6: 9, 9: 12}.get(valor_proposto)
        if proximo is None:
            raise ValueError('Não existe próximo valor de aposta')

        self._pedido = (equipe, proximo)
        self._indice_turno = self._jogadores.index(jogador)
        return proximo

    # ------------------------------------------------------------------
    # Mão de onze
    # ------------------------------------------------------------------

    def decidir_mao_onze(self, jogador: Jogador, jogar: bool) -> int | None:
        """Decide a mão de onze.

        Retorna:
            - None se decidiu jogar (mão continua valendo 3)
            - índice da equipe vencedora se decidiu correr
        """
        if self._estado != EstadoPartida.JOGANDO:
            raise ValueError('Não existe decisão de mão de onze pendente')
        if self._mao_onze is None:
            raise ValueError('Não existe decisão de mão de onze pendente')
        if self._resultados or self._jogadas_atuais:
            raise ValueError('A decisão deve acontecer antes da primeira jogada')

        equipe = self.indice_equipe(jogador)
        if equipe != self._mao_onze:
            raise ValueError('Somente a equipe com onze pontos decide')

        self._mao_onze = None
        if jogar:
            self.valor_mao = 3
            return None
        else:
            return 1 - equipe

    # ------------------------------------------------------------------
    # Configuração externa
    # ------------------------------------------------------------------

    def configurar_mao_onze(self, equipe_onze: int | None) -> None:
        """Configura a mão de onze após iniciar().

        Chamado pela Partida que conhece o placar global.
        """
        self._mao_onze = equipe_onze
