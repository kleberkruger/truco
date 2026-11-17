"""Ponto de entrada do jogo de Truco — Versão 3.

Arquitetura: frontend ativo + backend passivo (máquina de estado).

O frontend (agente ativo) comanda o loop principal do jogo, enquanto o
backend (máquina de estado passiva) apenas responde a chamadas e retorna
objetos de estado para o frontend exibir.
"""

from frontend_terminal import FrontendTerminal


def main():
    frontend = FrontendTerminal()
    frontend.executar()


if __name__ == "__main__":
    main()
