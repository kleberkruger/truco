"""Contrato mínimo compartilhado pelas interfaces de apresentação."""
from typing import Protocol


class View(Protocol):
    def executar(self) -> None:
        """Inicia o loop de interação da interface."""
        ...
