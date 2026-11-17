"""Interface de terminal para o Truco Paulista.

Não contém regras do jogo — apenas conversa com a Sessão
e exibe informações no terminal.
"""

from __future__ import annotations

import time
from aplicacao.sessao import Sessao
from dominio.estado import EstadoPartida
from estrategia.ia import Dificuldade


class Terminal:
    """Interface de texto para jogar Truco no terminal."""

    def __init__(
        self,
        *,
        modalidade: int = 2,
        limpo: bool = True,
        dificuldade: Dificuldade = Dificuldade.MEDIO,
        seed: int | None = None,
    ) -> None:
        self.sessao = Sessao(
            modalidade=modalidade,
            limpo=limpo,
            dificuldade=dificuldade,
            seed=seed,
        )
        self._eventos_exibidos = 0

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def _cabecalho(self) -> None:
        p = self.sessao.partida
        print('\n' + '=' * 60)
        print(f'TRUCO PAULISTA | MÃO {p.mao_numero} | VALE {p.valor_mao}')
        print(f'PLACAR: SUA EQUIPE {p.pontos[0]}  ×  {p.pontos[1]} ADVERSÁRIOS')
        print('=' * 60)

    def _mostrar_eventos(self) -> None:
        eventos = self.sessao.eventos
        novos = eventos[self._eventos_exibidos:]
        if novos:
            print('\nÚltimos acontecimentos:')
            for ev in novos:
                print(f'  • {ev.mensagem}')
            self._eventos_exibidos = len(eventos)

    def _mostrar_mesa(self) -> None:
        p = self.sessao.partida
        humano = self.sessao.humano

        print('\n--- MESA ---')
        print(f'Vira: {p.vira}')

        if not p.jogadas_atuais:
            print('Cartas na mesa: Nenhuma carta jogada nesta vaza.')
        else:
            maior_forca = max(j.carta.forca for j in p.jogadas_atuais)
            print('Cartas na mesa:')
            for j in p.jogadas_atuais:
                destaque = ' ★ [MAIOR]' if j.carta.forca == maior_forca else ''
                is_parceiro = (
                    j.jogador in p.equipes[0].jogadores
                    and j.jogador is not humano
                )
                tag = ' (Parceiro)' if is_parceiro else ''
                print(f'  • {j.jogador.nome}{tag}: {j.carta}{destaque}')

        if p.estado == EstadoPartida.JOGANDO and p.jogador_da_vez:
            if p.jogadas_atuais:
                primeiro = p.jogadas_atuais[0].jogador
                idx = p.jogadores.index(primeiro)
                ordem = [
                    p.jogadores[(idx + i) % len(p.jogadores)]
                    for i in range(len(p.jogadores))
                ]
                faltantes = ordem[len(p.jogadas_atuais):]
            else:
                faltantes = list(p.jogadores)

            if faltantes:
                fmt = []
                for j in faltantes:
                    tag = ''
                    if j is humano:
                        tag = ' (Você)'
                    elif j in p.equipes[0].jogadores:
                        tag = ' (Parceiro)'
                    fmt.append(f'{j.nome}{tag}')
                print(f'Faltam jogar: {", ".join(fmt)}')

    def _mostrar_cartas(self) -> None:
        jogador = self.sessao.humano
        print('\nSuas cartas:')
        for i, carta in enumerate(jogador.cartas, start=1):
            marca = ' [MANILHA]' if carta.manilha else ''
            print(f'  {i}. {carta}{marca}')

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def executar(self) -> None:
        p = self.sessao.partida
        print('\nBem-vindo ao Truco Paulista!')
        print('Você joga pela sua equipe; os demais são controlados por bots.\n')

        while p.estado != EstadoPartida.ENCERRADA:
            self._cabecalho()
            self._mostrar_eventos()

            # Aguardando iniciar mão
            if p.estado == EstadoPartida.AGUARDANDO:
                input('\nPressione ENTER para iniciar a próxima mão...')
                self.sessao.proxima_mao()
                continue

            self._mostrar_mesa()

            # Mão de onze
            if p.mao_de_onze is not None:
                if p.mao_de_onze == 0:
                    resp = input(
                        '\nSua equipe está com 11 pontos. '
                        'Jogar a mão? [s/N]: '
                    ).strip().lower()
                    self.sessao.decidir_onze(resp in {'s', 'sim'})
                else:
                    print('\nOs adversários estão decidindo a mão de onze...')
                    self.sessao.avancar_bot()
                    time.sleep(0.4)
                continue

            # Pedido de truco pendente
            if p.estado == EstadoPartida.PEDIDO_PENDENTE:
                solicitante, valor = p.pedido_pendente
                if solicitante == 0:
                    print('\nSua equipe pediu aumento; aguardando os adversários...')
                    self.sessao.avancar_bot()
                    time.sleep(0.4)
                else:
                    opcoes = '[a]ceitar / [c]orrer'
                    if valor < 12:
                        opcoes += ' / [u]mentar'
                    resp = input(
                        f'\nOs adversários pediram {valor} pontos. '
                        f'{opcoes}: '
                    ).strip().lower()
                    if resp in {'a', 'aceitar', 's'}:
                        self.sessao.responder(True)
                    elif resp in {'c', 'correr', 'n'}:
                        self.sessao.responder(False)
                    elif resp in {'u', 'aumentar'} and valor < 12:
                        self.sessao.aumentar()
                    else:
                        print('Opção inválida.')
                    continue

            # Vez do humano
            if self.sessao.precisa_humano:
                self._mostrar_cartas()
                opcoes = 'Digite o número da carta'
                if self.sessao.pode_trucar():
                    opcoes += ' ou T para pedir truco'
                resp = input(f'\nSua vez. {opcoes}: ').strip().lower()
                if resp in {'t', 'truco'}:
                    try:
                        self.sessao.pedir_truco()
                    except ValueError as err:
                        print(f'Não foi possível: {err}')
                else:
                    try:
                        indice = int(resp) - 1
                        self.sessao.jogar(indice)
                    except (ValueError, IndexError) as err:
                        print(f'Entrada inválida: {err}')
                continue

            # Vez do bot
            jogador = p.jogador_da_vez
            if jogador:
                print(f'\nVez de {jogador.nome}; aguardando...')
                self.sessao.avancar_bot()
                time.sleep(0.45)
            continue

        # Fim de jogo
        self._cabecalho()
        self._mostrar_eventos()
        if p.vencedor == 0:
            print('\n🏆 Você venceu a partida!')
        else:
            print('\nFim de jogo. Os adversários venceram.')


def main() -> None:
    """Ponto de entrada para o terminal interativo."""
    print('NOVO JOGO')
    print('1. Individual (1 × 1)')
    print('2. Duplas (2 × 2)')
    print('3. Trios (3 × 3; baralho sujo)')

    while True:
        valor = input('Modalidade [1-3] (padrão 2): ').strip() or '2'
        if valor in {'1', '2', '3'}:
            modalidade = int(valor)
            break
        print('Escolha 1, 2 ou 3.')

    limpo = modalidade != 3
    if modalidade != 3:
        escolha = input('Baralho [l]impo ou [s]ujo? (padrão l): ').strip().lower()
        limpo = escolha not in {'s', 'sujo'}

    print('Dificuldade dos bots:')
    print('1. Fácil')
    print('2. Médio')
    print('3. Difícil')
    while True:
        diff = input('Dificuldade [1-3] (padrão 2): ').strip() or '2'
        if diff in {'1', '2', '3'}:
            dificuldade = {
                '1': Dificuldade.FACIL,
                '2': Dificuldade.MEDIO,
                '3': Dificuldade.DIFICIL,
            }[diff]
            break
        print('Escolha 1, 2 ou 3.')

    Terminal(
        modalidade=modalidade,
        limpo=limpo,
        dificuldade=dificuldade,
    ).executar()


if __name__ == '__main__':
    main()
