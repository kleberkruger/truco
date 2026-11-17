"""Inteligência Artificial com níveis de dificuldade.

A IA decide:
1. Qual carta jogar (estratégia de carta)
2. Se deve pedir truco (estratégia de aposta)
3. Se deve aceitar/correr de um truco (estratégia de resposta)

Os níveis de dificuldade ajustam a qualidade das decisões.
"""

import enum
import random
from enum import auto

from dominio.carta import Carta
from dominio.jogador import Jogador


class Dificuldade(enum.IntEnum):
    """Níveis de dificuldade da IA."""
    FACIL = 1
    MEDIO = 2
    DIFICIL = 3


class EstrategiaCarta:
    """Decide qual carta a IA deve jogar."""

    def __init__(self, dificuldade: Dificuldade = Dificuldade.MEDIO, rng: random.Random | None = None) -> None:
        self._dificuldade = dificuldade
        self._rng = rng or random.Random()

    def escolher_carta(
        self,
        jogador: Jogador,
        cartas_na_mesa: list[Carta],
        rodadas_vencidas: int,
        total_rodadas: int,
    ) -> int:
        """Escolhe o índice da carta a jogar.

        Args:
            jogador: Jogador da IA.
            cartas_na_mesa: Cartas já jogadas nesta vaza.
            rodadas_vencidas: Vazas vencidas pela equipe da IA nesta mão.
            total_rodadas: Total de vazas jogadas nesta mão.

        Returns:
            Índice da carta a jogar.
        """
        cartas = jogador.cartas
        if not cartas:
            raise ValueError('Jogador não tem cartas')
        if len(cartas) == 1:
            return 0

        # Força da mão restante
        forca_mao = self._forca_mao(cartas)

        if cartas_na_mesa:
            maior_mesa = max(c.forca for c in cartas_na_mesa)
            return self._responder_mao(cartas, maior_mesa, forca_mao)
        else:
            return self._primeira_carta(cartas, forca_mao)

    def _forca_mao(self, cartas: tuple[Carta, ...]) -> float:
        """Calcula a força relativa da mão (0.0 a 1.0)."""
        if not cartas:
            return 0.0
        forcas = [c.forca for c in cartas]
        # Normaliza pela força máxima possível (manilha de paus)
        max_forca = len(type(cartas[0]).__mro__) * 100 if forcas else 1
        return sum(f / 100 for f in forcas) / len(cartas)

    def _primeira_carta(self, cartas: tuple[Carta, ...], forca_mao: float) -> int:
        """Escolhe a primeira carta a jogar (sem cartas na mesa)."""
        if self._dificuldade == Dificuldade.FACIL:
            # Joga aleatório
            return self._rng.randrange(len(cartas))

        if self._dificuldade == Dificuldade.DIFICIL:
            # Se mão forte, joga fraca para economizar
            if forca_mao > 0.6:
                return min(range(len(cartas)), key=lambda i: cartas[i].forca)
            # Se mão fraca, joga forte para tentar ganhar
            return max(range(len(cartas)), key=lambda i: cartas[i].forca)

        # Médio: prefere jogar carta mais fraca 55% do tempo
        if self._rng.random() < 0.55:
            return min(range(len(cartas)), key=lambda i: cartas[i].forca)
        return self._rng.randrange(len(cartas))

    def _responder_mao(
        self,
        cartas: tuple[Carta, ...],
        maior_mesa: int,
        forca_mao: float,
    ) -> int:
        """Escolhe carta para responder às cartas na mesa."""
        # Cartas que batem a maior da mesa
        batem = [i for i, c in enumerate(cartas) if c.forca > maior_mesa]

        if not batem:
            # Não tem carta que bata, joga a mais fraca
            return min(range(len(cartas)), key=lambda i: cartas[i].forca)

        if self._dificuldade == Dificuldade.FACIL:
            # Tenta bater aleatoriamente
            if self._rng.random() < 0.5:
                return self._rng.choice(batem)
            return min(range(len(cartas)), key=lambda i: cartas[i].forca)

        if self._dificuldade == Dificuldade.DIFICIL:
            # Usa a carta mínima que bate (economiza)
            return min(batem, key=lambda i: cartas[i].forca)

        # Médio: 70% usa mínima que bate, 30% joga aleatório
        if self._rng.random() < 0.7:
            return min(batem, key=lambda i: cartas[i].forca)
        return self._rng.choice(batem)


class EstrategiaAposta:
    """Decide se a IA deve pedir/aceitar truco."""

    def __init__(self, dificuldade: Dificuldade = Dificuldade.MEDIO, rng: random.Random | None = None) -> None:
        self._dificuldade = dificuldade
        self._rng = rng or random.Random()

    def deve_pedir_truco(
        self,
        forca_mao: float,
        rodadas_vencidas: int,
        total_rodadas: int,
        valor_atual: int,
    ) -> bool:
        """Decide se deve pedir truco."""
        if valor_atual >= 12:
            return False

        vantagem = rodadas_vencidas - (total_rodadas - rodadas_vencidas)

        if self._dificuldade == Dificuldade.FACIL:
            # Blefa frequentemente
            return self._rng.random() < 0.3

        if self._dificuldade == Dificuldade.DIFICIL:
            # Só pede com mão forte e vantagem
            return forca_mao > 0.7 and vantagem >= 0

        # Médio: pede com mão razoável
        probabilidade = forca_mao + vantagem * 0.1
        return self._rng.random() < probabilidade

    def deve_aceitar_truco(
        self,
        forca_mao: float,
        valor_proposto: int,
    ) -> bool:
        """Decide se deve aceitar um truco pedido pelo adversário."""
        if self._dificuldade == Dificuldade.FACIL:
            # Aceita quase sempre
            return self._rng.random() < 0.85

        if self._dificuldade == Dificuldade.DIFICIL:
            # Só aceita com mão forte ou valor baixo
            if valor_proposto <= 6:
                return forca_mao > 0.4
            return forca_mao > 0.7

        # Médio
        if valor_proposto <= 6:
            return self._rng.random() < 0.82
        return self._rng.random() < 0.64


class IA:
    """Inteligência Artificial completa para o jogo.

    Combina estratégia de carta e estratégia de aposta.
    """

    def __init__(self, dificuldade: Dificuldade = Dificuldade.MEDIO, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._carta = EstrategiaCarta(dificuldade, self._rng)
        self._aposta = EstrategiaAposta(dificuldade, self._rng)
        self._dificuldade = dificuldade

    @property
    def dificuldade(self) -> Dificuldade:
        return self._dificuldade

    def escolher_carta(
        self,
        jogador: Jogador,
        cartas_na_mesa: list[Carta],
        rodadas_vencidas: int,
        total_rodadas: int,
    ) -> int:
        return self._carta.escolher_carta(
            jogador, cartas_na_mesa, rodadas_vencidas, total_rodadas
        )

    def forca_mao(self, cartas: tuple[Carta, ...]) -> float:
        """Calcula a força da mão para decisões de aposta."""
        return self._carta._forca_mao(cartas)

    def deve_pedir_truco(
        self,
        forca_mao: float,
        rodadas_vencidas: int,
        total_rodadas: int,
        valor_atual: int,
    ) -> bool:
        return self._aposta.deve_pedir_truco(
            forca_mao, rodadas_vencidas, total_rodadas, valor_atual
        )

    def deve_aceitar_truco(
        self,
        forca_mao: float,
        valor_proposto: int,
    ) -> bool:
        return self._aposta.deve_aceitar_truco(forca_mao, valor_proposto)
