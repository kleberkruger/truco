from enum import Enum
import random

class Rank(Enum):
    QUATRO = '4'
    CINCO = '5'
    SEIS = '6'
    SETE = '7'
    VALETE = 'J'
    DAMA = 'Q'
    REI = 'K'
    AS = 'A'
    DOIS = '2'
    TRES = '3'

    @property
    def forca(self):
        return list(type(self)).index(self)
    
    @classmethod
    def baralho_sujo(cls):
        return list(cls)
    
    @classmethod
    def baralho_limpo(cls):
        return [
            rank for rank in cls
            if rank not in {
                cls.QUATRO,
                cls.CINCO,
                cls.SEIS,
                cls.SETE
            }
        ]

    def __str__(self):
        return self.value
    
    
class Naipe(Enum):
    OUROS = '♦'
    ESPADAS = '♠'
    COPAS = '♥'
    PAUS = '♣'

    @property
    def forca(self):
        return list(type(self)).index(self)

    def __str__(self):
        return self.value

    
class Carta:

    def __init__(self, rank: Rank, naipe: Naipe):
        self.rank = rank
        self.naipe = naipe
        self.manilha = False
        
    def tornar_manilha(self):
        self.manilha = True
        
    @property
    def forca(self):
        if self.manilha:
            return len(Rank) + self.naipe.forca / 10
        return self.rank.forca
        
    def __lt__(self, other):
        return self.rank.forca < other.rank.forca

    def __str__(self):
        return f"[{self.rank} {self.naipe}]"
    
    def __repr__(self):
        return str(self)
    
    
class Baralho:

    def __init__(self, limpo=True):
        self.limpo = limpo
        self.cartas = []
        ranks = Rank.baralho_limpo() if limpo else Rank.baralho_sujo()
        for rank in ranks:
            for naipe in Naipe:
                self.cartas.append(Carta(rank, naipe))
                
    def embaralhar(self):
        random.shuffle(self.cartas)
        
    def definir_manilha(self, vira: Carta):
        ranks = Rank.baralho_limpo() if self.limpo else Rank.baralho_sujo()
        manilha_index = (ranks.index(vira.rank) + 1) % len(ranks)
        for carta in self.cartas:
            if carta.rank == ranks[manilha_index]:
                carta.tornar_manilha()
            
    def distribuir_cartas(self):
        self.embaralhar()
        vira = self.cartas.pop()
        self.definir_manilha(vira)
        cartas_a, cartas_b = [], []
        for i in range(3):
            self.cartas.pop()
            cartas_a.append(self.cartas.pop())
            cartas_b.append(self.cartas.pop())
        return cartas_a, cartas_b, vira
