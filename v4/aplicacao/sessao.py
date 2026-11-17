"""Orquestra turnos, bots e ações sem importar nenhuma biblioteca gráfica."""
from dataclasses import dataclass
import random
from dominio.participante import Jogador
from dominio.truco import Partida, Estado

@dataclass(frozen=True)
class Evento:
    tipo: str
    mensagem: str

class Sessao:
    def __init__(self, modalidade=2, limpo=True, nomes=None, seed=None):
        if modalidade not in (1, 2, 3):
            raise ValueError('Modalidade inválida')
        if modalidade == 3:
            limpo = False
        nomes = nomes or ['Você', 'Luna', 'Theo', 'Maya', 'Davi', 'Nina']
        if len(nomes) < modalidade * 2:
            raise ValueError('Nomes insuficientes')
        self.rng = random.Random(seed)
        self.humano = Jogador(nomes[0])
        # Um jogador humano e demais bots. Distribuição em equipes alternadas.
        jogadores = [Jogador(n) for n in nomes[:modalidade * 2]]
        jogadores[0] = self.humano
        from dominio.participante import Equipe
        self.partida = Partida(Equipe(*jogadores[::2]), Equipe(*jogadores[1::2]), limpo=limpo)
        self.eventos: list[Evento] = []
        self.ultima_vaza = None
        self.partida.iniciar_mao()
        self._emitir('mao', 'Nova mão! Boa sorte.')

    def _emitir(self, tipo, mensagem):
        self.eventos.append(Evento(tipo, mensagem))
        self.eventos = self.eventos[-30:]

    @property
    def precisa_humano(self):
        p = self.partida
        return p.estado == Estado.JOGANDO and p.mao_de_onze is None and p.jogador_da_vez is self.humano

    def jogar(self, indice):
        if not self.precisa_humano:
            raise ValueError('Aguarde sua vez')
        self._jogar(self.humano, indice)

    def _jogar(self, jogador, indice):
        p = self.partida
        carta = jogador.cartas[indice]
        resultado = p.jogar(jogador, indice)
        self._emitir('carta', f'{jogador.nome} jogou {carta}')
        if resultado is not None:
            self.ultima_vaza = resultado
            if resultado.vencedor is None:
                self._emitir('vaza', f'Vaza {resultado.numero}: empate!')
            else:
                self._emitir('vaza', f'Vaza {resultado.numero}: lado {resultado.vencedor + 1} venceu')
        if p.estado in (Estado.AGUARDANDO, Estado.ENCERRADA):
            self._emitir('mao_fim', f'Placar: {p.pontos[0]} × {p.pontos[1]}')

    def pode_trucar(self):
        p = self.partida
        return p.pode_pedir_aumento(self.humano)

    def pedir_truco(self):
        if not self.pode_trucar():
            raise ValueError('Não é possível aumentar agora')
        valor = self.partida.pedir_aumento(self.humano)
        self._emitir('pedido', f'Você pediu {valor}!')

    def responder(self, aceitar):
        p = self.partida
        if p.estado != Estado.PEDIDO_PENDENTE:
            raise ValueError('Não há pedido pendente')
        solicitante, valor = p.pedido_pendente
        if solicitante == 0:
            raise ValueError('O pedido é seu: aguarde o adversário')
        p.responder_aumento(self.humano, aceitar)
        self._emitir('resposta', 'Você aceitou!' if aceitar else 'Você correu da aposta')

    def aumentar(self):
        p = self.partida
        if p.estado != Estado.PEDIDO_PENDENTE or p.pedido_pendente is None:
            raise ValueError('Não há pedido pendente')
        solicitante, valor = p.pedido_pendente
        if solicitante == 0:
            raise ValueError('O pedido é da sua equipe')
        novo_valor = p.aumentar_aposta_pendente(self.humano)
        self._emitir('pedido', f'Você aumentou para {novo_valor}!')

    def decidir_onze(self, jogar):
        p = self.partida
        if p.mao_de_onze != 0:
            raise ValueError('A decisão não pertence ao seu lado')
        p.decidir_mao_onze(self.humano, jogar)
        self._emitir('onze', 'Mão de onze aceita' if jogar else 'Mão de onze recusada')

    def avancar_bot(self):
        """Executa uma única decisão automática; a interface controla o ritmo."""
        p = self.partida
        if p.estado in (Estado.ENCERRADA, Estado.AGUARDANDO):
            return False
        if p.mao_de_onze is not None:
            if p.mao_de_onze == 0:
                return False
            j = p.equipes[1].jogadores[0]
            p.decidir_mao_onze(j, True)
            self._emitir('onze', 'Adversários aceitaram a mão de onze')
            return True
        if p.estado == Estado.PEDIDO_PENDENTE:
            solicitante, valor = p.pedido_pendente
            if solicitante != 0:
                return False
            bot = p.equipes[1].jogadores[0]
            aceitar = self.rng.random() < (0.82 if valor <= 6 else 0.64)
            p.responder_aumento(bot, aceitar)
            self._emitir('resposta', f'Adversários {"aceitaram" if aceitar else "correram"}!')
            return True
        j = p.jogador_da_vez
        if j is self.humano:
            return False
        # IA simples: escolhe entre cartas válidas, com preferência moderada pela menor.
        cartas = j.cartas
        if not cartas:
            return False
        indice = min(range(len(cartas)), key=lambda i: cartas[i].forca) if self.rng.random() < .55 else self.rng.randrange(len(cartas))
        self._jogar(j, indice)
        return True

    def proxima_mao(self):
        if self.partida.estado != Estado.AGUARDANDO:
            return False
        self.ultima_vaza = None
        self.partida.iniciar_mao()
        self._emitir('mao', f'Mão {self.partida.mao_numero} iniciada')
        return True
