from dataclasses import dataclass
from enum import Enum, IntEnum, auto

from dominio.baralho import Baralho, Carta
from dominio.participante import Equipe, Jogador


class Modalidade(IntEnum):
    INDIVIDUAL = 1
    DUPLAS = 2
    TRIOS = 3


class Estado(Enum):
    AGUARDANDO = auto()
    JOGANDO = auto()
    PEDIDO_PENDENTE = auto()
    ENCERRADA = auto()


@dataclass(frozen=True, slots=True)
class Jogada:
    jogador: Jogador
    carta: Carta


@dataclass(frozen=True, slots=True)
class ResultadoVaza:
    numero: int
    vencedor: int | None  # 0 ou 1; None significa empate
    jogadas: tuple[Jogada, ...]


class Partida:
    """Truco Paulista: vira, manilha móvel e disputa até 12 pontos.

    Convenções: equipes na ordem alternada dos turnos; empate na primeira
    vaza seguido de vitória atribui a mão à vencedora; empate na segunda
    após vitória na primeira favorece quem venceu a primeira; empate na
    terceira favorece a vencedora da primeira. Três empates favorecem
    a equipe mão (a que começa a mão). Não implementa mão de ferro.
    """

    def __init__(self, equipe1: Equipe, equipe2: Equipe, *, limpo: bool = True):
        if len(equipe1) != len(equipe2):
            raise ValueError('As equipes devem ter o mesmo número de jogadores')
        if limpo and len(equipe1) == 3:
            raise ValueError('Trios exigem baralho sujo')
        jogadores = equipe1.jogadores + equipe2.jogadores
        if len({j.id for j in jogadores}) != len(jogadores):
            raise ValueError('Um jogador não pode estar nas duas equipes')

        self.equipes = (equipe1, equipe2)
        self.baralho = Baralho(limpo)
        self.pontos = [0, 0]
        self.estado = Estado.AGUARDANDO
        self.vira: Carta | None = None
        self.valor_mao = 1
        self.resultados: list[ResultadoVaza] = []
        self.jogadas: list[Jogada] = []
        self.mao_numero = 0
        self._ordem = tuple(
            j for par in zip(equipe1.jogadores, equipe2.jogadores) for j in par
        )
        self._indice_mao = -1
        self._indice_turno = 0
        self._ultimo_aumentou: int | None = None
        self._pedido: tuple[int, int] | None = None
        self._mao_onze: int | None = None
        self.vencedor: int | None = None

    @property
    def modalidade(self) -> Modalidade:
        return Modalidade(len(self.equipes[0]))

    @property
    def jogadores(self) -> tuple[Jogador, ...]:
        return self._ordem

    def pode_pedir_aumento(self, jogador: Jogador) -> bool:
        if self.estado != Estado.JOGANDO or jogador is not self.jogador_da_vez:
            return False
        if self._mao_onze is not None or self.valor_mao == 12:
            return False
        return self._ultimo_aumentou != self.indice_equipe(jogador)

    @property
    def jogador_da_vez(self) -> Jogador | None:
        if self.estado != Estado.JOGANDO:
            return None
        return self._ordem[self._indice_turno]

    @property
    def pedido_pendente(self) -> tuple[int, int] | None:
        return self._pedido

    @property
    def mao_de_onze(self) -> int | None:
        return self._mao_onze

    def indice_equipe(self, jogador: Jogador) -> int:
        for indice, equipe in enumerate(self.equipes):
            if jogador in equipe.jogadores:
                return indice
        raise ValueError('Jogador não participa desta partida')

    def iniciar_mao(self) -> None:
        if self.estado not in (Estado.AGUARDANDO,):
            raise ValueError('Não é possível iniciar outra mão agora')
        self.mao_numero += 1
        self._indice_mao = (self._indice_mao + 1) % len(self._ordem)
        self._indice_turno = self._indice_mao
        self.valor_mao = 1
        self._ultimo_aumentou = None
        self._pedido = None
        self.resultados.clear()
        self.jogadas.clear()
        maos, self.vira = self.baralho.distribuir_cartas(len(self.equipes[0]))
        for jogador, cartas in zip(self._ordem, maos):
            jogador.receber_cartas(cartas)
        onze = [i for i, pontos in enumerate(self.pontos) if pontos == 11]
        self._mao_onze = onze[0] if len(onze) == 1 else None
        self.estado = Estado.JOGANDO

    def jogar(self, jogador: Jogador, indice_carta: int) -> ResultadoVaza | None:
        if self._mao_onze is not None:
            raise ValueError("É preciso decidir a mão de onze antes de jogar")
        if self.estado != Estado.JOGANDO:
            raise ValueError('A partida não está aceitando jogadas')
        if jogador is not self.jogador_da_vez:
            raise ValueError('Não é a vez deste jogador')
        carta = jogador.jogar(indice_carta)
        self.jogadas.append(Jogada(jogador, carta))
        self._indice_turno = (self._indice_turno + 1) % len(self._ordem)
        if len(self.jogadas) != len(self._ordem):
            return None
        return self._fechar_vaza()

    def _fechar_vaza(self) -> ResultadoVaza:
        maior = max(j.carta.forca for j in self.jogadas)
        melhores = [j for j in self.jogadas if j.carta.forca == maior]
        equipes = {self.indice_equipe(j.jogador) for j in melhores}
        vencedor = next(iter(equipes)) if len(equipes) == 1 else None
        resultado = ResultadoVaza(len(self.resultados) + 1, vencedor, tuple(self.jogadas))
        self.resultados.append(resultado)
        self.jogadas.clear()
        ganhador_mao = self._ganhador_mao()
        if ganhador_mao is not None:
            self._concluir_mao(ganhador_mao)
        else:
            if vencedor is not None:
                self._indice_turno = self._ordem.index(melhores[0].jogador)
            # Em empate, a próxima vaza começa com quem iniciou a anterior.
            else:
                self._indice_turno = self._ordem.index(resultado.jogadas[0].jogador)
        return resultado

    def _ganhador_mao(self) -> int | None:
        r = [v.vencedor for v in self.resultados]
        if len(r) == 1:
            return None
        if r[0] is not None:
            if r[1] == r[0] or r[1] is None:
                return r[0]
            if len(r) == 3:
                return r[2] if r[2] is not None else r[0]
            return None
        if r[1] is not None:
            return r[1]
        if len(r) == 3:
            return r[2] if r[2] is not None else self.indice_equipe(self._ordem[self._indice_mao])
        return None

    def pedir_aumento(self, jogador: Jogador) -> int:
        if self.estado != Estado.JOGANDO:
            raise ValueError('Não é possível pedir aumento agora')
        if jogador is not self.jogador_da_vez:
            raise ValueError("Somente o jogador da vez pode pedir aumento")
        equipe = self.indice_equipe(jogador)
        if self._mao_onze is not None:
            raise ValueError('Não se pode pedir truco na mão de onze')
        if self.valor_mao == 12:
            raise ValueError('A mão já vale 12 pontos')
        if self._ultimo_aumentou == equipe:
            raise ValueError('Somente a equipe adversária pode aumentar novamente')
        novo = {1: 3, 3: 6, 6: 9, 9: 12}[self.valor_mao]
        self._pedido = (equipe, novo)
        self.estado = Estado.PEDIDO_PENDENTE
        return novo

    def responder_aumento(self, jogador: Jogador, aceitar: bool) -> None:
        if self.estado != Estado.PEDIDO_PENDENTE or self._pedido is None:
            raise ValueError('Não há pedido pendente')
        solicitante, novo_valor = self._pedido
        if self.indice_equipe(jogador) == solicitante:
            raise ValueError('A própria equipe não pode responder ao pedido')
        self._pedido = None
        if aceitar:
            self.valor_mao = novo_valor
            self._ultimo_aumentou = solicitante
            self.estado = Estado.JOGANDO
        else:
            self._concluir_mao(solicitante)

    def aumentar_aposta_pendente(self, jogador: Jogador) -> int:
        """Contra-aumenta uma aposta pendente (ex.: truco -> seis)."""
        if self.estado != Estado.PEDIDO_PENDENTE or self._pedido is None:
            raise ValueError('Não há pedido pendente')
        solicitante, valor_proposto = self._pedido
        equipe = self.indice_equipe(jogador)
        if equipe == solicitante:
            raise ValueError('Somente a equipe adversária pode aumentar')
        if valor_proposto == 12:
            raise ValueError('A aposta já atingiu 12 pontos')
        proximo = {3: 6, 6: 9, 9: 12}.get(valor_proposto)
        if proximo is None:
            raise ValueError('Não existe próximo valor de aposta')
        self._pedido = (equipe, proximo)
        self._indice_turno = self._ordem.index(jogador)
        return proximo

    def decidir_mao_onze(self, jogador: Jogador, jogar: bool) -> None:
        if self.estado != Estado.JOGANDO or self._mao_onze is None:
            raise ValueError('Não existe decisão de mão de onze pendente')
        if self.resultados or self.jogadas:
            raise ValueError('A decisão deve acontecer antes da primeira jogada')
        if self.indice_equipe(jogador) != self._mao_onze:
            raise ValueError('Somente a equipe com onze pontos decide')
        equipe = self._mao_onze
        self._mao_onze = None
        if jogar:
            self.valor_mao = 3
        else:
            self._concluir_mao(1 - equipe)

    def _concluir_mao(self, equipe: int) -> None:
        self.pontos[equipe] += self.valor_mao
        self._pedido = None
        self._mao_onze = None
        if self.pontos[equipe] >= 12:
            self.vencedor = equipe
            self.estado = Estado.ENCERRADA
        else:
            self.estado = Estado.AGUARDANDO

    @classmethod
    def individual(cls, j1: Jogador, j2: Jogador, *, limpo: bool = True) -> 'Partida':
        return cls(Equipe(j1), Equipe(j2), limpo=limpo)

    @classmethod
    def duplas(cls, j1: Jogador, j2: Jogador, j3: Jogador, j4: Jogador, *, limpo: bool = True) -> 'Partida':
        return cls(Equipe(j1, j2), Equipe(j3, j4), limpo=limpo)

    @classmethod
    def trios(cls, *jogadores: Jogador) -> 'Partida':
        if len(jogadores) != 6:
            raise ValueError('Trios exigem exatamente seis jogadores')
        return cls(Equipe(*jogadores[:3]), Equipe(*jogadores[3:]), limpo=False)
