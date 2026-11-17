"""Valores das cartas do baralho."""

from enum import StrEnum


class Rank(StrEnum):
    """Valores das cartas, ordenados do mais fraco ao mais forte.

    Baralho limpo: A, 2, 3, 4, 5, 6, 7, Q, J, K (10 valores).
    Baralho sujo: 4, 5, 6, 7, Q, J, K, A, 2, 3 (13 valores).
    """
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
    def forca(self) -> int:
        """Retorna a força do rank (posição na lista, maior = mais forte)."""
        return list(Rank).index(self)

    @classmethod
    def valores_limpo(cls) -> list['Rank']:
        """Retorna os ranks do baralho limpo (sem 4, 5, 6, 7)."""
        removidos = {cls.QUATRO, cls.CINCO, cls.SEIS, cls.SETE}
        return [r for r in cls if r not in removidos]

    @classmethod
    def valores_sujo(cls) -> list['Rank']:
        """Retorna todos os ranks do baralho sujo."""
        return list(cls)

    @classmethod
    def valores(cls, limpo: bool = True) -> list['Rank']:
        """Retorna os ranks conforme o tipo de baralho."""
        return cls.valores_limpo() if limpo else cls.valores_sujo()

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)
