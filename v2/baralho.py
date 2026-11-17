from enum import StrEnum
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
    CORINGA = 'JOKER'

    @classmethod
    def baralho_sujo(cls) -> list['Rank']:
        return [
            cls.QUATRO, cls.CINCO, cls.SEIS, cls.SETE,
            cls.DAMA, cls.VALETE, cls.REI, cls.AS, cls.DOIS, cls.TRES
        ]

    @classmethod
    def baralho_limpo(cls) -> list['Rank']:
        return [
            cls.DAMA, cls.VALETE, cls.REI, cls.AS, cls.DOIS, cls.TRES
        ]

    @classmethod
    def baralho(cls, limpo=True) -> list['Rank']:
        return cls.baralho_limpo() if limpo else cls.baralho_sujo()

    def forca_baralho(self) -> int:
        match self:
            case Rank.QUATRO:  return 1
            case Rank.CINCO:   return 2
            case Rank.SEIS:    return 3
            case Rank.SETE:    return 4
            case Rank.DAMA:    return 5
            case Rank.VALETE:  return 6
            case Rank.REI:     return 7
            case Rank.AS:      return 8
            case Rank.DOIS:    return 9
            case Rank.TRES:    return 10
            case _:            return 0

    def __repr__(self) -> str:
        return self.value


class Naipe(StrEnum):
    OUROS = '♦'
    ESPADAS = '♠'
    COPAS = '♥'
    PAUS = '♣'

    def forca_baralho(self) -> int:
        match self:
            case Naipe.OUROS:   return 1
            case Naipe.ESPADAS: return 2
            case Naipe.COPAS:   return 3
            case Naipe.PAUS:    return 4

    def __repr__(self):
        return self.value


class Carta:

    def __init__(self, rank: Rank, naipe: Naipe):
        self._rank = rank
        self._naipe = naipe

    @property
    def rank(self) -> Rank:
        return self._rank

    @property
    def naipe(self) -> Naipe:
        return self._naipe

    @property
    def coringa(self) -> bool:
        return self._rank == Rank.CORINGA

    @property
    def nome(self) -> str:
        return f"{self._rank} de {self._naipe}"

    def __lt__(self, other: object):
        if not isinstance(other, Carta):
            return NotImplemented
        return self.forca < other.forca

    def __eq__(self, other: object):
        if not isinstance(other, Carta):
            return NotImplemented
        return self._rank == other._rank and self._naipe == other._naipe

    def __repr__(self):
        return f'[{self._rank} {self._naipe}]'


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


print(Rank.baralho(True))
print(Rank.DOIS)
print(list(Naipe))
print(Naipe.ESPADAS)

