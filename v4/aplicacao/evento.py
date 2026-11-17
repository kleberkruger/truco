"""Sistema de eventos para comunicação entre Sessão e Interface.

Os eventos são dados imutáveis que descrevem o que aconteceu no jogo.
A interface os consome para atualizar a tela, mas não interfere no jogo.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Evento:
    """Um evento do jogo emitido pela Sessão.

    Args:
        tipo: Categoria do evento (mao, carta, vaza, pedido, resposta, onze, fim).
        mensagem: Texto descritivo do evento.
        timestamp: Hora em que o evento ocorreu.
    """
    tipo: str
    mensagem: str
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return self.mensagem
