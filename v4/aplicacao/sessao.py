"""Sessão: orquestra turnos, bots e ações do jogador humano.

A Sessão é o coração da camada de aplicação. Ela:
- Cria a partida com um jogador humano e bots
- Emite eventos para a interface
- Gerencia as ações do jogador humano
- Controla os bots via estratégia de IA
- Rastreia se é a vez do humano
"""

import random
from dominio.carta import Carta
from dominio.equipe import Equipe
from dominio.estado import EstadoPartida
from dominio.jogador import Jogador
from dominio.partida import Partida
from dominio.vaza import ResultadoVaza
from estrategia.ia import IA, Dificuldade
from aplicacao.evento import Evento


# Nomes padrão para bots
NOMES_PADRAO = ['Você', 'Diogo', 'Vinícius', 'Rhana', 'Thiago', 'Alan']


class Sessao:
    """Orquestra uma sessão de jogo com um humano e bots.

    A Sessão não importa nenhuma biblioteca gráfica — é pura lógica
    de coordenação entre domínio e interface.

    Args:
        modalidade: 1 (individual), 2 (duplas) ou 3 (trios).
        limpo: True para baralho limpo, False para sujo.
        dificuldade: Nível de dificuldade dos bots.
        nomes: Lista de nomes para os jogadores.
        seed: Semente para reprodutibilidade dos bots.
    """

    def __init__(
        self,
        modalidade: int = 2,
        limpo: bool = True,
        dificuldade: Dificuldade = Dificuldade.MEDIO,
        nomes: list[str] | None = None,
        seed: int | None = None,
    ) -> None:
        if modalidade not in (1, 2, 3):
            raise ValueError('Modalidade deve ser 1, 2 ou 3')
        if modalidade == 3:
            limpo = False

        nomes = nomes or NOMES_PADRAO[:]
        total_jogadores = modalidade * 2
        if len(nomes) < total_jogadores:
            raise ValueError('Nomes insuficientes para a modalidade')

        self._rng = random.Random(seed)
        self._dificuldade = dificuldade

        # Criar jogador humano
        self._humano = Jogador(nomes[0])

        # Criar todos os jogadores
        jogadores = [Jogador(n) for n in nomes[:total_jogadores]]
        jogadores[0] = self._humano

        # Distribuir em equipes alternadas
        equipe_a = [jogadores[i] for i in range(0, total_jogadores, 2)]
        equipe_b = [jogadores[i] for i in range(1, total_jogadores, 2)]

        self._partida = Partida(
            Equipe(*equipe_a),
            Equipe(*equipe_b),
            limpo=limpo,
        )

        # IA para cada bot
        self._ias: dict[Jogador, IA] = {}
        for j in jogadores:
            if j is not self._humano:
                self._ias[j] = IA(dificuldade, self._rng.randint(0, 10000))

        # Eventos
        self._eventos: list[Evento] = []
        self._ultima_vaza: ResultadoVaza | None = None

        # Iniciar primeira mão
        self._partida.iniciar_mao()
        self._emitir('mao', 'Nova mão! Boa sorte.')

    # ------------------------------------------------------------------
    # Propriedades de acesso
    # ------------------------------------------------------------------

    @property
    def humano(self) -> Jogador:
        return self._humano

    @property
    def partida(self) -> Partida:
        return self._partida

    @property
    def eventos(self) -> list[Evento]:
        return self._eventos

    @property
    def ultima_vaza(self) -> ResultadoVaza | None:
        return self._ultima_vaza

    @property
    def precisa_humano(self) -> bool:
        """True se é a vez do jogador humano agir."""
        p = self._partida
        return (
            p.estado == EstadoPartida.JOGANDO
            and p.mao_de_onze is None
            and p.jogador_da_vez is self._humano
        )

    @property
    def dificuldade(self) -> Dificuldade:
        return self._dificuldade

    # ------------------------------------------------------------------
    # Ações do jogador humano
    # ------------------------------------------------------------------

    def jogar(self, indice: int) -> None:
        """Humano joga uma carta pelo índice."""
        if not self.precisa_humano:
            raise ValueError('Aguarde sua vez')
        self._executar_jogada(self._humano, indice)

    def pode_trucar(self) -> bool:
        """Verifica se o humano pode pedir truco."""
        if self._partida.estado != EstadoPartida.JOGANDO:
            return False
        return self._partida.pode_pedir_aumento(self._humano)

    def pedir_truco(self) -> None:
        """Humano pede aumento de aposta."""
        if not self.pode_trucar():
            raise ValueError('Não é possível aumentar agora')
        valor = self._partida.pedir_aumento(self._humano)
        self._emitir('pedido', f'Você pediu {valor}!')

    def responder(self, aceitar: bool) -> None:
        """Humano responde a um pedido de truco."""
        p = self._partida
        if p.estado != EstadoPartida.PEDIDO_PENDENTE:
            raise ValueError('Não há pedido pendente')
        solicitante, valor = p.pedido_pendente
        if solicitante == 0:
            raise ValueError('O pedido é seu: aguarde o adversário')
        # O humano está na equipe 0, o solicitante é da equipe 1 (adversário)
        p.responder_aumento(self._humano, aceitar)
        if aceitar:
            self._emitir('resposta', f'Você aceitou {valor}!')
        else:
            self._emitir('resposta', 'Você correu da aposta')

    def aumentar(self) -> None:
        """Humano contra-aumenta uma aposta pendente."""
        p = self._partida
        if p.estado != EstadoPartida.PEDIDO_PENDENTE or p.pedido_pendente is None:
            raise ValueError('Não há pedido pendente')
        solicitante, valor = p.pedido_pendente
        if solicitante == 0:
            raise ValueError('O pedido é da sua equipe')
        novo = p.contra_aumentar(self._humano)
        self._emitir('pedido', f'Você aumentou para {novo}!')

    def decidir_onze(self, jogar: bool) -> None:
        """Humano decide a mão de onze."""
        p = self._partida
        if p.mao_de_onze != 0:
            raise ValueError('A decisão não pertence ao seu lado')
        p.decidir_mao_onze(self._humano, jogar)
        self._emitir('onze', 'Mão de onze aceita' if jogar else 'Mão de onze recusada')

    # ------------------------------------------------------------------
    # Controle de bots
    # ------------------------------------------------------------------

    def avancar_bot(self) -> bool:
        """Executa uma única decisão automática de um bot.

        Returns:
            True se um bot agiu, False se não há ação de bot pendente.
        """
        p = self._partida

        if p.estado in (EstadoPartida.ENCERRADA, EstadoPartida.AGUARDANDO):
            return False

        # Mão de onze
        if p.mao_de_onze is not None:
            if p.mao_de_onze == 0:
                return False  # Aguarda humano
            bot = p.equipes[1].jogadores[0]
            p.decidir_mao_onze(bot, True)
            self._emitir('onze', 'Adversários aceitaram a mão de onze')
            return True

        # Pedido pendente
        if p.estado == EstadoPartida.PEDIDO_PENDENTE:
            solicitante, valor = p.pedido_pendente
            if solicitante == 1:
                return False  # Aguarda resposta do humano (adversário pediu)
            # Humano pediu, bot responde
            bot = p.equipes[1].jogadores[0]
            ia = self._ias[bot]
            forca = ia.forca_mao(bot.cartas)
            aceitar = ia.deve_aceitar_truco(forca, valor)
            p.responder_aumento(bot, aceitar)
            self._emitir('resposta', f'Adversários {"aceitaram" if aceitar else "correram"}!')
            return True

        # Jogada normal
        jogador = p.jogador_da_vez
        if jogador is None or jogador is self._humano:
            return False

        ia = self._ias.get(jogador)
        if ia is None:
            return False

        cartas = jogador.cartas
        if not cartas:
            return False

        # Cartas na mesa
        cartas_mesa = [j.carta for j in p.jogadas_atuais]

        # Rodadas vencidas pela equipe do bot
        equipe_idx = p.indice_equipe(jogador)
        rodadas_vencidas = sum(
            1 for r in p.resultados
            if r.equipe_vencedora == equipe_idx
        )

        indice = ia.escolher_carta(jogador, cartas_mesa, rodadas_vencidas, len(p.resultados))
        self._executar_jogada(jogador, indice)
        return True

    # ------------------------------------------------------------------
    # Controle de mãos
    # ------------------------------------------------------------------

    def proxima_mao(self) -> bool:
        """Inicia a próxima mão.

        Returns:
            True se a mão foi iniciada, False se não é possível.
        """
        if self._partida.estado != EstadoPartida.AGUARDANDO:
            return False
        self._ultima_vaza = None
        self._partida.iniciar_mao()
        self._emitir('mao', f'Mão {self._partida.mao_numero} iniciada')
        return True

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _executar_jogada(self, jogador: Jogador, indice: int) -> None:
        """Executa uma jogada e emite eventos."""
        p = self._partida
        carta = jogador.cartas[indice]
        resultado = p.jogar(jogador, indice)
        self._emitir('carta', f'{jogador.nome} jogou {carta}')

        if resultado is not None:
            self._ultima_vaza = resultado
            if resultado.equipe_vencedora is None:
                self._emitir('vaza', f'Vaza {resultado.numero}: empate!')
            else:
                self._emitir('vaza', f'Vaza {resultado.numero}: equipe {resultado.equipe_vencedora + 1} venceu')

        if p.estado in (EstadoPartida.AGUARDANDO, EstadoPartida.ENCERRADA):
            self._emitir('mao_fim', f'Placar: {p.pontos[0]} × {p.pontos[1]}')

    def _emitir(self, tipo: str, mensagem: str) -> None:
        """Emite um evento para a interface."""
        self._eventos.append(Evento(tipo, mensagem))
        # Manter apenas os últimos 50 eventos
        if len(self._eventos) > 50:
            self._eventos = self._eventos[-50:]
