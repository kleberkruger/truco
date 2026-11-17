"""Resultados de vaza e mão — dados imutáveis."""

from dataclasses import dataclass
from dominio.carta import Carta
from dominio.jogador import Jogador


@dataclass(frozen=True, slots=True)
class Jogada:
    """Registro de uma carta jogada por um jogador."""
    jogador: Jogador
    carta: Carta

    def __str__(self) -> str:
        return f'{self.jogador.nome} jogou {self.carta}'


@dataclass(frozen=True, slots=True)
class ResultadoVaza:
    """Resultado de uma vaza (rodada de cartas).

    Args:
        numero: Número sequencial da vaza (1, 2, 3).
        equipe_vencedora: Índice da equipe vencedora (0 ou 1), None = empate.
        jogadas: Todas as jogadas desta vaza.
    """
    numero: int
    equipe_vencedora: int | None
    jogadas: tuple[Jogada, ...]

    @property
    def eh_empate(self) -> bool:
        return self.equipe_vencedora is None

    def __str__(self) -> str:
        if self.equipe_vencedora is None:
            return f'Vaza {self.numero}: empate'
        return f'Vaza {self.numero}: equipe {self.equipe_vencedora + 1} venceu'
