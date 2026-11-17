import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Truco Paulista")
    parser.add_argument("--interface", choices=("gui", "terminal", "pyqt"), default="pyqt",
                        help="Interface de apresentação (padrão: pyqt)")
    args = parser.parse_args()

    if args.interface == "terminal":
        from interfaces.terminal import Terminal
        Terminal().executar()
    elif args.interface == "gui":
        from interfaces.pygame_ui import TelaTruco
        TelaTruco().executar()
    else:
        from PyQt6.QtWidgets import QApplication
        from interfaces.pyqt6_ui import TelaTrucoPyQt
        app = QApplication(sys.argv)
        tela = TelaTrucoPyQt()
        tela.executar()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
