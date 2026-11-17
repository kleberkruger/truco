"""Interface de terminal. Não contém regras do truco: apenas conversa com Sessao."""
from __future__ import annotations

import time

from aplicacao.sessao import Sessao
from dominio.truco import Estado


class Terminal:
    def __init__(self, *, modalidade: int = 2, limpo: bool = True, seed=None):
        self.sessao = Sessao(modalidade=modalidade, limpo=limpo, seed=seed)
        self._eventos_exibidos = 0

    def _linha(self):
        p = self.sessao.partida
        print("\n" + "=" * 60)
        print(f"TRUCO PAULISTA | MÃO {p.mao_numero} | VALE {p.valor_mao}")
        print(f"PLACAR: SUA EQUIPE {p.pontos[0]}  ×  {p.pontos[1]} ADVERSÁRIOS")
        print("=" * 60)

    def _mostrar_eventos(self):
        eventos = self.sessao.eventos
        if eventos[self._eventos_exibidos:]:
            print("\nÚltimos acontecimentos:")
            for evento in eventos[self._eventos_exibidos:]:
                print(f"  • {evento.mensagem}")
            self._eventos_exibidos = len(eventos)

    def _mostrar_mesa(self):
        p = self.sessao.partida
        humano = self.sessao.humano

        print("\n--- MESA ---")
        print(f"Vira: {p.vira}")

        # Cartas jogadas na vaza atual com destaque para a maior carta
        if not p.jogadas:
            print("Cartas na mesa: Nenhuma carta jogada nesta vaza.")
        else:
            maior_forca = max(j.carta.forca for j in p.jogadas)
            print("Cartas na mesa:")
            for j in p.jogadas:
                is_maior = (j.carta.forca == maior_forca)
                destaque = " ★ [MAIOR CARTA]" if is_maior else ""
                is_parceiro = (j.jogador in p.equipes[0].jogadores and j.jogador is not humano)
                tag_parceiro = " (Seu parceiro)" if is_parceiro else ""
                print(f"  • {j.jogador.nome}{tag_parceiro}: {j.carta}{destaque}")

        # Jogadores que ainda faltam jogar nesta vaza
        if p.estado == Estado.JOGANDO and p.jogador_da_vez:
            primeiro_jogador = p.jogadas[0].jogador if p.jogadas else p.jogador_da_vez
            idx_inicio = p.jogadores.index(primeiro_jogador)
            ordem_vaza = [p.jogadores[(idx_inicio + i) % len(p.jogadores)] for i in range(len(p.jogadores))]
            faltantes = ordem_vaza[len(p.jogadas):]

            if faltantes:
                fmt_faltantes = []
                for j in faltantes:
                    is_parceiro = (j in p.equipes[0].jogadores and j is not humano)
                    suffix = " (Seu parceiro)" if is_parceiro else ""
                    is_voce = " (Você)" if j is humano else ""
                    fmt_faltantes.append(f"{j.nome}{is_voce}{suffix}")

                print(f"Faltam jogar nesta vaza: {', '.join(fmt_faltantes)}")

    def _mostrar_cartas(self):
        jogador = self.sessao.humano
        print("\nSuas cartas:")
        for i, carta in enumerate(jogador.cartas, start=1):
            marca = " [MANILHA]" if carta.manilha else ""
            print(f"  {i}. {carta}{marca}")

    @staticmethod
    def _escolher_modalidade():
        print("NOVO JOGO")
        print("1. Individual (1 × 1)")
        print("2. Duplas (2 × 2)")
        print("3. Trios (3 × 3; baralho sujo)")
        while True:
            valor = input("Modalidade [1-3] (padrão 2): ").strip() or "2"
            if valor in {"1", "2", "3"}:
                return int(valor)
            print("Escolha 1, 2 ou 3.")

    def executar(self):
        p = self.sessao.partida
        print("\nBem-vindo ao Truco Paulista!")
        print("Você joga pela sua equipe; os demais participantes são controlados por bots.")
        while p.estado != Estado.ENCERRADA:
            self._linha()
            self._mostrar_eventos()

            if p.estado == Estado.AGUARDANDO:
                input("\nPressione ENTER para iniciar a próxima mão...")
                self.sessao.proxima_mao()
                continue

            self._mostrar_mesa()

            if p.mao_de_onze is not None:
                if p.mao_de_onze == 0:
                    resposta = input("\nSua equipe está com 11 pontos. Jogar a mão? [s/N]: ").strip().lower()
                    self.sessao.decidir_onze(resposta in {"s", "sim"})
                else:
                    print("\nOs adversários estão decidindo a mão de onze...")
                    self.sessao.avancar_bot()
                    time.sleep(0.4)
                continue

            if p.estado == Estado.PEDIDO_PENDENTE:
                solicitante, valor = p.pedido_pendente
                if solicitante == 0:
                    print("\nSua equipe pediu aumento; aguardando os adversários...")
                    self.sessao.avancar_bot()
                    time.sleep(0.4)
                else:
                    opcoes = "[a]ceitar / [c]orrer"
                    if valor < 12:
                        opcoes += " / [u]mentar"
                    resposta = input(f"\nOs adversários pediram {valor} pontos. {opcoes}: ").strip().lower()
                    if resposta in {"a", "aceitar", "s"}:
                        self.sessao.responder(True)
                    elif resposta in {"c", "correr", "n"}:
                        self.sessao.responder(False)
                    elif resposta in {"u", "aumentar"} and valor < 12:
                        self.sessao.aumentar()
                    else:
                        print("Opção inválida.")
                    continue

            if self.sessao.precisa_humano:
                self._mostrar_cartas()
                opcoes = "Digite o número da carta"
                if self.sessao.pode_trucar():
                    opcoes += " ou T para pedir truco"
                resposta = input(f"\nSua vez. {opcoes}: ").strip().lower()
                if resposta in {"t", "truco"}:
                    try:
                        self.sessao.pedir_truco()
                    except ValueError as erro:
                        print(f"Não foi possível: {erro}")
                else:
                    try:
                        indice = int(resposta) - 1
                        self.sessao.jogar(indice)
                    except (ValueError, IndexError) as erro:
                        print(f"Entrada inválida: {erro}")
                continue

            print(f"\nVez de {p.jogador_da_vez.nome}; aguardando...")
            self.sessao.avancar_bot()
            time.sleep(0.45)

        self._linha()
        self._mostrar_eventos()
        if p.vencedor == 0:
            print("\n🏆 Você venceu a partida!")
        else:
            print("\nFim de jogo. Os adversários venceram.")


def main():
    modalidade = Terminal._escolher_modalidade()
    limpo = modalidade != 3
    if modalidade != 3:
        escolha = input("Baralho [l]impo ou [s]ujo? (padrão l): ").strip().lower()
        limpo = escolha not in {"s", "sujo"}
    Terminal(modalidade=modalidade, limpo=limpo).executar()


if __name__ == "__main__":
    main()
