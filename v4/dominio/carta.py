"""Carta individual do baralho."""

from dominio.naipe import Naipe
from dominio.rank import Rank


class Carta:
    """Representa uma carta do baralho com rank, naipe e estado de manilha."""

    __slots__ = ('_rank', '_naipe', '_manilha')

    def __init__(self, rank: Rank, naipe: Naipe) -> None:
        self._rank = rank
        self._naipe = naipe
        self._manilha = False

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
    def forca(self) -> int:
        """Calcula a força da carta.

        Manilhas são sempre mais fortes que cartas normais.
        Entre manilhas, a força depende do naipe.
        Entre cartas normais, a força depende do rank.
        """
        if self._manilha:
            return len(Rank) * 10 + self._naipe.forca
        return self._rank.forca * 10

    @property
    def nome(self) -> str:
        return f'{self._rank} de {self._naipe}'

    def tornar_manilha(self) -> None:
        self._manilha = True

    def tornar_comum(self) -> None:
        self._manilha = False

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Carta):
            return NotImplemented
        return self.forca < other.forca

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Carta):
            return NotImplemented
        return self._rank == other._rank and self._naipe == other._naipe

    def __hash__(self) -> int:
        return hash((self._rank, self._naipe))

    def __str__(self) -> str:
        return f'[{self._rank} {self._naipe}]'

    def __repr__(self) -> str:
        return str(self)
