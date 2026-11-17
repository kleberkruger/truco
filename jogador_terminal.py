"""Frontend terminal para JogadorHumano.

Fornece a implementação de ``JogadorHumanoFrontend`` via terminal,
separando a interação com o usuário da lógica de jogo do backend.
"""

from jogador import JogadaCarta, JogadaCorrer, JogadaTruco
from baralho import Carta


class JogadorHumanoTerminal:
    """Implementação de frontend terminal para JogadorHumano.

    Injete esta instância no construtor de ``JogadorHumano`` para que
    toda a interação com o terminal seja centralizada aqui.
    """

    def mostrar_mao(self, cartas: list[Carta], vira: Carta) -> None:
        """Exibe as cartas da mão e a carta virada ao usuário."""
        print(f"Sua mão: {', '.join(str(c) for c in cartas)}")
        print(f"Carta virada: {vira}")

    def escolher_carta(
        self,
        cartas: list[Carta],
        rodada: int,
        vencidas: int,
        maior_carta: Carta | None,
        vira: Carta | None,
    ) -> Carta:
        """Solicita ao usuário que escolha uma carta para jogar via terminal."""
        print("------------------------------------------------------------")
        print(f"Rodada {rodada}: {vencidas} rodadas vencidas")
        print(f"Vira: {vira}")
        print(f"Maior carta da mesa: {maior_carta}")
        print("Escolha uma carta para jogar:")
        for i, carta in enumerate(cartas):
            print(f"  {i + 1}. {carta}")

        while True:
            try:
                escolha = int(input("Digite o número da carta: ")) - 1
                if 0 <= escolha < len(cartas):
                    return cartas[escolha]
                print(f"Escolha inválida. Digite um número entre 1 e {len(cartas)}.")
            except ValueError:
                print("Entrada inválida. Digite um número.")

    def decisao_proposta(
        self, pontuacao_atual: int, pontuacao_proposta: int
    ) -> JogadaTruco | JogadaCorrer:
        """Solicita ao usuário a decisão sobre uma proposta de truco via terminal."""
        nomes = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
        nome_proposta = nomes.get(pontuacao_proposta, pontuacao_proposta)

        print(f"\n*** {nome_proposta}! (pontuação atual: {pontuacao_atual}) ***")
        print("  1. Aceitar")
        print("  2. Correr")

        proximas = [p for p in (3, 6, 9, 12) if p > pontuacao_proposta]
        if proximas:
            print("  3. Contra-oferecer")
            for p in proximas:
                print(f"     - {nomes.get(p, p)} ({p} pontos)")

        while True:
            try:
                opcao = int(input("Sua decisão: "))
                if opcao == 1:
                    return JogadaTruco(pontuacao_proposta)
                if opcao == 2:
                    print("Você correu!")
                    return JogadaCorrer()
                if opcao == 3 and proximas:
                    print(f"Contra-ofertas disponíveis: {[nomes.get(p, p) for p in proximas]}")
                    while True:
                        try:
                            contra = int(input("Digite a pontuação da contra-oferta: "))
                            if contra in proximas:
                                return JogadaTruco(contra)
                            print(f"Escolha uma das opções: {proximas}")
                        except ValueError:
                            print("Entrada inválida. Digite um número.")
                else:
                    print("Opção inválida. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Digite um número.")
