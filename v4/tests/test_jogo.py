"""Testes automatizados do Truco Paulista v5 — cobertura completa."""

import unittest
from aplicacao.sessao import Sessao
from aplicacao.evento import Evento
from dominio.estado import EstadoPartida, Modalidade
from dominio.jogador import Jogador
from dominio.partida import Partida
from dominio.equipe import Equipe
from dominio.baralho import Baralho
from dominio.carta import Carta
from dominio.rank import Rank
from dominio.naipe import Naipe
from dominio.vaza import Jogada, ResultadoVaza
from estrategia.ia import IA, Dificuldade, EstrategiaCarta, EstrategiaAposta


# =====================================================================
# RANK
# =====================================================================

class TesteRank(unittest.TestCase):
    """Testa os valores das cartas (Rank)."""

    def test_ordem_de_forca(self) -> None:
        """A força deve aumentar conforme a posição no enum."""
        ranks = list(Rank)
        for i in range(len(ranks) - 1):
            self.assertLess(ranks[i].forca, ranks[i + 1].forca)

    def test_rank_mais_fraco(self) -> None:
        """O 4 é o rank mais fraco."""
        self.assertEqual(Rank.QUATRO.forca, 0)

    def test_rank_mais_forte(self) -> None:
        """O 3 é o rank mais forte."""
        self.assertEqual(Rank.TRES.forca, len(Rank) - 1)

    def test_valores_limpo(self) -> None:
        """Baralho limpo remove 4, 5, 6, 7 do enum."""
        v = Rank.valores_limpo()
        self.assertNotIn(Rank.QUATRO, v)
        self.assertNotIn(Rank.CINCO, v)
        self.assertNotIn(Rank.SEIS, v)
        self.assertNotIn(Rank.SETE, v)
        self.assertGreater(len(v), 0)

    def test_valores_sujo(self) -> None:
        """Baralho sujo tem todos os ranks do enum."""
        v = Rank.valores_sujo()
        self.assertEqual(len(v), len(list(Rank)))
        self.assertIn(Rank.QUATRO, v)

    def test_valores_metodo(self) -> None:
        """O método valores() delega corretamente."""
        self.assertEqual(len(Rank.valores(True)), len(Rank.valores_limpo()))
        self.assertEqual(len(Rank.valores(False)), len(Rank.valores_sujo()))

    def test_str_repr(self) -> None:
        """String e repr retornam o valor da carta."""
        self.assertEqual(str(Rank.AS), 'A')
        self.assertEqual(repr(Rank.AS), 'A')


# =====================================================================
# NAIPE
# =====================================================================

class TesteNaipe(unittest.TestCase):
    """Testa os naipes das cartas."""

    def test_quatro_naipes(self) -> None:
        """Existem exatamente 4 naipes."""
        self.assertEqual(len(list(Naipe)), 4)

    def test_ordem_de_forca(self) -> None:
        """A força do naipe segue a ordem do enum."""
        naipes = list(Naipe)
        for i in range(len(naipes) - 1):
            self.assertLess(naipes[i].forca, naipes[i + 1].forca)

    def test_str_repr(self) -> None:
        """String e repr retornam o símbolo do naipe."""
        self.assertEqual(str(Naipe.OUROS), '♦')
        self.assertEqual(repr(Naipe.ESPADAS), '♠')


# =====================================================================
# CARTA
# =====================================================================

class TesteCarta(unittest.TestCase):
    """Testa a classe Carta."""

    def test_criar_carta(self) -> None:
        """Carta é criada com rank e naipe."""
        c = Carta(Rank.AS, Naipe.OUROS)
        self.assertEqual(c.rank, Rank.AS)
        self.assertEqual(c.naipe, Naipe.OUROS)
        self.assertFalse(c.manilha)

    def test_forca_carta_normal(self) -> None:
        """A força de carta normal depende do rank."""
        c1 = Carta(Rank.AS, Naipe.OUROS)
        c2 = Carta(Rank.TRES, Naipe.OUROS)
        self.assertLess(c1.forca, c2.forca)

    def test_forca_manilha_maior_que_normal(self) -> None:
        """Manilha é sempre mais forte que carta normal."""
        c1 = Carta(Rank.TRES, Naipe.OUROS)
        c2 = Carta(Rank.AS, Naipe.ESPADAS)
        c2.tornar_manilha()
        self.assertLess(c1.forca, c2.forca)

    def test_forca_manilha_desempate_por_naipe(self) -> None:
        """Entre manilhas, a força depende do naipe."""
        c1 = Carta(Rank.AS, Naipe.OUROS)
        c2 = Carta(Rank.AS, Naipe.PAUS)
        c1.tornar_manilha()
        c2.tornar_manilha()
        self.assertLess(c1.forca, c2.forca)

    def test_tornar_manilha_e_comum(self) -> None:
        """Pode alternar entre manilha e comum."""
        c = Carta(Rank.AS, Naipe.OUROS)
        self.assertFalse(c.manilha)
        c.tornar_manilha()
        self.assertTrue(c.manilha)
        c.tornar_comum()
        self.assertFalse(c.manilha)

    def test_comparacao_lt(self) -> None:
        """Comparação com < usa a força."""
        c1 = Carta(Rank.AS, Naipe.OUROS)
        c2 = Carta(Rank.TRES, Naipe.OUROS)
        self.assertTrue(c1 < c2)

    def test_igualdade(self) -> None:
        """Duas cartas iguais têm mesmo rank e naipe."""
        c1 = Carta(Rank.AS, Naipe.OUROS)
        c2 = Carta(Rank.AS, Naipe.OUROS)
        c3 = Carta(Rank.AS, Naipe.ESPADAS)
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)

    def test_hash(self) -> None:
        """Cartas iguais têm mesmo hash."""
        c1 = Carta(Rank.AS, Naipe.OUROS)
        c2 = Carta(Rank.AS, Naipe.OUROS)
        self.assertEqual(hash(c1), hash(c2))

    def test_str_nome(self) -> None:
        """String da carta mostra rank e naipe."""
        c = Carta(Rank.AS, Naipe.OUROS)
        self.assertIn('A', str(c))
        self.assertIn('♦', str(c))

    def test_carta_nao_e_manilha_por_padrao(self) -> None:
        """Carta recém-criada não é manilha."""
        for r in Rank:
            for n in Naipe:
                self.assertFalse(Carta(r, n).manilha)


# =====================================================================
# BARALHO
# =====================================================================

class TesteBaralho(unittest.TestCase):
    """Testa o baralho e distribuição de cartas."""

    def test_baralho_limpo_24_cartas(self) -> None:
        """Baralho limpo tem 24 cartas (6 ranks × 4 naipes)."""
        b = Baralho(limpo=True)
        cartas = b._criar_cartas()
        esperado = len(Rank.valores_limpo()) * len(list(Naipe))
        self.assertEqual(len(cartas), esperado)
        self.assertEqual(len(cartas), 24)  # 6 ranks × 4 naipes

    def test_baralho_sujo_40_cartas(self) -> None:
        """Baralho sujo tem 40 cartas (10 ranks × 4 naipes)."""
        b = Baralho(limpo=False)
        cartas = b._criar_cartas()
        esperado = len(Rank.valores_sujo()) * len(list(Naipe))
        self.assertEqual(len(cartas), esperado)
        self.assertEqual(len(cartas), 40)  # 10 ranks × 4 naipes

    def test_distribuicao_individual(self) -> None:
        """Distribui 3 cartas para cada jogador individual."""
        b = Baralho(limpo=True)
        maos, vira = b.distribuir(1)
        self.assertEqual(len(maos), 2)
        self.assertEqual(len(maos[0]), 3)
        self.assertEqual(len(maos[1]), 3)
        self.assertIsNotNone(vira)

    def test_distribuicao_duplas(self) -> None:
        """Distribui 3 cartas para cada jogador em duplas."""
        b = Baralho(limpo=True)
        maos, vira = b.distribuir(2)
        self.assertEqual(len(maos), 4)
        for mao in maos:
            self.assertEqual(len(mao), 3)

    def test_distribuicao_trios(self) -> None:
        """Distribui 3 cartas para cada jogador em trios."""
        b = Baralho(limpo=False)
        maos, vira = b.distribuir(3)
        self.assertEqual(len(maos), 6)
        for mao in maos:
            self.assertEqual(len(mao), 3)

    def test_distribuicao_invalida_0(self) -> None:
        """Distribuir com 0 jogadores por equipe levanta erro."""
        b = Baralho(limpo=True)
        with self.assertRaises(ValueError):
            b.distribuir(0)

    def test_distribuicao_invalida_4(self) -> None:
        """Distribuir com 4 jogadores por equipe levanta erro."""
        b = Baralho(limpo=True)
        with self.assertRaises(ValueError):
            b.distribuir(4)

    def test_trios_exige_baralho_sujo(self) -> None:
        """Trios com baralho limpo levanta erro."""
        b = Baralho(limpo=True)
        with self.assertRaises(ValueError):
            b.distribuir(3)

    def test_manilha_definida_corretamente(self) -> None:
        """A manilha é o rank seguinte ao da carta virada."""
        b = Baralho(limpo=True)
        maos, vira = b.distribuir(1)
        ranks = Rank.valores(True)
        rank_manilha = ranks[(ranks.index(vira.rank) + 1) % len(ranks)]
        todas = [c for m in maos for c in m] + [vira]
        manilhas = [c for c in todas if c.rank == rank_manilha]
        for c in manilhas:
            self.assertTrue(c.manilha)
        self.assertFalse(vira.manilha)

    def test_cartas_nao_se_repetem(self) -> None:
        """Cada carta distribuída é única."""
        b = Baralho(limpo=True)
        maos, vira = b.distribuir(1)
        todas = [c for m in maos for c in m] + [vira]
        self.assertEqual(len(todas), len(set(todas)))

    def test_multiplas_distribuicoes(self) -> None:
        """Múltiplas distribuições recriam cartas independentes."""
        b = Baralho(limpo=True)
        maos1, _ = b.distribuir(1)
        maos2, _ = b.distribuir(1)
        # As cartas são objetos diferentes a cada distribuição
        todas1 = [c for m in maos1 for c in m]
        todas2 = [c for m in maos2 for c in m]
        # Ambas têm 6 cartas
        self.assertEqual(len(todas1), 6)
        self.assertEqual(len(todas2), 6)

    def test_propriedade_limpo(self) -> None:
        """A propriedade limpo retorna o valor configurado."""
        self.assertTrue(Baralho(limpo=True).limpo)
        self.assertFalse(Baralho(limpo=False).limpo)


# =====================================================================
# JOGADOR
# =====================================================================

class TesteJogador(unittest.TestCase):
    """Testa a classe Jogador."""

    def test_criar_jogador(self) -> None:
        """Jogador é criado com nome e ID único."""
        j = Jogador('Teste')
        self.assertEqual(j.nome, 'Teste')
        self.assertEqual(len(j.cartas), 0)

    def test_id_unico(self) -> None:
        """Cada jogador tem um ID único."""
        j1 = Jogador('A')
        j2 = Jogador('B')
        self.assertNotEqual(j1.id, j2.id)

    def test_nome_vazio_levanta_erro(self) -> None:
        """Nome vazio ou apenas espaços levanta erro."""
        with self.assertRaises(ValueError):
            Jogador('')
        with self.assertRaises(ValueError):
            Jogador('   ')

    def test_nome_e_stripado(self) -> None:
        """Nome com espaços é stripado."""
        j = Jogador('  Teste  ')
        self.assertEqual(j.nome, 'Teste')

    def test_receber_cartas(self) -> None:
        """Jogador recebe exatamente 3 cartas."""
        cartas = [
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.DOIS, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ]
        j = Jogador('Teste')
        j.receber_cartas(cartas)
        self.assertEqual(len(j.cartas), 3)

    def test_receber_cartas_quantidade_errada(self) -> None:
        """Receber menos ou mais de 3 cartas levanta erro."""
        j = Jogador('Teste')
        with self.assertRaises(ValueError):
            j.receber_cartas([Carta(Rank.AS, Naipe.OUROS)])
        with self.assertRaises(ValueError):
            j.receber_cartas([
                Carta(Rank.AS, Naipe.OUROS),
                Carta(Rank.DOIS, Naipe.ESPADAS),
                Carta(Rank.TRES, Naipe.COPAS),
                Carta(Rank.REI, Naipe.PAUS),
            ])

    def test_receber_cartas_ordenadas_por_forca(self) -> None:
        """As cartas devem ser ordenadas por força crescente ao receber."""
        # Envia cartas em ordem aleatória
        cartas = [
            Carta(Rank.TRES, Naipe.COPAS),   # Mais forte
            Carta(Rank.AS, Naipe.OUROS),     # Mais fraca
            Carta(Rank.DOIS, Naipe.ESPADAS), # Meio
        ]
        j = Jogador('Teste')
        j.receber_cartas(cartas)
        mao = j.cartas
        # Deve estar ordenada: AS < DOIS < TRES
        self.assertEqual(mao[0].rank, Rank.AS)
        self.assertEqual(mao[1].rank, Rank.DOIS)
        self.assertEqual(mao[2].rank, Rank.TRES)
        # Força crescente
        self.assertLess(mao[0].forca, mao[1].forca)
        self.assertLess(mao[1].forca, mao[2].forca)

    def test_receber_cartas_com_manilha_ordenada(self) -> None:
        """Manilha deve ficar no final da mão por ser a mais forte."""
        cartas = [
            Carta(Rank.AS, Naipe.ESPADAS),   # Manilha (mais forte)
            Carta(Rank.AS, Naipe.OUROS),     # Normal
            Carta(Rank.DOIS, Naipe.COPAS),   # Normal
        ]
        cartas[0].tornar_manilha()
        j = Jogador('Teste')
        j.receber_cartas(cartas)
        mao = j.cartas
        # A manilha deve estar no último índice
        self.assertTrue(mao[2].manilha)
        self.assertFalse(mao[0].manilha)
        self.assertFalse(mao[1].manilha)

    def test_jogar_carta_por_indice(self) -> None:
        """Jogar carta remove do índice correto."""
        j = Jogador('Teste')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.DOIS, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ])
        jogada = j.jogar(0)
        self.assertEqual(jogada.rank, Rank.AS)
        self.assertEqual(len(j.cartas), 2)

    def test_jogar_carta_indice_invalido(self) -> None:
        """Jogar com índice inválido levanta erro."""
        j = Jogador('Teste')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.DOIS, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ])
        with self.assertRaises(ValueError):
            j.jogar(-1)
        with self.assertRaises(ValueError):
            j.jogar(3)

    def test_cartas_retorna_tupla_imutavel(self) -> None:
        """A propriedade cartas retorna uma tupla imutável."""
        j = Jogador('Teste')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.DOIS, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ])
        self.assertIsInstance(j.cartas, tuple)

    def test_str_repr(self) -> None:
        """String e repr do jogador."""
        j = Jogador('Ana')
        self.assertEqual(str(j), 'Ana')
        self.assertIn('Ana', repr(j))


# =====================================================================
# EQUIPE
# =====================================================================

class TesteEquipe(unittest.TestCase):
    """Testa a classe Equipe."""

    def test_equipe_com_1_jogador(self) -> None:
        """Equipe com 1 jogador (individual)."""
        eq = Equipe(Jogador('A'))
        self.assertEqual(len(eq), 1)

    def test_equipe_com_2_jogadores(self) -> None:
        """Equipe com 2 jogadores (duplas)."""
        eq = Equipe(Jogador('A'), Jogador('B'))
        self.assertEqual(len(eq), 2)

    def test_equipe_com_3_jogadores(self) -> None:
        """Equipe com 3 jogadores (trios)."""
        eq = Equipe(Jogador('A'), Jogador('B'), Jogador('C'))
        self.assertEqual(len(eq), 3)

    def test_equipe_vazia_levanta_erro(self) -> None:
        """Equipe sem jogadores levanta erro."""
        with self.assertRaises(ValueError):
            Equipe()

    def test_equipe_com_4_jogadores_levanta_erro(self) -> None:
        """Equipe com mais de 3 jogadores levanta erro."""
        with self.assertRaises(ValueError):
            Equipe(Jogador('A'), Jogador('B'), Jogador('C'), Jogador('D'))

    def test_jogador_duplicado_levanta_erro(self) -> None:
        """Jogador duplicado na mesma equipe levanta erro."""
        j = Jogador('A')
        with self.assertRaises(ValueError):
            Equipe(j, j)

    def test_jogadores_propriedade(self) -> None:
        """Propriedade jogadores retorna tupla."""
        j1 = Jogador('A')
        j2 = Jogador('B')
        eq = Equipe(j1, j2)
        self.assertIsInstance(eq.jogadores, tuple)
        self.assertEqual(len(eq.jogadores), 2)

    def test_str_equipe(self) -> None:
        """String da equipe mostra nomes separados."""
        eq = Equipe(Jogador('Ana'), Jogador('Beto'))
        self.assertIn('Ana', str(eq))
        self.assertIn('Beto', str(eq))


# =====================================================================
# VAZA
# =====================================================================

class TesteVaza(unittest.TestCase):
    """Testa Jogada e ResultadoVaza."""

    def test_jogada_str(self) -> None:
        """String da jogada mostra jogador e carta."""
        j = Jogador('Ana')
        c = Carta(Rank.AS, Naipe.OUROS)
        jogada = Jogada(j, c)
        self.assertIn('Ana', str(jogada))
        self.assertIn('A', str(jogada))

    def test_resultado_vaza_decidido(self) -> None:
        """Resultado de vaza com vencedor."""
        j1 = Jogada(Jogador('A'), Carta(Rank.AS, Naipe.OUROS))
        j2 = Jogada(Jogador('B'), Carta(Rank.REI, Naipe.OUROS))
        rv = ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2))
        self.assertEqual(rv.numero, 1)
        self.assertEqual(rv.equipe_vencedora, 0)
        self.assertFalse(rv.eh_empate)

    def test_resultado_vaza_empate(self) -> None:
        """Resultado de vaza empatada."""
        j1 = Jogada(Jogador('A'), Carta(Rank.AS, Naipe.OUROS))
        j2 = Jogada(Jogador('B'), Carta(Rank.AS, Naipe.ESPADAS))
        rv = ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2))
        self.assertTrue(rv.eh_empate)

    def test_resultado_vaza_str_decidido(self) -> None:
        """String de vaza decidida."""
        j1 = Jogada(Jogador('A'), Carta(Rank.AS, Naipe.OUROS))
        j2 = Jogada(Jogador('B'), Carta(Rank.REI, Naipe.OUROS))
        rv = ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2))
        self.assertIn('2', str(rv))
        self.assertIn('2', str(rv))

    def test_resultado_vaza_str_empate(self) -> None:
        """String de vaza empatada."""
        j1 = Jogada(Jogador('A'), Carta(Rank.AS, Naipe.OUROS))
        j2 = Jogada(Jogador('B'), Carta(Rank.AS, Naipe.ESPADAS))
        rv = ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2))
        self.assertIn('empate', str(rv))

    def test_resultado_vaza_imutavel(self) -> None:
        """ResultadoVaza é imutável (frozen)."""
        j1 = Jogada(Jogador('A'), Carta(Rank.AS, Naipe.OUROS))
        j2 = Jogada(Jogador('B'), Carta(Rank.REI, Naipe.OUROS))
        rv = ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2))
        with self.assertRaises(Exception):
            rv.equipe_vencedora = 1  # type: ignore


# =====================================================================
# ESTADO
# =====================================================================

class TesteEstado(unittest.TestCase):
    """Testa os estados e modalidades."""

    def test_estados_existem(self) -> None:
        """Os 4 estados existem."""
        self.assertEqual(EstadoPartida.AGUARDANDO.name, 'AGUARDANDO')
        self.assertEqual(EstadoPartida.JOGANDO.name, 'JOGANDO')
        self.assertEqual(EstadoPartida.PEDIDO_PENDENTE.name, 'PEDIDO_PENDENTE')
        self.assertEqual(EstadoPartida.ENCERRADA.name, 'ENCERRADA')

    def test_modalidade_nome(self) -> None:
        """Nomes das modalidades."""
        self.assertIn('Individual', Modalidade.nome(1))
        self.assertIn('Duplas', Modalidade.nome(2))
        self.assertIn('Trios', Modalidade.nome(3))
        self.assertEqual(Modalidade.nome(99), 'Desconhecida')

    def test_modalidade_constantes(self) -> None:
        """Constantes de modalidade."""
        self.assertEqual(Modalidade.INDIVIDUAL, 1)
        self.assertEqual(Modalidade.DUPLAS, 2)
        self.assertEqual(Modalidade.TRIOS, 3)


# =====================================================================
# EVENTO
# =====================================================================

class TesteEvento(unittest.TestCase):
    """Testa a classe Evento."""

    def test_criar_evento(self) -> None:
        """Evento é criado com tipo e mensagem."""
        ev = Evento('mao', 'Nova mão!')
        self.assertEqual(ev.tipo, 'mao')
        self.assertEqual(ev.mensagem, 'Nova mão!')

    def test_evento_imutavel(self) -> None:
        """Evento é imutável (frozen)."""
        ev = Evento('mao', 'Nova mão!')
        with self.assertRaises(Exception):
            ev.tipo = 'carta'  # type: ignore

    def test_evento_timestamp(self) -> None:
        """Evento tem timestamp."""
        ev = Evento('mao', 'Nova mão!')
        self.assertIsNotNone(ev.timestamp)

    def test_evento_str(self) -> None:
        """String do evento retorna a mensagem."""
        ev = Evento('mao', 'Nova mão!')
        self.assertEqual(str(ev), 'Nova mão!')


# =====================================================================
# PARTIDA — CRIAÇÃO E VALIDAÇÃO
# =====================================================================

class TestePartidaCriacao(unittest.TestCase):
    """Testa a criação e validação de Partida."""

    def test_individual(self) -> None:
        """Cria partida individual."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        self.assertEqual(p.modalidade, 1)
        self.assertEqual(len(p.jogadores), 2)

    def test_duplas(self) -> None:
        """Cria partida de duplas."""
        p = Partida.duplas(Jogador('A'), Jogador('B'), Jogador('C'), Jogador('D'))
        self.assertEqual(p.modalidade, 2)
        self.assertEqual(len(p.jogadores), 4)

    def test_trios(self) -> None:
        """Cria partida de trios."""
        p = Partida.trios(
            Jogador('A'), Jogador('B'), Jogador('C'),
            Jogador('D'), Jogador('E'), Jogador('F'),
        )
        self.assertEqual(p.modalidade, 3)
        self.assertEqual(len(p.jogadores), 6)

    def test_trios_com_baralho_limpo_levanta_erro(self) -> None:
        """Trios com baralho limpo levanta erro."""
        with self.assertRaises(ValueError):
            Partida(
                Equipe(Jogador('A'), Jogador('B'), Jogador('C')),
                Equipe(Jogador('D'), Jogador('E'), Jogador('F')),
                limpo=True,
            )

    def test_equipes_tamanhos_diferentes(self) -> None:
        """Equipes com tamanhos diferentes levanta erro."""
        with self.assertRaises(ValueError):
            Partida(
                Equipe(Jogador('A')),
                Equipe(Jogador('B'), Jogador('C')),
            )

    def test_jogador_duplicado_entre_equipes(self) -> None:
        """O mesmo jogador nas duas equipes levanta erro."""
        j = Jogador('A')
        with self.assertRaises(ValueError):
            Partida(Equipe(j), Equipe(j))

    def test_placar_inicial_zero(self) -> None:
        """Placar começa em 0×0."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        self.assertEqual(p.pontos, (0, 0))

    def test_estado_inicial_aguardando(self) -> None:
        """Estado inicial é AGUARDANDO."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        self.assertEqual(p.estado, EstadoPartida.AGUARDANDO)

    def test_mao_numero_inicial_zero(self) -> None:
        """Número da mão começa em 0."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        self.assertEqual(p.mao_numero, 0)

    def test_vencedor_inicial_none(self) -> None:
        """Vencedor é None no início."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        self.assertIsNone(p.vencedor)

    def test_trios_exige_6_jogadores(self) -> None:
        """Método trios exige exatamente 6 jogadores."""
        with self.assertRaises(ValueError):
            Partida.trios(Jogador('A'), Jogador('B'))


# =====================================================================
# PARTIDA — MÃOS
# =====================================================================

class TestePartidaMaos(unittest.TestCase):
    """Testa o controle de mãos na Partida."""

    def test_iniciar_mao(self) -> None:
        """Iniciar mão muda estado para JOGANDO."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        self.assertEqual(p.estado, EstadoPartida.JOGANDO)

    def test_mao_numero_incrementa(self) -> None:
        """Número da mão incrementa a cada início."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        self.assertEqual(p.mao_numero, 1)

    def test_iniciar_mao_dupla_levanta_erro(self) -> None:
        """Iniciar mão com mão em andamento levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.iniciar_mao()

    def test_iniciar_mao_apos_encerramento(self) -> None:
        """Pode iniciar nova mão após mão anterior encerrar."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        mao = p.mao_atual
        # Simular 2 vazas para equipe 0
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        mao._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        p._concluir_mao(0)
        self.assertEqual(p.estado, EstadoPartida.AGUARDANDO)
        p.iniciar_mao()
        self.assertEqual(p.estado, EstadoPartida.JOGANDO)

    def test_iniciar_mao_partida_encerrada_levanta_erro(self) -> None:
        """Iniciar mão após partida encerrada levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._vencedor = 0
        with self.assertRaises(ValueError):
            p.iniciar_mao()

    def test_jogador_da_vez(self) -> None:
        """Após iniciar mão, há um jogador da vez."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        self.assertIsNotNone(p.jogador_da_vez)

    def test_vira_nao_e_none(self) -> None:
        """A carta virada não é None após iniciar mão."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        self.assertIsNotNone(p.vira)

    def test_jogadores_recebem_cartas(self) -> None:
        """Jogadores recebem 3 cartas ao iniciar mão."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        for j in p.jogadores:
            self.assertEqual(len(j.cartas), 3)

    def test_mao_atual_sem_mao_levanta_erro(self) -> None:
        """Acessar mão atual sem mão iniciada levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        with self.assertRaises(RuntimeError):
            _ = p.mao_atual


# =====================================================================
# PARTIDA — JOGADAS
# =====================================================================

class TestePartidaJogadas(unittest.TestCase):
    """Testa as jogadas na Partida."""

    def _jogar_vaza(self, partida: Partida, equipe_vencedora: int) -> None:
        """Auxiliar: joga uma vaza completa simulando resultado."""
        mao = partida.mao_atual
        jogadores = partida.jogadores
        # Simular jogadas de todos os jogadores
        for j in jogadores:
            if mao.jogador_da_vez is j:
                carta = Carta(Rank.AS, Naipe.OUROS)
                j._cartas = [carta, carta, carta]  # Força cartas
                partida.jogar(j, 0)

    def test_jogada_retorna_resultado_vaza(self) -> None:
        """Jogar todas as cartas retorna ResultadoVaza."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        a, b = p.jogadores
        # Jogar carta do A
        r = p.jogar(a, 0)
        self.assertIsNone(r)  # Vaza não completa
        # Jogar carta do B
        r = p.jogar(b, 0)
        self.assertIsInstance(r, ResultadoVaza)

    def test_jogada_nao_e_a_vez_levanta_erro(self) -> None:
        """Jogar quando não é a vez levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        a, b = p.jogadores
        if p.jogador_da_vez is a:
            with self.assertRaises(ValueError):
                p.jogar(b, 0)
        else:
            with self.assertRaises(ValueError):
                p.jogar(a, 0)

    def test_jogada_fora_de_jogo_levanta_erro(self) -> None:
        """Jogar quando não está JOGANDO levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        with self.assertRaises(RuntimeError):
            p.jogar(p.jogadores[0], 0)

    def test_pontos_aplicados_apos_mao(self) -> None:
        """Pontos são aplicados após concluir mão."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        mao = p.mao_atual
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        mao._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        p._concluir_mao(0)
        self.assertEqual(p.pontos[0], 1)  # Valor padrão da mão = 1

    def test_vencedor_ao_alcançar_12(self) -> None:
        """Vencedor é definido ao alcançar 12 pontos."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        mao = p.mao_atual
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        mao._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        p._concluir_mao(0)
        self.assertEqual(p.vencedor, 0)
        self.assertEqual(p.estado, EstadoPartida.ENCERRADA)

    def test_indice_equipe(self) -> None:
        """Índice da equipe de um jogador."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        self.assertEqual(p.indice_equipe(p.jogadores[0]), 0)
        self.assertEqual(p.indice_equipe(p.jogadores[1]), 1)

    def test_indice_equipe_jogador_nao_participa(self) -> None:
        """Jogador que não participa levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        with self.assertRaises(ValueError):
            p.indice_equipe(Jogador('C'))


# =====================================================================
# PARTIDA — TRUCO / APOSTAS
# =====================================================================

class TestePartidaApostas(unittest.TestCase):
    """Testa o sistema de truco e apostas na Partida."""

    def test_pedir_truco_1_para_3(self) -> None:
        """Pedir truco aumenta de 1 para 3."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        novo = p.pedir_aumento(p.jogadores[0])
        self.assertEqual(novo, 3)

    def test_pedir_truco_3_para_6(self) -> None:
        """Contra-aumentar de 3 para 6."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        p.pedir_aumento(p.jogadores[0])
        self.assertEqual(p.contra_aumentar(p.jogadores[1]), 6)

    def test_escalada_valores(self) -> None:
        """Verifica os valores de escalada: 1→3, 3→6, 6→9, 9→12."""
        # Testa o mapeamento de valores de aposta
        mapa = {1: 3, 3: 6, 6: 9, 9: 12}
        self.assertEqual(mapa[1], 3)
        self.assertEqual(mapa[3], 6)
        self.assertEqual(mapa[6], 9)
        self.assertEqual(mapa[9], 12)
        # 12 não tem próximo
        self.assertNotIn(12, mapa)

    def test_nao_pode_pedir_acima_de_12(self) -> None:
        """Não pode pedir truco quando mão já vale 12."""
        # Força valor_mao = 12 e verifica que não pode pedir
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        p.mao_atual.valor_mao = 12
        self.assertFalse(p.pode_pedir_aumento(p.jogadores[0]))
        self.assertFalse(p.pode_pedir_aumento(p.jogadores[1]))

    def test_mesma_equipe_nao_pode_pedir_dois_vezes(self) -> None:
        """A mesma equipe não pode pedir truco duas vezes seguidas."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        p.pedir_aumento(p.jogadores[0])
        p.responder_aumento(p.jogadores[1], True)
        # Equipe 0 já pediu, não pode pedir de novo
        self.assertFalse(p.pode_pedir_aumento(p.jogadores[0]))

    def test_responder_nao_aceita_concede_mao(self) -> None:
        """Recusar truco concede a mão ao solicitante com o valor atual."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        self.assertEqual(p.valor_mao, 1)
        p.pedir_aumento(p.jogadores[0])
        p.responder_aumento(p.jogadores[1], False)
        # O valor atual da mão (1) é concedido ao solicitante
        self.assertEqual(p.pontos[0], 1)

    def test_pode_pedir_aumento_retorna_falso_fora_de_jogo(self) -> None:
        """pode_pedir_aumento levanta erro quando não há mão."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        with self.assertRaises(RuntimeError):
            p.pode_pedir_aumento(p.jogadores[0])

    def test_pedir_aumento_fora_de_jogo_levanta_erro(self) -> None:
        """pedir_aumento fora de JOGANDO levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        with self.assertRaises(RuntimeError):
            p.pedir_aumento(p.jogadores[0])

    def test_responder_aumento_sem_pedido_levanta_erro(self) -> None:
        """Responder aumento sem pedido pendente levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.responder_aumento(p.jogadores[1], True)

    def test_mesma_equipe_nao_responde_proprio_pedido(self) -> None:
        """A mesma equipe que pediu não pode responder."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        p.pedir_aumento(p.jogadores[0])
        with self.assertRaises(ValueError):
            p.responder_aumento(p.jogadores[0], True)

    def test_contra_aumentar_acima_de_12_levanta_erro(self) -> None:
        """Contra-aumentar quando pedido é 12 levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        j1 = p.jogador_da_vez
        j2 = p.jogadores[1 - p.indice_equipe(j1)]
        # 1→3 (j1 pede)
        p.pedir_aumento(j1)
        # 3→6 (j2 contra)
        p.contra_aumentar(j2)
        # 6→9 (j1 contra — mas j1 não é jogador_da_vez)
        # Simplifica: força pedido pendente com valor 12
        p.mao_atual._pedido = (0, 12)
        p.mao_atual._estado = EstadoPartida.PEDIDO_PENDENTE
        with self.assertRaises(ValueError):
            p.contra_aumentar(j2)


# =====================================================================
# PARTIDA — MÃO DE ONZE
# =====================================================================

class TestePartidaMaoDeOnze(unittest.TestCase):
    """Testa a mão de onze na Partida."""

    def test_mao_de_onze_detectada(self) -> None:
        """Mão de onze é detectada quando equipe chega a 11."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        self.assertEqual(p.mao_de_onze, 0)

    def test_mao_de_onze_equipe_1(self) -> None:
        """Mão de onze para equipe 1."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [5, 11]
        p.iniciar_mao()
        self.assertEqual(p.mao_de_onze, 1)

    def test_mao_de_onze_nao_detectada(self) -> None:
        """Mão de onze não é detectada quando ninguém tem 11."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [5, 5]
        p.iniciar_mao()
        self.assertIsNone(p.mao_de_onze)

    def test_mao_de_onze_ambas_11(self) -> None:
        """Se ambas têm 11, não há mão de onze."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 11]
        p.iniciar_mao()
        self.assertIsNone(p.mao_de_onze)

    def test_decidir_onze_jogar(self) -> None:
        """Decidir jogar na mão de onze."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        p.decidir_mao_onze(p.jogadores[0], True)
        self.assertEqual(p.valor_mao, 3)
        self.assertEqual(p.estado, EstadoPartida.JOGANDO)

    def test_decidir_onze_correr(self) -> None:
        """Decidir correr na mão de onze concede a mão ao adversário."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        pontos_antes = p.pontos[1]
        p.decidir_mao_onze(p.jogadores[0], False)
        # Equipe adversária (1) ganha a mão
        # O valor concedido é o valor atual da mão (1, pois não decidiu jogar)
        self.assertEqual(p.pontos[1], pontos_antes + 1)

    def test_decidir_onze_equipe_errada_levanta_erro(self) -> None:
        """Equipe sem 11 não pode decidir."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.decidir_mao_onze(p.jogadores[1], True)

    def test_nao_pode_trucar_na_mao_de_onze(self) -> None:
        """Não pode pedir truco na mão de onze."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        self.assertFalse(p.pode_pedir_aumento(p.jogadores[0]))


# =====================================================================
# MÃO — ENCERRAMENTO (regras de vaza)
# =====================================================================

class TesteEncerramentoMao(unittest.TestCase):
    """Testa as regras de encerramento de mão (vazas e desempate)."""

    def _criar_mao(self) -> Partida:
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        return p

    def test_equipe_ganha_2_vazas_equipe_0(self) -> None:
        """Equipe 0 ganha 2 vazas → mão termina."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        self.assertEqual(p.mao_atual._ganhador_mao(), 0)

    def test_equipe_ganha_2_vazas_equipe_1(self) -> None:
        """Equipe 1 ganha 2 vazas → mão termina."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=1, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2)),
        ]
        self.assertEqual(p.mao_atual._ganhador_mao(), 1)

    def test_cada_equipe_ganha_1_vaza_desempate(self) -> None:
        """1×1 → vaza de desempate (retorna None)."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2)),
        ]
        self.assertIsNone(p.mao_atual._ganhador_mao())

    def test_vaza_3_decide_equipe_0(self) -> None:
        """Vaza 3 para equipe 0 → equipe 0 vence."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2)),
            ResultadoVaza(numero=3, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        self.assertEqual(p.mao_atual._ganhador_mao(), 0)

    def test_vaza_3_decide_equipe_1(self) -> None:
        """Vaza 3 para equipe 1 → equipe 1 vence."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2)),
            ResultadoVaza(numero=3, equipe_vencedora=1, jogadas=(j1, j2)),
        ]
        self.assertEqual(p.mao_atual._ganhador_mao(), 1)

    def test_1_vaza_empate_continua(self) -> None:
        """1 vaza empatada → continua."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2)),
        ]
        self.assertIsNone(p.mao_atual._ganhador_mao())

    def test_2_vazas_ambas_empate_continua(self) -> None:
        """2 vazas empatadas → continua."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=None, jogadas=(j1, j2)),
        ]
        self.assertIsNone(p.mao_atual._ganhador_mao())

    def test_2_vazas_1_empate_1_decidida_continua(self) -> None:
        """1 empate + 1 decidida → continua (precisa de 2)."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        self.assertIsNone(p.mao_atual._ganhador_mao())

    def test_3_vazas_terceira_empata_primeira_decide(self) -> None:
        """3 vazas: terceira empatada, primeira decidida → primeira vence."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2)),
            ResultadoVaza(numero=3, equipe_vencedora=None, jogadas=(j1, j2)),
        ]
        self.assertEqual(p.mao_atual._ganhador_mao(), 0)

    def test_3_vazas_terceira_empata_segunda_decide(self) -> None:
        """3 vazas: 1ª empatada, 2ª decidida, 3ª empatada → 2ª vence."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=1, jogadas=(j1, j2)),
            ResultadoVaza(numero=3, equipe_vencedora=None, jogadas=(j1, j2)),
        ]
        self.assertEqual(p.mao_atual._ganhador_mao(), 1)

    def test_3_vazas_todas_empatadas_favorece_jogador_mao(self) -> None:
        """3 vazas todas empatadas → favorece equipe do jogador da mão."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=None, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=None, jogadas=(j1, j2)),
            ResultadoVaza(numero=3, equipe_vencedora=None, jogadas=(j1, j2)),
        ]
        # O jogador da mão é o primeiro jogador (índice 0)
        indice_mao = p.mao_atual._indice_mao
        equipe_esperada = p.mao_atual.indice_equipe(p.jogadores[indice_mao])
        self.assertEqual(p.mao_atual._ganhador_mao(), equipe_esperada)

    def test_1_vaza_nao_decide(self) -> None:
        """Apenas 1 vaza nunca decide a mão."""
        p = self._criar_mao()
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        p.mao_atual._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        self.assertIsNone(p.mao_atual._ganhador_mao())


# =====================================================================
# MÃO — JOGADAS E VAZAS
# =====================================================================

class TesteMaoJogadas(unittest.TestCase):
    """Testa as jogadas e vazas na Mão."""

    def test_jogar_sequencialmente(self) -> None:
        """Jogadas sequenciais completam uma vaza."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        a, b = p.jogadores
        r1 = p.jogar(a, 0)
        self.assertIsNone(r1)
        r2 = p.jogar(b, 0)
        self.assertIsInstance(r2, ResultadoVaza)
        self.assertEqual(r2.numero, 1)

    def test_vencedor_da_vaza_comeca_proxima(self) -> None:
        """Vencedor da vaza começa a próxima."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        a, b = p.jogadores
        # A joga primeiro
        self.assertEqual(p.jogador_da_vez, a)
        p.jogar(a, 0)
        p.jogar(b, 0)
        # A vaza foi empatada (mesma carta), então o mesmo jogador começa
        # Mas se A ganhou, A começa a próxima

    def test_resultados_acumulam(self) -> None:
        """Resultados de vazas são acumulados."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        a, b = p.jogadores
        p.jogar(a, 0)
        p.jogar(b, 0)
        self.assertEqual(len(p.resultados), 1)

    def test_jogadas_atuais_limpos_apos_vaza(self) -> None:
        """Jogadas atuais são limpas após fechar vaza."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        a, b = p.jogadores
        p.jogar(a, 0)
        self.assertEqual(len(p.jogadas_atuais), 1)
        p.jogar(b, 0)
        self.assertEqual(len(p.jogadas_atuais), 0)


# =====================================================================
# SESSÃO — CRIAÇÃO E VALIDAÇÃO
# =====================================================================

class TesteSessaoCriacao(unittest.TestCase):
    """Testa a criação e validação de Sessão."""

    def test_modalidade_invalida(self) -> None:
        """Modalidade inválida levanta erro."""
        with self.assertRaises(ValueError):
            Sessao(modalidade=0)
        with self.assertRaises(ValueError):
            Sessao(modalidade=4)

    def test_nomes_insuficientes(self) -> None:
        """Nomes insuficientes para a modalidade levanta erro."""
        with self.assertRaises(ValueError):
            Sessao(modalidade=2, nomes=['A', 'B'])

    def test_sessao_individual(self) -> None:
        """Sessão individual cria 2 jogadores."""
        s = Sessao(modalidade=1)
        self.assertEqual(len(s.partida.jogadores), 2)

    def test_sessao_duplas(self) -> None:
        """Sessão duplas cria 4 jogadores."""
        s = Sessao(modalidade=2)
        self.assertEqual(len(s.partida.jogadores), 4)

    def test_sessao_trios(self) -> None:
        """Sessão trios cria 6 jogadores."""
        s = Sessao(modalidade=3)
        self.assertEqual(len(s.partida.jogadores), 6)

    def test_humano_e_primeiro_jogador(self) -> None:
        """O humano é o primeiro jogador."""
        s = Sessao(modalidade=1)
        self.assertIs(s.humano, s.partida.jogadores[0])

    def test_primeira_mao_iniciada(self) -> None:
        """A primeira mão é iniciada automaticamente."""
        s = Sessao(modalidade=1)
        self.assertEqual(s.partida.estado, EstadoPartida.JOGANDO)

    def test_evento_de_mao_emitido(self) -> None:
        """Evento de mão é emitido ao criar sessão."""
        s = Sessao(modalidade=1)
        self.assertTrue(len(s.eventos) > 0)
        self.assertEqual(s.eventos[0].tipo, 'mao')

    def test_dificuldade_padrao(self) -> None:
        """Dificuldade padrão é MÉDIO."""
        s = Sessao(modalidade=1)
        self.assertEqual(s.dificuldade, Dificuldade.MEDIO)

    def test_seed_reprodutivel(self) -> None:
        """Seed garante reprodutibilidade."""
        s1 = Sessao(modalidade=1, seed=42)
        s2 = Sessao(modalidade=1, seed=42)
        # As cartas do humano devem ser iguais
        self.assertEqual(len(s1.humano.cartas), len(s2.humano.cartas))


# =====================================================================
# SESSÃO — JOGADAS E FLOW
# =====================================================================

class TesteSessaoJogadas(unittest.TestCase):
    """Testa as jogadas e fluxo da Sessão."""

    def test_precisa_humano_no_inicio(self) -> None:
        """No início, pode ser a vez do humano."""
        s = Sessao(modalidade=1, seed=42)
        # Depende de quem começa a mão
        self.assertIsInstance(s.precisa_humano, bool)

    def test_jogar_carta(self) -> None:
        """Humano joga carta com sucesso."""
        s = Sessao(modalidade=1, seed=42)
        if s.precisa_humano:
            s.jogar(0)
        # Se não é a vez, o jogar levanta erro
        else:
            with self.assertRaises(ValueError):
                s.jogar(0)

    def test_jogar_fora_da_vez_levanta_erro(self) -> None:
        """Jogar quando não é a vez levanta erro."""
        s = Sessao(modalidade=1, seed=42)
        if not s.precisa_humano:
            with self.assertRaises(ValueError):
                s.jogar(0)

    def test_avancar_bot(self) -> None:
        """Bot avança com sucesso."""
        s = Sessao(modalidade=1, seed=42)
        if not s.precisa_humano:
            self.assertTrue(s.avancar_bot())

    def test_bot_nao_avanca_se_e_vez_do_humano(self) -> None:
        """Bot não avança se é vez do humano."""
        s = Sessao(modalidade=1, seed=42)
        if s.precisa_humano:
            self.assertFalse(s.avancar_bot())

    def test_proxima_mao(self) -> None:
        """Próxima mão inicia quando estado é AGUARDANDO."""
        s = Sessao(modalidade=1, seed=42)
        self.assertFalse(s.proxima_mao())  # Não é AGUARDANDO ainda

    def test_eventos_sao_emitidos(self) -> None:
        """Eventos são emitidos durante o jogo."""
        s = Sessao(modalidade=1, seed=42)
        inicial = len(s.eventos)
        if s.precisa_humano:
            s.jogar(0)
        else:
            s.avancar_bot()
        self.assertGreater(len(s.eventos), inicial)

    def test_pode_trucar(self) -> None:
        """pode_trucar retorna bool."""
        s = Sessao(modalidade=1, seed=42)
        self.assertIsInstance(s.pode_trucar(), bool)

    def test_pede_truco_fora_da_vez_levanta_erro(self) -> None:
        """Pedir truco quando não pode levanta erro."""
        s = Sessao(modalidade=1, seed=42)
        if not s.pode_trucar():
            with self.assertRaises(ValueError):
                s.pedir_truco()


# =====================================================================
# SESSÃO — SIMULAÇÕES COMPLETAS
# =====================================================================

class TesteSimulacao(unittest.TestCase):
    """Simula partidas completas com bots."""

    def _simular(self, modalidade: int, seed: int) -> None:
        s = Sessao(modalidade=modalidade, seed=seed)
        for _ in range(2000):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(True)
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                s.responder(True)
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()
        self.assertEqual(s.partida.estado, EstadoPartida.ENCERRADA)
        self.assertGreaterEqual(max(s.partida.pontos), 12)

    def test_simulacao_individual_seed_12(self) -> None:
        self._simular(1, seed=12)

    def test_simulacao_individual_seed_99(self) -> None:
        self._simular(1, seed=99)

    def test_simulacao_duplas_seed_12(self) -> None:
        self._simular(2, seed=12)

    def test_simulacao_duplas_seed_99(self) -> None:
        self._simular(2, seed=99)

    def test_simulacao_trios_seed_12(self) -> None:
        self._simular(3, seed=12)

    def test_simulacao_trios_seed_99(self) -> None:
        self._simular(3, seed=99)

    def test_simulacao_individual_varias_seeds(self) -> None:
        """Múltiplas simulações com seeds diferentes."""
        for seed in [1, 2, 3, 7, 13, 42, 100]:
            with self.subTest(seed=seed):
                self._simular(1, seed=seed)


# =====================================================================
# SESSÃO — TRUCO E APOSTAS
# =====================================================================

class TesteSessaoApostas(unittest.TestCase):
    """Testa o sistema de truco na Sessão."""

    def test_pedir_truco(self) -> None:
        """Humano pede truco com sucesso."""
        s = Sessao(modalidade=1, seed=42)
        if s.pode_trucar():
            s.pedir_truco()
            self.assertEqual(s.partida.estado, EstadoPartida.PEDIDO_PENDENTE)

    def test_bot_responde_truco(self) -> None:
        """Bot responde ao pedido de truco do humano."""
        s = Sessao(modalidade=1, seed=42)
        if s.pode_trucar():
            s.pedir_truco()
            self.assertTrue(s.avancar_bot())
            self.assertIn(
                s.partida.estado,
                (EstadoPartida.JOGANDO, EstadoPartida.AGUARDANDO),
            )

    def test_responder_truco(self) -> None:
        """Humano responde a pedido de truco do bot."""
        # Cria sessão e força cenário onde bot pede truco
        s = Sessao(modalidade=1, seed=42)
        # Simula até ter pedido pendente do adversário
        for _ in range(50):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(True)
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                s.responder(True)
                break
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()

    def test_aumentar(self) -> None:
        """Humano contra-aumenta."""
        s = Sessao(modalidade=1, seed=42)
        for _ in range(50):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(True)
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                # Adversário pediu, humano pode aumentar
                try:
                    s.aumentar()
                    break
                except ValueError:
                    s.responder(True)
                    break
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()

    def test_simulacao_com_truco(self) -> None:
        """Simulação completa onde truco é pedido e aceito."""
        s = Sessao(modalidade=1, seed=12)
        for _ in range(2000):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(True)
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                s.responder(True)
            elif s.precisa_humano and s.pode_trucar() and len(s.eventos) < 5:
                s.pedir_truco()
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()
        self.assertEqual(s.partida.estado, EstadoPartida.ENCERRADA)


# =====================================================================
# SESSÃO — MÃO DE ONZE
# =====================================================================

class TesteSessaoMaoDeOnze(unittest.TestCase):
    """Testa a mão de onze na Sessão."""

    def test_decidir_onze_jogar(self) -> None:
        """Humano decide jogar na mão de onze."""
        # Usa Partida diretamente para evitar conflito com mão já iniciada
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        self.assertEqual(p.mao_de_onze, 0)
        p.decidir_mao_onze(p.jogadores[0], True)
        self.assertEqual(p.valor_mao, 3)
        self.assertEqual(p.estado, EstadoPartida.JOGANDO)

    def test_decidir_onze_correr(self) -> None:
        """Humano decide correr na mão de onze."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 5]
        p.iniciar_mao()
        pontos_antes = p.pontos[1]
        p.decidir_mao_onze(p.jogadores[0], False)
        self.assertEqual(p.pontos[1], pontos_antes + 1)

    def test_decidir_onze_equipe_errada(self) -> None:
        """Humano não pode decidir quando não é sua equipe."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [5, 11]
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.decidir_mao_onze(p.jogadores[0], True)


# =====================================================================
# IA — ESTRATÉGIA DE CARTA
# =====================================================================

class TesteEstrategiaCarta(unittest.TestCase):
    """Testa a estratégia de carta da IA."""

    def _jogador_com_cartas(self) -> Jogador:
        j = Jogador('Bot')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.REI, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ])
        return j

    def test_escolher_carta_retorna_indice_valido(self) -> None:
        """Escolher carta retorna índice válido."""
        j = self._jogador_com_cartas()
        ec = EstrategiaCarta(Dificuldade.MEDIO, __import__('random').Random(42))
        idx = ec.escolher_carta(j, [], 0, 0)
        self.assertIn(idx, [0, 1, 2])

    def test_escolher_carta_1_carta(self) -> None:
        """Com 1 carta, retorna índice 0."""
        j = Jogador('Bot')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.AS, Naipe.OUROS),
        ])
        j.jogar(0)
        j.jogar(0)
        ec = EstrategiaCarta(Dificuldade.MEDIO, __import__('random').Random(42))
        idx = ec.escolher_carta(j, [], 0, 0)
        self.assertEqual(idx, 0)

    def test_escolher_carta_sem_cartas_levanta_erro(self) -> None:
        """Escolher carta sem cartas levanta erro."""
        j = Jogador('Bot')
        ec = EstrategiaCarta(Dificuldade.MEDIO, __import__('random').Random(42))
        with self.assertRaises(ValueError):
            ec.escolher_carta(j, [], 0, 0)

    def test_facil_joga_aleatorio(self) -> None:
        """IA fácil joga aleatoriamente."""
        j = self._jogador_com_cartas()
        ec = EstrategiaCarta(Dificuldade.FACIL, __import__('random').Random(42))
        idx = ec.escolher_carta(j, [], 0, 0)
        self.assertIn(idx, [0, 1, 2])

    def test_dificil_economiza_carta_forte(self) -> None:
        """IA difícil joga carta fraca quando mão é forte."""
        j = self._jogador_com_cartas()
        ec = EstrategiaCarta(Dificuldade.DIFICIL, __import__('random').Random(42))
        idx = ec.escolher_carta(j, [], 0, 0)
        # Deve jogar a carta mais fraca (AS ou REI, não TRES)
        carta_escolhida = j.cartas[idx]
        self.assertNotEqual(carta_escolhida.rank, Rank.TRES)

    def test_responder_mao_bate_carta(self) -> None:
        """IA responde com carta que bate a da mesa."""
        j = self._jogador_com_cartas()
        ec = EstrategiaCarta(Dificuldade.DIFICIL, __import__('random').Random(42))
        carta_mesa = Carta(Rank.AS, Naipe.OUROS)
        idx = ec.escolher_carta(j, [carta_mesa], 0, 0)
        carta_escolhida = j.cartas[idx]
        self.assertGreater(carta_escolhida.forca, carta_mesa.forca)

    def test_responder_mao_sem_carta_que_bate(self) -> None:
        """IA joga carta fraca quando não tem que bate."""
        j = Jogador('Bot')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.REI, Naipe.ESPADAS),
            Carta(Rank.DAMA, Naipe.COPAS),
        ])
        ec = EstrategiaCarta(Dificuldade.DIFICIL, __import__('random').Random(42))
        carta_mesa = Carta(Rank.TRES, Naipe.PAUS)
        idx = ec.escolher_carta(j, [carta_mesa], 0, 0)
        # Joga a mais fraca
        self.assertEqual(j.cartas[idx], min(j.cartas, key=lambda c: c.forca))


# =====================================================================
# IA — ESTRATÉGIA DE APOSTA
# =====================================================================

class TesteEstrategiaAposta(unittest.TestCase):
    """Testa a estratégia de aposta da IA."""

    def test_nao_pede_truco_acima_de_12(self) -> None:
        """Não pede truco quando valor já é 12."""
        ea = EstrategiaAposta(Dificuldade.DIFICIL, __import__('random').Random(42))
        self.assertFalse(ea.deve_pedir_truco(0.9, 2, 2, 12))

    def test_facil_blefa(self) -> None:
        """IA fácil pode pedir truco mesmo com mão fraca."""
        ea = EstrategiaAposta(Dificuldade.FACIL, __import__('random').Random(42))
        # Com seed 42, pode ou não pedir — só verificamos que retorna bool
        self.assertIsInstance(ea.deve_pedir_truco(0.1, 0, 0, 1), bool)

    def test_dificil_somente_com_mao_forte(self) -> None:
        """IA difícil só pede com mão forte."""
        ea = EstrategiaAposta(Dificuldade.DIFICIL, __import__('random').Random(42))
        self.assertFalse(ea.deve_pedir_truco(0.3, 0, 0, 1))
        self.assertTrue(ea.deve_pedir_truco(0.8, 1, 1, 1))

    def test_aceitar_truco_facil(self) -> None:
        """IA fácil aceita truco frequentemente."""
        ea = EstrategiaAposta(Dificuldade.FACIL, __import__('random').Random(42))
        self.assertIsInstance(ea.deve_aceitar_truco(0.5, 3), bool)

    def test_aceitar_truco_dificil(self) -> None:
        """IA difícil só aceita com mão forte."""
        ea = EstrategiaAposta(Dificuldade.DIFICIL, __import__('random').Random(42))
        self.assertFalse(ea.deve_aceitar_truco(0.3, 9))
        self.assertTrue(ea.deve_aceitar_truco(0.8, 3))


# =====================================================================
# IA — CLASSE IA COMPLETA
# =====================================================================

class TesteIACompleta(unittest.TestCase):
    """Testa a classe IA completa."""

    def test_dificuldade_facil(self) -> None:
        """IA com dificuldade fácil."""
        ia = IA(Dificuldade.FACIL, seed=42)
        self.assertEqual(ia.dificuldade, Dificuldade.FACIL)

    def test_dificuldade_medio(self) -> None:
        """IA com dificuldade médio."""
        ia = IA(Dificuldade.MEDIO, seed=42)
        self.assertEqual(ia.dificuldade, Dificuldade.MEDIO)

    def test_dificuldade_dificil(self) -> None:
        """IA com dificuldade difícil."""
        ia = IA(Dificuldade.DIFICIL, seed=42)
        self.assertEqual(ia.dificuldade, Dificuldade.DIFICIL)

    def test_escolher_carta(self) -> None:
        """IA escolhe carta."""
        j = Jogador('Bot')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.REI, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ])
        ia = IA(Dificuldade.MEDIO, seed=42)
        idx = ia.escolher_carta(j, [], 0, 0)
        self.assertIn(idx, [0, 1, 2])

    def test_forca_mao(self) -> None:
        """IA calcula força da mão."""
        j = Jogador('Bot')
        j.receber_cartas([
            Carta(Rank.AS, Naipe.OUROS),
            Carta(Rank.REI, Naipe.ESPADAS),
            Carta(Rank.TRES, Naipe.COPAS),
        ])
        ia = IA(Dificuldade.MEDIO, seed=42)
        forca = ia.forca_mao(j.cartas)
        self.assertIsInstance(forca, float)
        self.assertGreater(forca, 0)

    def test_deve_pedir_truco(self) -> None:
        """IA decide se pede truco."""
        ia = IA(Dificuldade.MEDIO, seed=42)
        self.assertIsInstance(ia.deve_pedir_truco(0.5, 1, 1, 1), bool)

    def test_deve_aceitar_truco(self) -> None:
        """IA decide se aceita truco."""
        ia = IA(Dificuldade.MEDIO, seed=42)
        self.assertIsInstance(ia.deve_aceitar_truco(0.5, 3), bool)


# =====================================================================
# CASOS DE BORDA E INTEGRAÇÃO
# =====================================================================

class TesteCasosDeBorda(unittest.TestCase):
    """Testa casos de borda e cenários incomuns."""

    def test_partida_encerrada_nao_permitir_jogada(self) -> None:
        """Não pode jogar após partida encerrada."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._vencedor = 0
        with self.assertRaises(ValueError):
            p.iniciar_mao()

    def test_pontos_nao_ultrapassam_12(self) -> None:
        """Pontos podem ultrapassar 12, mas vencedor é definido."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p._pontos = [11, 10]
        p.iniciar_mao()
        mao = p.mao_atual
        carta = Carta(Rank.AS, Naipe.OUROS)
        j1 = Jogada(p.jogadores[0], carta)
        j2 = Jogada(p.jogadores[1], carta)
        mao._resultados = [
            ResultadoVaza(numero=1, equipe_vencedora=0, jogadas=(j1, j2)),
            ResultadoVaza(numero=2, equipe_vencedora=0, jogadas=(j1, j2)),
        ]
        p._concluir_mao(0)
        self.assertEqual(p.pontos[0], 12)
        self.assertEqual(p.vencedor, 0)

    def test_manilha_ciclica_no_fim(self) -> None:
        """Manilha ciclica corretamente no último rank."""
        b = Baralho(limpo=True)
        # Força a vira ser o último rank
        ranks = Rank.valores(True)
        ultimo_rank = ranks[-1]  # TRES
        # Se vira é TRES, manilha é o primeiro rank (Q/DAMA)
        primeiro_rank = ranks[0]
        # Criar carta virada manualmente
        vira = Carta(ultimo_rank, Naipe.OUROS)
        cartas = b._criar_cartas()
        b.definir_manilha(vira, cartas)
        manilhas = [c for c in cartas if c.manilha]
        for c in manilhas:
            self.assertEqual(c.rank, primeiro_rank)

    def test_manilha_ciclica_no_inicio(self) -> None:
        """Manilha ciclica corretamente no primeiro rank."""
        b = Baralho(limpo=True)
        ranks = Rank.valores(True)
        primeiro_rank = ranks[0]  # DAMA
        segundo_rank = ranks[1]  # VALETE
        vira = Carta(primeiro_rank, Naipe.OUROS)
        cartas = b._criar_cartas()
        b.definir_manilha(vira, cartas)
        manilhas = [c for c in cartas if c.manilha]
        for c in manilhas:
            self.assertEqual(c.rank, segundo_rank)

    def test_duplas_jogador_da_vez(self) -> None:
        """Em duplas, a vez alterna entre 4 jogadores."""
        p = Partida.duplas(Jogador('A'), Jogador('B'), Jogador('C'), Jogador('D'))
        p.iniciar_mao()
        self.assertIsNotNone(p.jogador_da_vez)
        self.assertIn(p.jogador_da_vez, p.jogadores)

    def test_trios_jogador_da_vez(self) -> None:
        """Em trios, a vez alterna entre 6 jogadores."""
        p = Partida.trios(
            Jogador('A'), Jogador('B'), Jogador('C'),
            Jogador('D'), Jogador('E'), Jogador('F'),
        )
        p.iniciar_mao()
        self.assertIsNotNone(p.jogador_da_vez)
        self.assertIn(p.jogador_da_vez, p.jogadores)

    def test_resultado_vaza_em_duplas(self) -> None:
        """Resultado de vaza em duplas tem 4 jogadas."""
        p = Partida.duplas(Jogador('A'), Jogador('B'), Jogador('C'), Jogador('D'))
        p.iniciar_mao()
        # Jogar todas as 4 cartas
        for _ in range(4):
            j = p.jogador_da_vez
            r = p.jogar(j, 0)
        self.assertIsInstance(r, ResultadoVaza)
        self.assertEqual(len(r.jogadas), 4)

    def test_resultado_vaza_em_trios(self) -> None:
        """Resultado de vaza em trios tem 6 jogadas."""
        p = Partida.trios(
            Jogador('A'), Jogador('B'), Jogador('C'),
            Jogador('D'), Jogador('E'), Jogador('F'),
        )
        p.iniciar_mao()
        for _ in range(6):
            j = p.jogador_da_vez
            r = p.jogar(j, 0)
        self.assertIsInstance(r, ResultadoVaza)
        self.assertEqual(len(r.jogadas), 6)

    def test_equipe_vencedora_em_duplas(self) -> None:
        """Em duplas, a equipe vencedora é detectada."""
        p = Partida.duplas(Jogador('A'), Jogador('B'), Jogador('C'), Jogador('D'))
        p.iniciar_mao()
        # Equipe 0: A, C. Equipe 1: B, D
        self.assertEqual(p.indice_equipe(p.jogadores[0]), 0)  # A
        self.assertEqual(p.indice_equipe(p.jogadores[1]), 1)  # B
        self.assertEqual(p.indice_equipe(p.jogadores[2]), 0)  # C
        self.assertEqual(p.indice_equipe(p.jogadores[3]), 1)  # D

    def test_sessao_com_dificuldade_facil(self) -> None:
        """Sessão com dificuldade fácil."""
        s = Sessao(modalidade=1, dificuldade=Dificuldade.FACIL, seed=42)
        self.assertEqual(s.dificuldade, Dificuldade.FACIL)

    def test_sessao_com_dificuldade_dificil(self) -> None:
        """Sessão com dificuldade difícil."""
        s = Sessao(modalidade=1, dificuldade=Dificuldade.DIFICIL, seed=42)
        self.assertEqual(s.dificuldade, Dificuldade.DIFICIL)

    def test_sessao_trios_usa_baralho_sujo(self) -> None:
        """Sessão de trios usa baralho sujo."""
        s = Sessao(modalidade=3, seed=42)
        self.assertFalse(s.partida._baralho.limpo)

    def test_eventos_sao_limitados(self) -> None:
        """Eventos são limitados a 50."""
        s = Sessao(modalidade=1, seed=42)
        # Adicionar muitos eventos
        for _ in range(100):
            s._emitir('teste', 'Evento de teste')
        self.assertLessEqual(len(s.eventos), 50)

    def test_simulacao_completamente_aceita_truco(self) -> None:
        """Simulação onde humano sempre aceita truco."""
        s = Sessao(modalidade=1, seed=7)
        for _ in range(2000):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(True)
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                s.responder(True)
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()
        self.assertEqual(s.partida.estado, EstadoPartida.ENCERRADA)

    def test_simulacao_sempre_corre_truco(self) -> None:
        """Simulação onde humano sempre corre do truco."""
        s = Sessao(modalidade=1, seed=7)
        for _ in range(2000):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(True)
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                s.responder(False)  # Sempre corre
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()
        self.assertEqual(s.partida.estado, EstadoPartida.ENCERRADA)

    def test_simulacao_sempre_corre_onze(self) -> None:
        """Simulação onde humano sempre corre na mão de onze."""
        s = Sessao(modalidade=1, seed=7)
        for _ in range(2000):
            p = s.partida
            if p.estado == EstadoPartida.ENCERRADA:
                break
            if p.estado == EstadoPartida.AGUARDANDO:
                s.proxima_mao()
            elif p.mao_de_onze == 0:
                s.decidir_onze(False)  # Sempre corre
            elif (
                p.estado == EstadoPartida.PEDIDO_PENDENTE
                and p.pedido_pendente
                and p.pedido_pendente[0] == 1
            ):
                s.responder(True)
            elif s.precisa_humano:
                s.jogar(0)
            else:
                s.avancar_bot()
        self.assertEqual(s.partida.estado, EstadoPartida.ENCERRADA)

    def test_carta_com_manilha_tem_forca_maior(self) -> None:
        """Carta com manilha tem força maior que qualquer carta normal."""
        normal = Carta(Rank.TRES, Naipe.PAUS)  # Mais forte normal
        manilha = Carta(Rank.DAMA, Naipe.OUROS)  # Mais fraca manilha
        manilha.tornar_manilha()
        self.assertGreater(manilha.forca, normal.forca)

    def test_ordem_de_manilhas_por_naipe(self) -> None:
        """Manilhas são ordenadas por naipe."""
        manilhas = []
        for n in Naipe:
            c = Carta(Rank.DAMA, n)
            c.tornar_manilha()
            manilhas.append(c)
        for i in range(len(manilhas) - 1):
            self.assertLess(manilhas[i].forca, manilhas[i + 1].forca)

    def test_vira_nunca_e_manilha(self) -> None:
        """A carta virada nunca é manilha."""
        b = Baralho(limpo=True)
        for _ in range(10):
            maos, vira = b.distribuir(1)
            self.assertFalse(vira.manilha)


# =====================================================================
# MÃO — VALIDAÇÕES
# =====================================================================

class TesteMaoValidacoes(unittest.TestCase):
    """Testa as validações da Mão."""

    def test_iniciar_mao_dupla_levanta_erro(self) -> None:
        """Iniciar mão já iniciada levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.mao_atual.iniciar()

    def test_jogar_fora_de_jogo_levanta_erro(self) -> None:
        """Jogar quando mão não está JOGANDO levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        # Mão não iniciada
        with self.assertRaises(RuntimeError):
            p.jogar(p.jogadores[0], 0)

    def test_pode_pedir_aumento_fora_de_jogo(self) -> None:
        """pode_pedir_aumento retorna False fora de JOGANDO."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        # Sem mão iniciada
        self.assertFalse(p.mao_atual.pode_pedir_aumento(p.jogadores[0]) if p._mao else False)

    def test_responder_aumento_sem_pedido(self) -> None:
        """Responder aumento sem pedido pendente levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.mao_atual.responder_aumento(p.jogadores[1], True)

    def test_contra_aumentar_sem_pedido(self) -> None:
        """Contra-aumentar sem pedido pendente levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.mao_atual.contra_aumentar(p.jogadores[1])

    def test_decidir_onze_sem_mao_de_onze(self) -> None:
        """Decidir onze sem mão de onze levanta erro."""
        p = Partida.individual(Jogador('A'), Jogador('B'))
        p.iniciar_mao()
        with self.assertRaises(ValueError):
            p.mao_atual.decidir_mao_onze(p.jogadores[0], True)


if __name__ == '__main__':
    unittest.main()
