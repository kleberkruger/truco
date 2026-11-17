"""Naipes das cartas do baralho."""

from enum import StrEnum


class Naipe(StrEnum):
    """Naipes do baralho, ordenados por força para desempate de manilhas."""
    OUROS = '♦'
    ESPADAS = '♠'
    COPAS = '♥'
    PAUS = '♣'

    @property
    def forca(self) -> int:
        """Retorna a força do naipe (usado para desempate de manilhas)."""
        return list(Naipe).index(self)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)
