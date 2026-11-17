"""Interface visual: somente renderização, mouse, teclado e ritmo dos bots."""
import math
from pathlib import Path
import pygame
from aplicacao.sessao import Sessao
from dominio.truco import Estado

W, H = 1200, 780
BG = (8, 22, 25)
FELT = (17, 83, 70)
FELT2 = (12, 65, 58)
GOLD = (240, 196, 110)
CREAM = (250, 244, 229)
MUTED = (164, 187, 180)
RED = (187, 54, 64)
WHITE = (255, 253, 248)

class TelaTruco:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('TRUCO • Mesa Paulista')
        self.tela = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.assets = Path(__file__).resolve().parent.parent / 'assets'
        self.mesa_imagem = pygame.image.load(str(self.assets / 'mesa.png')).convert()
        self._imagens_cartas = {}
        self.fonte = pygame.font.SysFont('inter', 19)
        self.pequena = pygame.font.SysFont('inter', 15)
        self.media = pygame.font.SysFont('inter', 27, bold=True)
        self.grande = pygame.font.SysFont('georgia', 54, bold=True)
        self.carta_fonte = pygame.font.SysFont('dejavusans', 35, bold=True)
        self.suit_fonte = pygame.font.SysFont('dejavusans', 45)
        self.botoes = []
        self.sessao = None
        self.modalidade = 2
        self.limpo = True
        self.ultimo_bot = 0
        self.proxima = 0
        self.mensagem = ''
        self.inicio_mensagem = 0

    def texto(self, s, x, y, fonte=None, cor=CREAM, centro=False):
        surf = (fonte or self.fonte).render(str(s), True, cor)
        rect = surf.get_rect(center=(x, y)) if centro else surf.get_rect(topleft=(x, y))
        self.tela.blit(surf, rect)
        return rect

    def ret(self, rect, cor, raio=12, borda=0):
        pygame.draw.rect(self.tela, cor, rect, borda, border_radius=raio)

    def botao(self, titulo, rect, callback, ativo=True, destaque=False):
        r = pygame.Rect(rect)
        hover = ativo and r.collidepoint(pygame.mouse.get_pos())
        shadow = r.move(0, 4)
        pygame.draw.rect(self.tela, (6, 20, 23), shadow, border_radius=14)
        fundo = ((235, 194, 120) if hover else (210, 167, 99)) if destaque else ((51, 113, 105) if hover else (28, 75, 75))
        if not ativo:
            fundo = (32, 53, 54)
        pygame.draw.rect(self.tela, fundo, r, border_radius=14)
        pygame.draw.rect(self.tela, (248, 217, 156) if destaque else (75, 122, 112), r, 1, border_radius=14)
        self.texto(titulo, r.centerx, r.centery, self.fonte,
                   BG if destaque else (CREAM if ativo else (115, 136, 135)), True)
        if ativo:
            self.botoes.append((r, callback))

    def carta(self, carta, x, y, w=87, h=124, verso=False, clicavel=None, pequena=False):
        r = pygame.Rect(round(x), round(y), w, h)
        hovered = bool(clicavel and r.collidepoint(pygame.mouse.get_pos()))
        key = 'verso' if verso else f'{carta.rank.value}_{dict(zip("♦♠♥♣", "DSHC"))[carta.naipe.value]}'
        cache_key = (key, w, h)
        if cache_key not in self._imagens_cartas:
            original = pygame.image.load(str(self.assets / (key + '.png'))).convert_alpha()
            self._imagens_cartas[cache_key] = pygame.transform.smoothscale(original, (w, h))
        pygame.draw.rect(self.tela, (5, 27, 28), r.move(2, 7), border_radius=10)
        self.tela.blit(self._imagens_cartas[cache_key], r)
        if not verso and carta.manilha:
            pygame.draw.circle(self.tela, GOLD, (r.right - 11, r.y + 12), 10)
            self.texto('M', r.right - 11, r.y + 12, self.pequena, BG, True)
        if hovered:
            pygame.draw.rect(self.tela, GOLD, r, 2, border_radius=10)
        if clicavel:
            self.botoes.append((r, clicavel))
        return r

    def base(self):
        self.tela.blit(self.mesa_imagem, (0, 0))
        self.texto('TRUCO', 600, 44, self.grande, GOLD, True)
        self.texto('PAULISTA  •  MESA DE CARTAS', 600, 86, self.pequena, MUTED, True)

    def menu(self):
        self.base()
        self.ret(pygame.Rect(345, 185, 510, 432), (13, 47, 49), 24)
        pygame.draw.rect(self.tela, (92, 132, 113), (345, 185, 510, 432), 1, border_radius=24)
        self.texto('NOVA PARTIDA', 600, 229, self.media, GOLD, True)
        self.texto('Escolha como quer jogar', 600, 264, self.fonte, MUTED, True)
        for i, (nome, quantidade) in enumerate([('Individual',1), ('Duplas',2), ('Trios',3)]):
            self.botao(nome, (386+i*145, 306, 135, 51), lambda n=quantidade: self.selecionar(n), destaque=self.modalidade==quantidade)
        self.texto('TIPO DE BARALHO', 600, 399, self.pequena, MUTED, True)
        self.botao('Limpo · 24 cartas', (394, 422, 197, 49), lambda: self.tipo(True), ativo=self.modalidade!=3, destaque=self.limpo)
        self.botao('Sujo · 40 cartas', (606, 422, 197, 49), lambda: self.tipo(False), destaque=not self.limpo)
        if self.modalidade==3:
            self.texto('Trios utiliza obrigatoriamente o baralho sujo', 600, 492, self.pequena, GOLD, True)
        self.botao('COMEÇAR A JOGAR', (435, 530, 330, 58), self.comecar, destaque=True)
        self.texto('1 humano + adversários e parceiros controlados por bots', 600, 725, self.pequena, MUTED, True)

    def selecionar(self, n):
        self.modalidade=n
        if n==3: self.limpo=False

    def tipo(self, limpo):
        if self.modalidade!=3 or not limpo:
            self.limpo=limpo

    def comecar(self):
        self.sessao=Sessao(self.modalidade, self.limpo)
        self.ultimo_bot=pygame.time.get_ticks()
        self.proxima=0

    def aviso(self, mensagem):
        self.mensagem=mensagem
        self.inicio_mensagem=pygame.time.get_ticks()

    def agir(self, func, *args):
        try:
            func(*args)
            self.ultimo_bot=pygame.time.get_ticks()
        except ValueError as e:
            self.aviso(str(e))

    def jogo(self):
        self.base()
        s=self.sessao
        p=s.partida
        self.ret(pygame.Rect(24, 21, 215, 69), (18, 49, 49), 14)
        self.texto('SUA EQUIPE', 39, 31, self.pequena, MUTED)
        self.texto(str(p.pontos[0]), 45, 49, self.media, GOLD)
        self.texto('×', 106, 53, self.fonte, MUTED)
        self.texto(str(p.pontos[1]), 133, 49, self.media, CREAM)
        self.texto('ADVERSÁRIOS', 166, 31, self.pequena, MUTED)
        self.ret(pygame.Rect(966, 21, 210, 69), (18, 49, 49), 14)
        self.texto(f'MÃO {p.mao_numero}', 985, 33, self.fonte, CREAM)
        self.texto(f'VALE {p.valor_mao} PONTO(S)', 985, 60, self.pequena, GOLD)
        self.botao('MENU', (1093, 103, 82, 34), self.voltar)

        # Jogadores, assentos em torno da mesa, cartas dos bots ocultas.
        ordem=p.jogadores
        outros=[j for j in ordem if j is not s.humano]
        posicoes={1:[(600, 186)], 3:[(305, 229),(895,229),(600,172)], 5:[(285,244),(470,167),(730,167),(915,244),(600,340)]}[len(outros)]
        for j, (x,y) in zip(outros,posicoes):
            eq=p.indice_equipe(j)
            cor=GOLD if eq==0 else (228, 235, 226)
            pygame.draw.circle(self.tela, (14, 47, 48), (x,y), 30)
            pygame.draw.circle(self.tela, cor, (x,y), 30, 2)
            self.texto(j.nome[0],x,y,self.media,cor,True)
            self.texto(j.nome,x,y+42,self.pequena,cor,True)
            if p.jogador_da_vez is j:
                pygame.draw.circle(self.tela,GOLD,(x,y),35,2)
            n=len(j.cartas)
            for i in range(n):
                self.carta(None,x-(n*22)//2+i*22,y+55,36,52,verso=True)

        # Área central: vira, última vaza, cartas na mesa.
        self.texto('VIRA', 180, 336, self.pequena, MUTED, True)
        if p.vira: self.carta(p.vira, 137, 355, 86, 123)
        self.texto('MESA', 600, 339, self.pequena, MUTED, True)
        jogadas=p.jogadas if p.jogadas else (s.ultima_vaza.jogadas if s.ultima_vaza else ())
        n=len(jogadas)
        for i, jogada in enumerate(jogadas):
            x=600-(n*94)//2+i*94
            self.carta(jogada.carta,x,367,77,107,pequena=True)
            self.texto(jogada.jogador.nome[:9],x+39,487,self.pequena,CREAM,True)
        if not jogadas:
            self.texto('Aguardando primeira carta', 600, 423, self.fonte, MUTED, True)

        # Indicadores das vazas.
        for i in range(3):
            r=pygame.Rect(505+i*66, 530, 55, 27)
            resultado=p.resultados[i] if i<len(p.resultados) else None
            cor=GOLD if resultado and resultado.vencedor==0 else (189, 222, 209) if resultado and resultado.vencedor==1 else (63, 108, 101)
            self.ret(r,cor,7)
            self.texto(('E' if resultado.vencedor is None else str(resultado.vencedor+1)) if resultado else str(i+1),r.centerx,r.centery,self.pequena,BG if resultado else CREAM,True)

        # Sua mão.
        self.texto('SUAS CARTAS', 600, 583, self.pequena, GOLD, True)
        cartas=s.humano.cartas
        pode=s.precisa_humano
        largura=116
        inicio=600-(len(cartas)*largura)//2
        for i,c in enumerate(cartas):
            x=inicio+i*largura
            y=612-(9 if pode and pygame.Rect(x,612,98,139).collidepoint(pygame.mouse.get_pos()) else 0)
            self.carta(c,x,y,98,139,clicavel=(lambda n=i: self.agir(s.jogar,n)) if pode else None)
        self.texto('VOCÊ  •  EQUIPE 1', 600, 763, self.pequena, GOLD, True)
        self.botao('TRUCO!' if p.valor_mao==1 else {3:'SEIS!',6:'NOVE!',9:'DOZE!'}.get(p.valor_mao,'TRUCO!'), (866, 638, 160, 52), lambda:self.agir(s.pedir_truco), ativo=s.pode_trucar(), destaque=s.pode_trucar())
        self.texto('Sua vez!' if pode else 'Aguardando jogadores...', 600, 567, self.pequena, GOLD if pode else MUTED, True)

        # Log à direita.
        self.ret(pygame.Rect(980, 270, 183, 175), (10, 48, 47), 12)
        self.texto('ÚLTIMAS AÇÕES', 992, 283, self.pequena, GOLD)
        for i,e in enumerate(s.eventos[-5:][::-1]):
            msg=e.mensagem
            if len(msg)>23: msg=msg[:22]+'…'
            self.texto(msg,992,315+i*24,self.pequena,MUTED)

        if p.estado==Estado.ENCERRADA:
            self.dialogo('VITÓRIA!' if p.vencedor==0 else 'FIM DE JOGO', 'Sua equipe venceu!' if p.vencedor==0 else 'Os adversários venceram.', [('NOVA PARTIDA',self.voltar)])
        elif p.mao_de_onze==0:
            self.dialogo('MÃO DE ONZE', 'Sua equipe quer jogar valendo 3?', [('JOGAR',lambda:self.agir(s.decidir_onze,True)),('CORRER',lambda:self.agir(s.decidir_onze,False))])
        elif p.estado==Estado.PEDIDO_PENDENTE and p.pedido_pendente[0]==1:
            valor=p.pedido_pendente[1]
            opcoes=[('ACEITAR',lambda:self.agir(s.responder,True)),('CORRER',lambda:self.agir(s.responder,False))]
            if valor < 12:
                opcoes.append(('AUMENTAR',lambda:self.agir(s.aumentar)))
            self.dialogo(f'PEDIRAM {valor}!', 'Você aceita, corre ou aumenta a aposta?', opcoes)
        elif p.estado==Estado.PEDIDO_PENDENTE:
            self.dialogo('APOSTA NA MESA', 'Aguardando a resposta dos adversários...', [])
        elif p.estado==Estado.AGUARDANDO:
            self.dialogo('MÃO ENCERRADA', f'Placar: {p.pontos[0]} × {p.pontos[1]}', [('PRÓXIMA MÃO',lambda:self.agir(s.proxima_mao))])

        if self.mensagem and pygame.time.get_ticks()-self.inicio_mensagem<2700:
            self.ret(pygame.Rect(370,102,460,38),(120,51,49),8)
            self.texto(self.mensagem,600,121,self.pequena,WHITE,True)

    def dialogo(self,titulo,subtitulo,opcoes):
        camada=pygame.Surface((W,H),pygame.SRCALPHA)
        camada.fill((0,12,14,172))
        self.tela.blit(camada,(0,0))
        r=pygame.Rect(350,257,500,256)
        self.ret(r,(18,54,56),22)
        pygame.draw.rect(self.tela,GOLD,r,2,border_radius=22)
        self.texto(titulo,600,319,self.media,GOLD,True)
        self.texto(subtitulo,600,373,self.fonte,CREAM,True)
        for i,(nome,cb) in enumerate(opcoes):
            total=len(opcoes)
            largura=145 if total >= 3 else 190
            x=600-(total*largura+(total-1)*12)/2+i*(largura+12)
            self.botao(nome,(x,417,largura,54),cb,destaque=i==0)

    def voltar(self):
        self.sessao=None

    def executar(self):
        rodando = True
        while rodando:
            # Atualiza a lógica antes de desenhar o estado atual.
            if self.sessao:
                s = self.sessao
                p = s.partida
                agora = pygame.time.get_ticks()
                if (agora - self.ultimo_bot > 850
                        and p.estado not in (Estado.AGUARDANDO, Estado.ENCERRADA)):
                    if s.avancar_bot():
                        self.ultimo_bot = agora

            # Os elementos clicáveis devem ser registrados ANTES
            # de consultar os eventos de mouse desta iteração.
            self.botoes.clear()
            if self.sessao:
                self.jogo()
            else:
                self.menu()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.voltar()
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for rect, callback in reversed(self.botoes):
                        if rect.collidepoint(evento.pos):
                            callback()
                            break

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
