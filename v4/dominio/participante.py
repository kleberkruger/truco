from dataclasses import dataclass, field
from uuid import UUID, uuid4

from dominio.baralho import Carta


@dataclass(eq=False, slots=True)
class Jogador:
    nome: str
    id: UUID = field(default_factory=uuid4, init=False)
    _cartas: list[Carta] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError('O nome do jogador não pode ser vazio')

    @property
    def cartas(self) -> tuple[Carta, ...]:
        return tuple(self._cartas)

    def receber_cartas(self, cartas: list[Carta]) -> None:
        if len(cartas) != 3:
            raise ValueError('Cada jogador deve receber exatamente três cartas')
        self._cartas = list(cartas)

    def jogar(self, indice: int) -> Carta:
        if not 0 <= indice < len(self._cartas):
            raise ValueError('Índice de carta inválido')
        return self._cartas.pop(indice)

    def __str__(self) -> str:
        return self.nome


@dataclass(frozen=True, slots=True, init=False)
class Equipe:
    jogadores: tuple[Jogador, ...]

    def __init__(self, *jogadores: Jogador):
        if not 1 <= len(jogadores) <= 3:
            raise ValueError('A equipe deve ter de um a três jogadores')
        if not all(isinstance(j, Jogador) for j in jogadores):
            raise TypeError('Todos os integrantes devem ser Jogador')
        if len({j.id for j in jogadores}) != len(jogadores):
            raise ValueError('Jogador duplicado na equipe')
        object.__setattr__(self, 'jogadores', tuple(jogadores))

    def __len__(self) -> int:
        return len(self.jogadores)

    def __str__(self) -> str:
        return ' / '.join(j.nome for j in self.jogadores)
