from enum import StrEnum
import random


class Rank(StrEnum):
    QUATRO = '4'
    CINCO = '5'
    SEIS = '6'
    SETE = '7'
    DAMA = 'Q'
    VALETE = 'J'
    REI = 'K'
    AS = 'A'
    DOIS = '2'
    TRES = '3'

    @property
    def forca(self):
        return list(Rank).index(self)

    @classmethod
    def baralho_sujo(cls) -> list['Rank']:
        return list(cls)

    @classmethod
    def baralho_limpo(cls) -> list['Rank']:
        removidos = {cls.QUATRO, cls.CINCO, cls.SEIS, cls.SETE}
        return [rank for rank in cls if rank not in removidos]

    @classmethod
    def baralho(cls, limpo=True) -> list['Rank']:
        return cls.baralho_limpo() if limpo else cls.baralho_sujo()

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class Naipe(StrEnum):
    OUROS = '♦'
    ESPADAS = '♠'
    COPAS = '♥'
    PAUS = '♣'

    @property
    def forca(self):
        return list(Naipe).index(self)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class Carta:

    def __init__(self, rank: Rank, naipe: Naipe):
        self._rank = rank
        self._naipe = naipe
        self._manilha = False

    def tornar_comum(self):
        self._manilha = False

    def tornar_manilha(self):
        self._manilha = True

    @property
    def rank(self) -> Rank:
        return self._rank

    @property
    def naipe(self) -> Naipe:
        return self._naipe

    @property
    def manilha(self) -> bool:
        return self._manilha

    @property
    def nome(self) -> str:
        return f"{self._rank} de {self._naipe}"

    @property
    def forca(self) -> int:
        if self.manilha:
            return len(Rank) * 10 + self._naipe.forca
        return self._rank.forca * 10

    def __lt__(self, other: object):
        if not isinstance(other, Carta):
            return NotImplemented
        return self.forca < other.forca

    def __eq__(self, other: object):
        if not isinstance(other, Carta):
            return NotImplemented
        return self._rank == other._rank and self._naipe == other._naipe

    def __str__(self):
        return f"[{self._rank} {self._naipe}]"

    def __repr__(self):
        return str(self)


class Baralho:

    def __init__(self, limpo: bool = True):
        self._limpo = limpo
        self._cartas = {
            rank: [Carta(rank, naipe) for naipe in Naipe]
            for rank in Rank.baralho(limpo)
        }

    @property
    def limpo(self) -> bool:
        return self._limpo

    @property
    def cartas(self) -> list[Carta]:
        return [c for lista in self._cartas.values() for c in lista]

    def embaralhar(self) -> list[Carta]:
        cartas = self.cartas
        for carta in cartas:
            carta.tornar_comum()
        random.shuffle(cartas)
        return cartas

    def distribuir_cartas(self, jogadores_por_equipe: int = 1) -> tuple[list[list[Carta]], Carta]:
        if not 1 <= jogadores_por_equipe <= 3:
            raise ValueError("O número de jogadores por equipe deve ser entre 1 e 3")
        if jogadores_por_equipe == 3 and self.limpo:
            raise ValueError("O número máximo de jogadores por equipe no truco limpo é 2")

        cartas = self.embaralhar()
        maos = [
            [cartas.pop() for _ in range(3)]
            for _ in range(jogadores_por_equipe * 2)
        ]
        vira = cartas.pop()
        self.definir_manilha(vira)
        return maos, vira

    def definir_manilha(self, vira: Carta):
        ranks = Rank.baralho(self.limpo)
        for carta in self._cartas[ranks[(ranks.index(vira.rank) + 1) % len(ranks)]]:
            carta.tornar_manilha()
