"""Jogador: participante individual do jogo."""

import enum
from uuid import UUID, uuid4
from dominio.carta import Carta


class Sexo(enum.StrEnum):
    """Sexo gramatical do jogador para concordância de termos como parceiro/parceira."""
    MASCULINO = 'M'
    FEMININO = 'F'


class Jogador:
    """Representa um jogador com nome, ID único e mão de cartas."""

    def __init__(self, nome: str, sexo: Sexo = Sexo.MASCULINO) -> None:
        nome = nome.strip()
        if not nome:
            raise ValueError('O nome do jogador não pode ser vazio')
        self._nome = nome
        self._sexo = sexo
        self._id = uuid4()
        self._cartas: list[Carta] = []

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def sexo(self) -> Sexo:
        return self._sexo

    @property
    def id(self) -> UUID:
        return self._id

    def nome_parceiro(self) -> str:
        """Retorna 'Parceiro' ou 'Parceira' conforme o sexo do jogador."""
        return 'Parceira' if self._sexo == Sexo.FEMININO else 'Parceiro'

    @property
    def cartas(self) -> tuple[Carta, ...]:
        """Retorna as cartas da mão como tupla imutável."""
        return tuple(self._cartas)

    def receber_cartas(self, cartas: list[Carta]) -> None:
        """Recebe exatamente 3 cartas para a mão, ordenadas por força crescente."""
        if len(cartas) != 3:
            raise ValueError('Cada jogador deve receber exatamente três cartas')
        self._cartas = sorted(cartas, key=lambda c: c.forca)

    def jogar(self, indice: int) -> Carta:
        """Joga a carta no índice especificado e a remove da mão."""
        if not 0 <= indice < len(self._cartas):
            raise ValueError('Índice de carta inválido')
        return self._cartas.pop(indice)

    def __str__(self) -> str:
        return self._nome

    def __repr__(self) -> str:
        return f'Jogador({self._nome!r})'
