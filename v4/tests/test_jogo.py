import unittest
from aplicacao.sessao import Sessao
from dominio.truco import Estado

class TesteTruco(unittest.TestCase):
    def test_modalidades(self):
        for n in (1, 2, 3):
            s = Sessao(n)
            self.assertEqual(len(s.partida.jogadores), n * 2)
            self.assertEqual(s.partida.modalidade, n)
            self.assertEqual(len(s.humano.cartas), 3)

    def test_turnos_e_simulacao(self):
        for n in (1, 2, 3):
            s = Sessao(n, seed=12)
            for _ in range(2000):
                p=s.partida
                if p.estado==Estado.ENCERRADA: break
                if p.estado==Estado.AGUARDANDO:
                    s.proxima_mao()
                elif p.mao_de_onze==0:
                    s.decidir_onze(True)
                elif p.estado==Estado.PEDIDO_PENDENTE and p.pedido_pendente[0]==1:
                    s.responder(True)
                elif s.precisa_humano:
                    s.jogar(0)
                else:
                    self.assertTrue(s.avancar_bot())
            self.assertEqual(s.partida.estado, Estado.ENCERRADA)
            self.assertGreaterEqual(max(s.partida.pontos), 12)

    def test_aposta(self):
        s=Sessao(1)
        # A mão pode começar com o humano.
        self.assertTrue(s.precisa_humano)
        s.pedir_truco()
        self.assertEqual(s.partida.estado, Estado.PEDIDO_PENDENTE)
        self.assertTrue(s.avancar_bot())
        self.assertIn(s.partida.estado,(Estado.JOGANDO,Estado.AGUARDANDO))

    def test_contra_aumento(self):
        s = Sessao(1, seed=4)
        # Se a vez inicial for humana, pede truco e verifica a resposta dos bots.
        if s.precisa_humano:
            s.pedir_truco()
            self.assertTrue(s.avancar_bot())
        # Testa diretamente a transição de contra-aumento no domínio.
        from dominio.truco import Partida, Estado
        from dominio.participante import Jogador
        a, b = Jogador("A"), Jogador("B")
        partida = Partida.individual(a, b)
        partida.iniciar_mao()
        partida.pedir_aumento(a)
        self.assertEqual(partida.aumentar_aposta_pendente(b), 6)
        self.assertEqual(partida.pedido_pendente, (1, 6))
        partida.responder_aumento(a, True)
        self.assertEqual(partida.valor_mao, 6)
        self.assertEqual(partida.estado, Estado.JOGANDO)

if __name__=='__main__':
    unittest.main()
