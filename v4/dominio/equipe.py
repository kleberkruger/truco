"""Equipe: grupo de jogadores que disputam juntos."""

from dominio.jogador import Jogador


class Equipe:
    """Agrupa 1 a 3 jogadores em uma equipe imutável."""

    def __init__(self, *jogadores: Jogador) -> None:
        if not 1 <= len(jogadores) <= 3:
            raise ValueError('Uma equipe deve ter de 1 a 3 jogadores')
        ids = {j.id for j in jogadores}
        if len(ids) != len(jogadores):
            raise ValueError('Jogador duplicado na equipe')
        self._jogadores = tuple(jogadores)

    @property
    def jogadores(self) -> tuple[Jogador, ...]:
        return self._jogadores

    def __len__(self) -> int:
        return len(self._jogadores)

    def __str__(self) -> str:
        return ' / '.join(j.nome for j in self._jogadores)

    def __repr__(self) -> str:
        return f'Equipe({", ".join(j.nome for j in self._jogadores)})'
