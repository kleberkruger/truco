"""Truco Paulista — Versão 5.

Ponto de entrada principal. Escolha a interface desejada:
  --interface terminal → Interface de texto
  --interface PyQt6 → Interface gráfica PyQt6 (padrão)
"""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Truco Paulista — Versão 5 (Arquitetura Modular)',
    )
    parser.add_argument(
        '--interface',
        choices=('terminal', 'pyqt'),
        default='pyqt',
        help='Interface de apresentação (padrão: pyqt)',
    )
    args = parser.parse_args()

    if args.interface == 'terminal':
        from interfaces.terminal import Terminal
        Terminal().executar()
    else:
        from PyQt6.QtWidgets import QApplication
        from interfaces.pyqt import TelaTrucoPyQt

        app = QApplication(sys.argv)
        tela = TelaTrucoPyQt()
        tela.executar()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()
