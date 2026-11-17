"""Estados da partida."""

from enum import Enum, auto


class EstadoPartida(Enum):
    """Estados possíveis de uma partida."""
    AGUARDANDO = auto()      # Entre mãos, aguardando iniciar próxima
    JOGANDO = auto()          # Mão em andamento
    PEDIDO_PENDENTE = auto()  # Truco pedido, aguardando resposta
    ENCERRADA = auto()        # Partida finalizada


class Modalidade:
    """Modalidades de jogo suportadas."""
    INDIVIDUAL = 1
    DUPLAS = 2
    TRIOS = 3

    @staticmethod
    def nome(modalidade: int) -> str:
        return {
            Modalidade.INDIVIDUAL: 'Individual (1×1)',
            Modalidade.DUPLAS: 'Duplas (2×2)',
            Modalidade.TRIOS: 'Trios (3×3)',
        }.get(modalidade, 'Desconhecida')
