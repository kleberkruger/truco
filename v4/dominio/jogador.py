"""Jogador: participante individual do jogo."""

from uuid import UUID, uuid4
from dominio.carta import Carta


class Jogador:
    """Representa um jogador com nome, ID único e mão de cartas."""

    def __init__(self, nome: str) -> None:
        nome = nome.strip()
        if not nome:
            raise ValueError('O nome do jogador não pode ser vazio')
        self._nome = nome
        self._id = uuid4()
        self._cartas: list[Carta] = []

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def cartas(self) -> tuple[Carta, ...]:
        """Retorna as cartas da mão como tupla imutável."""
        return tuple(self._cartas)

    def receber_cartas(self, cartas: list[Carta]) -> None:
        """Recebe exatamente 3 cartas para a mão."""
        if len(cartas) != 3:
            raise ValueError('Cada jogador deve receber exatamente três cartas')
        self._cartas = list(cartas)

    def jogar(self, indice: int) -> Carta:
        """Joga a carta no índice especificado e a remove da mão."""
        if not 0 <= indice < len(self._cartas):
            raise ValueError('Índice de carta inválido')
        return self._cartas.pop(indice)

    def __str__(self) -> str:
        return self._nome

    def __repr__(self) -> str:
        return f'Jogador({self._nome!r})'
