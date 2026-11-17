from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Protocol


class Dificuldade(StrEnum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class Acao(Protocol):
    """Protocolo que descreve uma ação retornada pelo método `jogar`."""

    @property
    def tipo(self) -> str:
        ...


class JogadaCarta:
    """Ação de jogar uma carta na mesa."""

    def __init__(self, carta: 'Carta'):
        self._carta = carta

    @property
    def tipo(self) -> str:
        return "carta"

    @property
    def carta(self) -> 'Carta':
        return self._carta


class JogadaTruco:
    """Ação de pedir truco / seis / nove / doze."""

    def __init__(self, pontuacao_alvo: int):
        """
        :param pontuacao_alvo: 3 para truco, 6 para seis, 9 para nove, 12 para doze.
        """
        if pontuacao_alvo not in (3, 6, 9, 12):
            raise ValueError("pontuacao_alvo deve ser 3, 6, 9 ou 12")
        self._pontuacao_alvo = pontuacao_alvo

    @property
    def tipo(self) -> str:
        return "truco"

    @property
    def pontuacao_alvo(self) -> int:
        return self._pontuacao_alvo


class JogadaCorrer:
    """Ação de correr (desistir da mão)."""

    @property
    def tipo(self) -> str:
        return "correr"


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class Jogador(ABC):
    """Classe abstrata base para qualquer jogador do Truco.

    Subclasses concretas devem implementar ``jogar`` para decidir qual carta
    jogar (ou qual ação tomar) e ``decidir_proposta`` para responder a
    propostas de truco.
    """

    def __init__(self, nome: str):
        self._nome: str = nome
        self._cartas: list['Carta'] = []
        self._vira: 'Carta | None' = None

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cartas(self) -> list['Carta']:
        """Retorna as cartas atualmente na mão do jogador (backend-only)."""
        return self._cartas

    @property
    def vira(self) -> 'Carta | None':
        return self._vira

    def iniciar_mao(self, cartas: list['Carta'], vira: 'Carta'):
        """Distribui as cartas do jogador e a carta virada no início de uma mão."""
        self._cartas = cartas
        self._vira = vira
        self._on_mao_iniciada(cartas, vira)

    @abstractmethod
    def _on_mao_iniciada(self, cartas: list['Carta'], vira: 'Carta') -> None:
        """Callback chamado quando as cartas são distribuídas.

        Subclasses de frontend podem sobrescrever para exibir as cartas ao
        usuário humano, enquanto a IA simplesmente as armazena.
        """
        ...

    @abstractmethod
    def jogar(
        self, rodada: int, vencidas: int, maior_carta: 'Carta | None'
    ) -> JogadaCarta:
        """Retorna a carta que o jogador deseja jogar nesta rodada."""
        ...

    @abstractmethod
    def decidir_proposta(
        self, pontuacao_atual: int, pontuacao_proposta: int
    ) -> JogadaTruco | JogadaCorrer:
        """Decide se aceita (e eventualmente contra oferece) ou corre de uma proposta."""
        ...

    def __repr__(self):
        return self._nome


# ---------------------------------------------------------------------------
# Concrete: Human player (backend only — frontend via terminal)
# ---------------------------------------------------------------------------

class JogadorHumano(Jogador):
    """Jogador controlado por um humano.

    A lógica de interação com o terminal fica em ``JogadorHumanoTerminal``
    (arquivo separado). Esta classe expõe apenas a interface backend.
    """

    def __init__(self, nome: str, frontend: 'JogadorHumanoFrontend'):
        super().__init__(nome)
        self._frontend = frontend

    def _on_mao_iniciada(self, cartas: list['Carta'], vira: 'Carta') -> None:
        self._frontend.mostrar_mao(cartas, vira)

    def jogar(
        self, rodada: int, vencidas: int, maior_carta: 'Carta | None'
    ) -> JogadaCarta:
        carta = self._frontend.escolher_carta(
            self._cartas, rodada, vencidas, maior_carta, self._vira
        )
        idx = self._cartas.index(carta)
        self._cartas.pop(idx)
        return JogadaCarta(carta)

    def decidir_proposta(
        self, pontuacao_atual: int, pontuacao_proposta: int
    ) -> JogadaTruco | JogadaCorrer:
        return self._frontend.decisao_proposta(pontuacao_atual, pontuacao_proposta)


# ---------------------------------------------------------------------------
# Concrete: AI player (backend — difficulty-driven strategy)
# ---------------------------------------------------------------------------

class JogadorIA(Jogador):
    """Jogador controlado por inteligência artificial.

    :param nome: Nome exibido do jogador.
    :param dificuldade: Nível de dificuldade da IA
        (``Dificuldade.FACIL``, ``MEDIO`` ou ``DIFICIL``).
    """

    def __init__(self, nome: str, dificuldade: Dificuldade = Dificuldade.FACIL):
        super().__init__(nome)
        self._dificuldade = dificuldade

    @property
    def dificuldade(self) -> Dificuldade:
        return self._dificuldade

    def _on_mao_iniciada(self, cartas: list['Carta'], vira: 'Carta') -> None:
        pass  # IA não precisa de feedback visual

    def jogar(
        self, rodada: int, vencidas: int, maior_carta: 'Carta | None'
    ) -> JogadaCarta:
        carta = self._escolher_carta(maior_carta)
        idx = self._cartas.index(carta)
        self._cartas.pop(idx)
        return JogadaCarta(carta)

    def decidir_proposta(
        self, pontuacao_atual: int, pontuacao_proposta: int
    ) -> JogadaTruco | JogadaCorrer:
        forca_mao = self._forca_relativa_mao()

        if self._dificuldade == Dificuldade.FACIL:
            return self._decidir_proposta_facil(
                pontuacao_atual, pontuacao_proposta, forca_mao
            )
        elif self._dificuldade == Dificuldade.MEDIO:
            return self._decidir_proposta_medio(
                pontuacao_atual, pontuacao_proposta, forca_mao
            )
        else:
            return self._decidir_proposta_dificil(
                pontuacao_atual, pontuacao_proposta, forca_mao
            )

    # -- Estratégia de escolha de carta -------------------------------------

    def _escolher_carta(self, maior_carta: 'Carta | None') -> 'Carta':
        if not self._cartas:
            raise RuntimeError("Nenhuma carta disponível para jogar")

        if self._dificuldade == Dificuldade.FACIL:
            return self._escolher_carta_facil(maior_carta)
        elif self._dificuldade == Dificuldade.MEDIO:
            return self._escolher_carta_medio(maior_carta)
        else:
            return self._escolher_carta_dificil(maior_carta)

    def _escolher_carta_facil(self, maior_carta: 'Carta | None') -> 'Carta':
        """Fácil: joga uma carta aleatória."""
        import random
        return random.choice(self._cartas)

    def _escolher_carta_medio(self, maior_carta: 'Carta | None') -> 'Carta':
        """Médio: tenta bater a maior carta da mesa; se não puder, joga a mais fraca."""
        cartas_melhores = [c for c in self._cartas if c > maior_carta] if maior_carta else self._cartas
        if cartas_melhores:
            return min(cartas_melhores, key=lambda c: c.forca)
        return min(self._cartas, key=lambda c: c.forca)

    def _escolher_carta_dificil(self, maior_carta: 'Carta | None') -> 'Carta':
        """Difícil: estratégia completa considerando manilhas, sequenciação e economia de cartas."""
        cartas_melhores = [c for c in self._cartas if c > maior_carta] if maior_carta else self._cartas

        # Se tem manilha e a maior carta também é forte, use a manilha
        manilhas = [c for c in self._cartas if c.manilha]
        if manilhas and maior_carta is not None and maior_carta.forca > 60:
            return min(cartas_melhores, key=lambda c: c.forca) if cartas_melhores else min(self._cartas, key=lambda c: c.forca)

        if cartas_melhores:
            # Jogue a carta mínima que bate — economize as fortes
            return min(cartas_melhores, key=lambda c: c.forca)
        else:
            # Não consegue bater — jogue a mais fraca para preservar cartas
            return min(self._cartas, key=lambda c: c.forca)

    # -- Avaliação da força da mão ------------------------------------------

    def _forca_relativa_mao(self) -> float:
        """Retorna um valor entre 0 e 1 indicando quão forte é a mão atual."""
        if not self._cartas:
            return 0.0
        # Manilhas valem muito; ranks altos valem mais
        total = sum(c.forca for c in self._cartas)
        # Normalização aproximada: manilha ~160, rank max ~80
        max_possible = 160 * 3
        return min(total / max_possible, 1.0)

    def forca_mao(self) -> float:
        """Método público para consulta externa da força da mão.
        
        Usado pelo backend (`Partida`) para decidir se a IA propõe truco.
        Retorna um valor entre 0 e 1.
        """
        return self._forca_relativa_mao()

    # -- Decisão de proposta por dificuldade --------------------------------

    def _decidir_proposta_facil(
        self, pontuacao_atual: int, pontuacao_proposta: int, forca_mao: float
    ) -> JogadaTruco | JogadaCorrer:
        """Fácil: aceita se a mão for razoável, senão corre."""
        import random
        if forca_mao > 0.4:
            return JogadaTruco(pontuacao_proposta)
        # Chance 50/50
        if random.random() > 0.5:
            return JogadaTruco(pontuacao_proposta)
        return JogadaCorrer()

    def _decidir_proposta_medio(
        self, pontuacao_atual: int, pontuacao_proposta: int, forca_mao: float
    ) -> JogadaTruco | JogadaCorrer:
        """Médio: avalia força da mão e risco da proposta."""
        if forca_mao > 0.5:
            # Mão boa — aceita e tenta contra-oferta se possível
            proximas = [p for p in (3, 6, 9, 12) if p > pontuacao_proposta]
            if proximas and forca_mao > 0.7:
                return JogadaTruco(proximas[0])
            return JogadaTruco(pontuacao_proposta)
        elif forca_mao > 0.3:
            return JogadaTruco(pontuacao_proposta)
        return JogadaCorrer()

    def _decidir_proposta_dificil(
        self, pontuacao_atual: int, pontuacao_proposta: int, forca_mao: float
    ) -> JogadaTruco | JogadaCorrer:
        """Difícil: análise profunda da mão, cartas restantes e probabilidade."""
        manilhas = sum(1 for c in self._cartas if c.manilha)
        cartas_fortes = sum(1 for c in self._cartas if c.forca > 50)

        # Pontuação interna da mão
        score = manilhas * 2 + cartas_fortes

        if score >= 4:
            # Mão muito forte — contra-oferta agressiva
            proximas = [p for p in (3, 6, 9, 12) if p > pontuacao_proposta]
            if proximas:
                return JogadaTruco(proximas[0])
            return JogadaTruco(pontuacao_proposta)
        elif score >= 2:
            # Mão razoável — aceita
            return JogadaTruco(pontuacao_proposta)
        elif score >= 1 and pontuacao_proposta <= 6:
            # Mão fraca mas proposta ainda é baixa — arrisca
            return JogadaTruco(pontuacao_proposta)
        else:
            # Mão fraca e proposta alta — corre
            return JogadaCorrer()


# ---------------------------------------------------------------------------
# Frontend protocol (for dependency injection)
# ---------------------------------------------------------------------------

class JogadorHumanoFrontend(Protocol):
    """Protocolo que um frontend de jogador humano deve implementar.

    Uma implementação via terminal já está disponível no arquivo
    ``jogador_terminal.py``.
    """

    def mostrar_mao(self, cartas: list['Carta'], vira: 'Carta') -> None:
        """Exibe as cartas da mão e a carta virada ao usuário."""
        ...

    def escolher_carta(
        self,
        cartas: list['Carta'],
        rodada: int,
        vencidas: int,
        maior_carta: 'Carta | None',
        vira: 'Carta | None',
    ) -> 'Carta':
        """Solicita ao usuário que escolha uma carta para jogar."""
        ...

    def decisao_proposta(
        self, pontuacao_atual: int, pontuacao_proposta: int
    ) -> JogadaTruco | JogadaCorrer:
        """Solicita ao usuário a decisão sobre uma proposta de truco."""
        ...
