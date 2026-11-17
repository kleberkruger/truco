"""Partida: gerencia o jogo completo de Truco com placar e mãos sequenciais.

A Partida é a classe principal do domínio. Ela:
- Cria e gerencia mãos sequenciais
- Mantém o placar global
- Detecta quando alguém chega a 12 pontos
- Fornece acesso à mão atual para jogadas e trucos
"""

from dominio.baralho import Baralho
from dominio.equipe import Equipe
from dominio.estado import EstadoPartida, Modalidade
from dominio.jogador import Jogador
from dominio.mao import Mao
from dominio.vaza import ResultadoVaza


class Partida:
    """Gerencia uma partida completa de Truco Paulista.

    A partida consiste em múltiplas mãos até que uma equipe
    alcance 12 pontos. Cada mão é gerenciada por uma instância
    de Mao que encapsula as regras de vaza, truco e mão de onze.

    Args:
        equipe1: Primeira equipe.
        equipe2: Segunda equipe.
        limpo: True para baralho limpo (24 cartas), False para sujo (40 cartas).
    """

    def __init__(
        self,
        equipe1: Equipe,
        equipe2: Equipe,
        *,
        limpo: bool = True,
    ) -> None:
        if len(equipe1) != len(equipe2):
            raise ValueError('As equipes devem ter o mesmo número de jogadores')
        if limpo and len(equipe1) == 3:
            raise ValueError('Trios exigem baralho sujo')

        # Verificar jogadores duplicados
        todos = equipe1.jogadores + equipe2.jogadores
        if len({j.id for j in todos}) != len(todos):
            raise ValueError('Um jogador não pode estar nas duas equipes')

        self._equipes = (equipe1, equipe2)
        self._baralho = Baralho(limpo)
        self._pontos = [0, 0]
        self._mao_numero = 0
        self._indice_mao = -1  # Quem começa cada mão (alterna)
        self._vencedor: int | None = None

        # Mão atual (criada sob demanda)
        self._mao: Mao | None = None

    @property
    def equipes(self) -> tuple[Equipe, Equipe]:
        return self._equipes

    @property
    def jogadores(self) -> tuple[Jogador, ...]:
        return tuple(
            j for par in zip(self._equipes[0].jogadores, self._equipes[1].jogadores)
            for j in par
        )

    @property
    def modalidade(self) -> int:
        return len(self._equipes[0])

    @property
    def pontos(self) -> tuple[int, ...]:
        return tuple(self._pontos)

    @property
    def mao_numero(self) -> int:
        return self._mao_numero

    @property
    def vencedor(self) -> int | None:
        return self._vencedor

    @property
    def estado(self) -> EstadoPartida:
        if self._vencedor is not None:
            return EstadoPartida.ENCERRADA
        if self._mao is None:
            return EstadoPartida.AGUARDANDO
        return self._mao.estado

    @property
    def mao_atual(self) -> Mao:
        """Retorna a mão atual. Levanta erro se não há mão ativa."""
        if self._mao is None:
            raise RuntimeError('Nenhuma mão iniciada')
        return self._mao

    @property
    def vira(self):
        return self._mao.vira if self._mao else None

    @property
    def valor_mao(self) -> int:
        return self._mao.valor_mao if self._mao else 1

    @property
    def jogador_da_vez(self) -> Jogador | None:
        return self._mao.jogador_da_vez if self._mao else None

    @property
    def pedido_pendente(self) -> tuple[int, int] | None:
        return self._mao.pedido_pendente if self._mao else None

    @property
    def mao_de_onze(self) -> int | None:
        return self._mao.mao_de_onze if self._mao else None

    @property
    def resultados(self) -> tuple[ResultadoVaza, ...]:
        return self._mao.resultados if self._mao else ()

    @property
    def jogadas_atuais(self):
        return self._mao.jogadas_atuais if self._mao else ()

    def indice_equipe(self, jogador: Jogador) -> int:
        for idx, equipe in enumerate(self._equipes):
            if jogador in equipe.jogadores:
                return idx
        raise ValueError('Jogador não participa desta partida')

    # ------------------------------------------------------------------
    # Controle de mãos
    # ------------------------------------------------------------------

    def iniciar_mao(self) -> None:
        """Inicia uma nova mão, distribuindo cartas."""
        if self._vencedor is not None:
            raise ValueError('Partida já encerrada')
        if self._mao is not None and self._mao.estado == EstadoPartida.JOGANDO:
            raise ValueError('Já existe uma mão em andamento')

        self._mao_numero += 1
        self._indice_mao = (self._indice_mao + 1) % len(self.jogadores)

        self._mao = Mao(self._equipes, self._baralho, self._indice_mao)
        self._mao.iniciar()

        # Verificar mão de onze
        onze = [i for i, pts in enumerate(self._pontos) if pts == 11]
        equipe_onze = onze[0] if len(onze) == 1 else None
        self._mao.configurar_mao_onze(equipe_onze)

    def _concluir_mao(self, equipe_vencedora: int) -> None:
        """Aplica os pontos e verifica se a partida terminou."""
        if self._mao is None:
            return

        self._pontos[equipe_vencedora] += self._mao.valor_mao
        if self._pontos[equipe_vencedora] >= 12:
            self._vencedor = equipe_vencedora
        self._mao = None

    # ------------------------------------------------------------------
    # Delegação à mão atual
    # ------------------------------------------------------------------

    def jogar(self, jogador: Jogador, indice_carta: int) -> ResultadoVaza | None:
        """Joga uma carta e retorna o resultado da vaza se completa."""
        resultado = self.mao_atual.jogar(jogador, indice_carta)
        if resultado is not None:
            # Verificar se a mão terminou
            ganhador = self.mao_atual._ganhador_mao()
            if ganhador is not None:
                self._concluir_mao(ganhador)
        return resultado

    def pode_correr(self, jogador: Jogador) -> bool:
        return self.mao_atual.pode_correr(jogador)

    def correr(self, jogador: Jogador) -> None:
        """Jogador corre a mão atual, concedendo-a à equipe adversária."""
        equipe_vencedora = self.mao_atual.correr(jogador)
        self._concluir_mao(equipe_vencedora)

    def pode_pedir_aumento(self, jogador: Jogador) -> bool:
        return self.mao_atual.pode_pedir_aumento(jogador)

    def pedir_aumento(self, jogador: Jogador) -> int:
        return self.mao_atual.pedir_aumento(jogador)

    def responder_aumento(self, jogador: Jogador, aceitar: bool) -> None:
        resultado = self.mao_atual.responder_aumento(jogador, aceitar)
        if resultado is not None:
            # Quem pediu ganhou (outro correu)
            self._concluir_mao(resultado)

    def contra_aumentar(self, jogador: Jogador) -> int:
        return self.mao_atual.contra_aumentar(jogador)

    def decidir_mao_onze(self, jogador: Jogador, jogar: bool) -> None:
        resultado = self.mao_atual.decidir_mao_onze(jogador, jogar)
        if resultado is not None:
            # Quem recusou perdeu a mão
            self._concluir_mao(resultado)

    # ------------------------------------------------------------------
    # Fábricas
    # ------------------------------------------------------------------

    @classmethod
    def individual(cls, j1: Jogador, j2: Jogador, *, limpo: bool = True) -> 'Partida':
        """Cria uma partida individual (1×1)."""
        return cls(Equipe(j1), Equipe(j2), limpo=limpo)

    @classmethod
    def duplas(
        cls,
        j1: Jogador, j2: Jogador,
        j3: Jogador, j4: Jogador,
        *,
        limpo: bool = True,
    ) -> 'Partida':
        """Cria uma partida de duplas (2×2)."""
        return cls(Equipe(j1, j2), Equipe(j3, j4), limpo=limpo)

    @classmethod
    def trios(cls, *jogadores: Jogador) -> 'Partida':
        """Cria uma partida de trios (3×3) com baralho sujo."""
        if len(jogadores) != 6:
            raise ValueError('Trios exigem exatamente seis jogadores')
        return cls(Equipe(*jogadores[:3]), Equipe(*jogadores[3:]), limpo=False)
