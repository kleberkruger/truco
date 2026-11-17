"""Implementação terminal do frontend de Truco.

Fornece a concretização de todos os métodos abstratos de ``Frontend``
usando ``print()`` e ``input()`` para interagir com o usuário via terminal.
"""

from baralho import Carta
from jogador import Dificuldade
from estados import (
    ConfiguracaoJogo,
    EstadoInicioMao,
    EstadoCartasMao,
    EstadoPlacar,
    EstadoInicioRodada,
    EstadoPedirCarta,
    EstadoCartaJogada,
    EstadoVencedorRodada,
    EstadoPropostaTruco,
    EstadoPedirDecisaoTruco,
    EstadoRespostaTruco,
    EstadoResultadoMao,
    EstadoFimPartida,
    ComandoCarta,
    ComandoDecisaoTruco,
    ComandoPropostaTruco,
    Lado,
)
from frontend import Frontend


class FrontendTerminal(Frontend):
    """Frontend de Truco via terminal.

    Implementa todos os métodos abstratos de ``Frontend`` usando
    saída de texto no terminal e leitura de entrada do usuário.
    """

    def exibir_titulo(self) -> None:
        print("=" * 50)
        print("           🃏  T R U C O  🃏")
        print("=" * 50)
        print()

    def pedir_configuracao(self) -> ConfiguracaoJogo:
        nome_humano = input("Digite seu nome: ").strip() or "Jogador"
        nome_ia = input("Digite o nome da IA: ").strip() or "IA"

        print("\nDificuldade da IA:")
        print("  1. Fácil")
        print("  2. Médio")
        print("  3. Difícil")
        while True:
            try:
                opcao = int(input("Escolha (1-3): "))
                if opcao == 1:
                    dificuldade = Dificuldade.FACIL
                    break
                elif opcao == 2:
                    dificuldade = Dificuldade.MEDIO
                    break
                elif opcao == 3:
                    dificuldade = Dificuldade.DIFICIL
                    break
                print("Opção inválida. Digite 1, 2 ou 3.")
            except ValueError:
                print("Entrada inválida. Digite um número.")

        print("\nBaralho:")
        print("  1. Limpo (sem 4, 5, 6, 7)")
        print("  2. Sujo (com todas as cartas)")
        while True:
            try:
                opcao = int(input("Escolha (1-2): "))
                if opcao == 1:
                    baralho_limpo = True
                    break
                elif opcao == 2:
                    baralho_limpo = False
                    break
                print("Opção inválida. Digite 1 ou 2.")
            except ValueError:
                print("Entrada inválida. Digite um número.")

        return ConfiguracaoJogo(
            nome_humano=nome_humano,
            nome_ia=nome_ia,
            dificuldade=dificuldade,
            baralho_limpo=baralho_limpo,
        )

    def exibir_placar(self, estado: EstadoPlacar) -> None:
        print(f"\n📊 Placar: {estado.nome_a} {estado.pontos_a} x {estado.pontos_b} {estado.nome_b}")

    def exibir_inicio_mao(self, estado: EstadoInicioMao) -> None:
        print(f"\n{'─' * 40}")
        print(f"  Mão #{estado.numero_mao}")
        print(f"{'─' * 40}")

    def exibir_cartas_mao(self, estado: EstadoCartasMao) -> None:
        print(f"\n  Sua mão: {', '.join(str(c) for c in estado.cartas)}")
        print(f"  Carta virada: {estado.vira}")

    def exibir_inicio_rodada(self, estado: EstadoInicioRodada) -> None:
        indicador = " ← sua vez" if estado.vez_humano else ""
        print(f"\n  Rodada {estado.numero_rodada}: {estado.nome_jogador} joga{indicador}")

    def pedir_carta_ou_truco(
        self, estado: EstadoPedirCarta
    ) -> ComandoCarta | ComandoPropostaTruco:
        """Pede ao humano que escolha uma carta ou proponha truco.
        
        Se a pontuação da mão for menor que 12, oferece a opção de propor
        truco/seis/nove/doze antes de pedir a carta.
        """
        print(f"  Rodada {estado.numero_rodada} — Rodadas vencidas: {estado.rodadas_vencidas}")
        if estado.maior_carta_mesa:
            print(f"  Maior carta da mesa: {estado.maior_carta_mesa}")
        print(f"  Pontuação da mão: {estado.pontuacao_mao}")
        print("  Suas cartas:")
        for i, carta in enumerate(estado.cartas_disponiveis):
            print(f"    {i + 1}. {carta}")

        # Verificar se o humano pode propor truco
        if estado.pontuacao_mao < 12:
            proximas = [p for p in (3, 6, 9, 12) if p > estado.pontuacao_mao]
            if proximas:
                print("  Opções:")
                print("    T. Propor Truco")
                while True:
                    resp = input("  Digite o número da carta ou T para truco: ").strip().upper()
                    if resp == "T":
                        return self._pedir_proposta_truco(estado.pontuacao_mao)
                    try:
                        escolha = int(resp) - 1
                        if 0 <= escolha < len(estado.cartas_disponiveis):
                            carta = estado.cartas_disponiveis[escolha]
                            return ComandoCarta(carta)
                        print(f"  Escolha inválida. Digite 1-{len(estado.cartas_disponiveis)} ou T.")
                    except ValueError:
                        print("  Entrada inválida. Digite um número ou T.")

        # Se não pode propor truco, pedir apenas a carta
        while True:
            try:
                escolha = int(input("  Digite o número da carta: ")) - 1
                if 0 <= escolha < len(estado.cartas_disponiveis):
                    carta = estado.cartas_disponiveis[escolha]
                    return ComandoCarta(carta)
                print(f"  Escolha inválida. Digite um número entre 1 e {len(estado.cartas_disponiveis)}.")
            except ValueError:
                print("  Entrada inválida. Digite um número.")

    def _pedir_proposta_truco(self, pontuacao_atual: int) -> ComandoPropostaTruco:
        """Auxilia o humano a escolher o nível de proposta de truco."""
        nomes = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
        proximas = [p for p in (3, 6, 9, 12) if p > pontuacao_atual]
        
        print("  \n  Propostas disponíveis:")
        for p in proximas:
            print(f"    - {nomes[p]} ({p} pontos)")
        
        while True:
            try:
                escolha = int(input("  Digite a pontuação proposta: "))
                if escolha in proximas:
                    return ComandoPropostaTruco(pontuacao_proposta=escolha)
                print(f"  Escolha uma das opções: {proximas}")
            except ValueError:
                print("  Entrada inválida. Digite um número.")

    def exibir_carta_jogada(self, estado: EstadoCartaJogada) -> None:
        print(f"  {estado.nome_jogador} jogou {estado.carta}")

    def exibir_vencedor_rodada(self, estado: EstadoVencedorRodada) -> None:
        if estado.nome_vencedor is not None:
            lado = estado.lado_vencedor.value if estado.lado_vencedor else "?"
            print(f"  ✅ Rodada vencida por {estado.nome_vencedor} [LADO {lado}]")
        else:
            print(f"  🤝 Rodada terminada em empate")

    def exibir_proposta_truco(self, estado: EstadoPropostaTruco) -> None:
        nomes = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
        nome = nomes.get(estado.pontuacao_proposta, estado.pontuacao_proposta)
        print(f"\n  🔊 {estado.nome_propositor} gritou: {nome}!")

    def pedir_decisao_truco(self, estado: EstadoPedirDecisaoTruco) -> ComandoDecisaoTruco:
        nomes = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
        nome_proposta = nomes.get(estado.pontuacao_proposta, estado.pontuacao_proposta)

        print(f"\n  *** {nome_proposta}! (pontuação atual: {estado.pontuacao_atual}) ***")
        print("  1. Aceitar")
        print("  2. Correr")

        proximas = [p for p in (3, 6, 9, 12) if p > estado.pontuacao_proposta]
        if proximas:
            print("  3. Contra-oferecer")
            for p in proximas:
                print(f"     - {nomes.get(p, p)} ({p} pontos)")

        while True:
            try:
                opcao = int(input("  Sua decisão: "))
                if opcao == 1:
                    return ComandoDecisaoTruco(aceita=True, pontuacao_contra_oferta=None)
                if opcao == 2:
                    print("  Você correu!")
                    return ComandoDecisaoTruco(aceita=False, pontuacao_contra_oferta=None)
                if opcao == 3 and proximas:
                    while True:
                        try:
                            contra = int(input("  Digite a pontuação da contra-oferta: "))
                            if contra in proximas:
                                return ComandoDecisaoTruco(aceita=True, pontuacao_contra_oferta=contra)
                            print(f"  Escolha uma das opções: {proximas}")
                        except ValueError:
                            print("  Entrada inválida. Digite um número.")
                else:
                    print("  Opção inválida. Tente novamente.")
            except ValueError:
                print("  Entrada inválida. Digite um número.")

    def exibir_resposta_truco(self, estado: EstadoRespostaTruco) -> None:
        if estado.aceita:
            if estado.pontuacao_contra_oferta:
                nomes = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
                nome = nomes.get(estado.pontuacao_contra_oferta, estado.pontuacao_contra_oferta)
                print(f"  🆙 Contra-oferta: {nome} ({estado.pontuacao_contra_oferta} pontos)!")
            else:
                print(f"  ✅ Proposta aceita!")
        else:
            print(f"  🏃 Você correu!")

    def exibir_resultado_mao(self, estado: EstadoResultadoMao) -> None:
        if estado.lado_ganhador == Lado.LADO_A:
            print(f"\n  🏆 {estado.nome_a} ganhou {estado.pontos} ponto(s) nesta mão!")
        elif estado.lado_ganhador == Lado.LADO_B:
            print(f"\n  🏆 {estado.nome_b} ganhou {estado.pontos} ponto(s) nesta mão!")
        else:
            print(f"\n  🤝 Mão empatada!")

    def exibir_fim_partida(self, estado: EstadoFimPartida) -> None:
        print(f"\n{'=' * 50}")
        if estado.lado_ganhador == Lado.LADO_A:
            print(f"  🎉  {estado.nome_a} venceu a partida!  🎉")
        else:
            print(f"  🎉  {estado.nome_b} venceu a partida!  🎉")
        print(f"  Placar final: {estado.nome_a} {estado.pontos_a} x {estado.pontos_b} {estado.nome_b}")
        print(f"{'=' * 50}")
