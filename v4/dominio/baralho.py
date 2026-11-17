"""Baralho: criação, embaralhamento e distribuição de cartas."""

import random
from dominio.carta import Carta
from dominio.naipe import Naipe
from dominio.rank import Rank


class Baralho:
    """Gerencia o baralho: cria cartas, embaralha e distribui mãos.

    Recria as cartas a cada distribuição para permitir múltiplas mãos.
    """

    def __init__(self, limpo: bool = True) -> None:
        self._limpo = limpo

    @property
    def limpo(self) -> bool:
        return self._limpo

    def _criar_cartas(self) -> list[Carta]:
        """Cria um novo conjunto de cartas."""
        return [
            Carta(rank, naipe)
            for rank in Rank.valores(self._limpo)
            for naipe in Naipe
        ]

    def definir_manilha(self, vira: Carta, todas_cartas: list[Carta]) -> None:
        """Define as manilhas com base na carta virada.

        A manilha é o rank seguinte ao da carta virada, ciclicamente.
        """
        ranks = Rank.valores(self._limpo)
        rank_manilha = ranks[(ranks.index(vira.rank) + 1) % len(ranks)]
        for carta in todas_cartas:
            if carta.rank == rank_manilha:
                carta.tornar_manilha()

    def distribuir(self, jogadores_por_equipe: int = 1) -> tuple[list[list[Carta]], Carta]:
        """Embaralha e distribui 3 cartas para cada jogador.

        Retorna:
            - Lista de mãos (uma por jogador)
            - Carta virada
        """
        if not 1 <= jogadores_por_equipe <= 3:
            raise ValueError('Jogadores por equipe deve ser 1, 2 ou 3')
        if jogadores_por_equipe == 3 and self._limpo:
            raise ValueError('Trios exigem baralho sujo')

        # Recria cartas a cada distribuição
        cartas = self._criar_cartas()
        for carta in cartas:
            carta.tornar_comum()
        random.shuffle(cartas)

        total_jogadores = jogadores_por_equipe * 2
        maos: list[list[Carta]] = []
        for _ in range(total_jogadores):
            mao = [cartas.pop() for _ in range(3)]
            maos.append(mao)
        vira = cartas.pop()
        # Define manilha em TODAS as cartas (mãos + vira + resto)
        todas = [c for m in maos for c in m] + [vira] + cartas
        self.definir_manilha(vira, todas)
        return maos, vira
