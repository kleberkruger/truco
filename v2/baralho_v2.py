from enum import StrEnum
from dataclasses import dataclass
from typing import Protocol, TypeVar, Any
import random


class Rank(StrEnum):
    AS = 'A'
    DOIS = '2'
    TRES = '3'
    QUATRO = '4'
    CINCO = '5'
    SEIS = '6'
    SETE = '7'
    OITO = '8'
    NOVE = '9'
    DEZ = '10'
    DAMA = 'Q'
    VALETE = 'J'
    REI = 'K'
    CORINGA = 'Joker'

    def __repr__(self) -> str:
        return self.value


class Naipe(StrEnum):
    OUROS = '♦'
    ESPADAS = '♠'
    COPAS = '♥'
    PAUS = '♣'

    def __repr__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Carta:
    rank: Rank
    naipe: Naipe

    @property
    def coringa(self) -> bool:
        return self.rank == Rank.CORINGA

    @property
    def nome(self) -> str:
        return f"{self.rank} de {self.naipe}"

    def __repr__(self) -> str:
        return f"[{self.rank}{self.naipe}]"


T_Contexto = TypeVar('T_Contexto')


class RegulamentoJogo(Protocol):

    def baralho(self) -> list[Carta]: ...

    def calcular_forca(self, carta: Carta, contexto: T_Contexto = None) -> int: ...

    def comparar(self, carta1: Carta, carta2: Carta, contexto: T_Contexto = None) -> int: ...

    def validar_jogada(self, carta: Carta, mao_jogador: list[Carta], contexto: T_Contexto = None) -> bool: ...

    def avaliar_mao(self, cartas: list[Carta], contexto: T_Contexto = None) -> tuple[int, Any]: ...


class RegraTruco:

    def __init__(self, limpo: bool = True):
        self._limpo = limpo
        self._ordem_forca = [
            Rank.QUATRO, Rank.CINCO, Rank.SEIS, Rank.SETE,
            Rank.DAMA, Rank.VALETE, Rank.REI, Rank.AS, Rank.DOIS, Rank.TRES
        ]
        if self._limpo:
            self._ordem_forca = self._ordem_forca[4:]

    def criar_cartas(self) -> list[Carta]:
        return [Carta(rank, naipe) for rank in self._ordem_forca for naipe in Naipe]

    def calcular_forca(self, carta: Carta, contexto: Carta = None) -> int:
        try:
            forca_base = (self._ordem_forca.index(carta.rank) + 1) * 10
        except ValueError:
            return 0

        if contexto is None:
            return forca_base

        idx_vira = self._ordem_forca.index(contexto.rank)
        rank_manilha = self._ordem_forca[(idx_vira + 1) % len(self._ordem_forca)]

        if carta.rank == rank_manilha:
            naipes_forca = {Naipe.OUROS: 1, Naipe.ESPADAS: 2, Naipe.COPAS: 3, Naipe.PAUS: 4}
            return 100 + naipes_forca.get(carta.naipe, 0)

        return forca_base

    def comparar(self, carta1: Carta, carta2: Carta, contexto: Carta) -> int:
        f1 = self.calcular_forca(carta1, contexto)
        f2 = self.calcular_forca(carta2, contexto)
        return (f1 > f2) - (f1 < f2)


class Baralho:

    def __init__(self, jogo: RegulamentoJogo):
        self.jogo = jogo
        self.cartas: list[Carta] = jogo.baralho()
        self.embaralhar()

    def __repr__(self) -> str:
        return f"Baralho({len(self.cartas)} cartas restantes)"

    def __len__(self) -> int:
        return len(self.cartas)

    def cartas(self) -> list[Carta]:
        return self.cartas

    def embaralhar(self) -> None:
        random.shuffle(self.cartas)

    def distribuir(self, quantidade: int) -> list[Carta]:
        if quantidade > len(self.cartas):
            raise ValueError("Cartas insuficientes no baralho.")
        return [self.cartas.pop() for _ in range(quantidade)]

    def puxar_carta(self) -> Carta:
        if not self.cartas:
            raise ValueError("O baralho está vazio.")
        return self.cartas.pop()

    def comparar_cartas(self, carta1: Carta, carta2: Carta, contexto: Any = None) -> int:
        return self.jogo.comparar(carta1, carta2, contexto)


print(list(Rank))
print(Rank.DOIS)
print(list(Naipe))
print(Naipe.ESPADAS)
print(Carta(Rank.DOIS, Naipe.ESPADAS))
print(repr(Carta(Rank.DOIS, Naipe.ESPADAS)))
