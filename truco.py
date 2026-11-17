from enum import StrEnum

from baralho import Baralho, Carta
from jogador import Jogador, JogadaCarta


class Lado(StrEnum):
    LADO_A = 'A'
    LADO_B = 'B'


class Partida:
    def __init__(
            self,
            equipe_a: Jogador | list[Jogador],
            equipe_b: Jogador | list[Jogador]
    ):
        self._baralho = None
        self._equipe_a, self._equipe_b = self._validar_equipes(equipe_a, equipe_b)
        self._pontos_a, self._pontos_b = 0, 0
        self._jogadores = [e for par in zip(self._equipe_a, self._equipe_b) for e in par]
        self._lado_jogador = {
            **dict.fromkeys(self._equipe_a, Lado.LADO_A),
            **dict.fromkeys(self._equipe_b, Lado.LADO_B),
        }
        self._vez_mao: int = 0

    @staticmethod
    def _validar_equipes(equipe_a, equipe_b):
        if isinstance(equipe_a, Jogador) and isinstance(equipe_b, Jogador):
            return [equipe_a], [equipe_b]
        if (isinstance(equipe_a, list) and all(isinstance(j, Jogador) for j in equipe_a) and
                isinstance(equipe_b, list) and all(isinstance(j, Jogador) for j in equipe_b)):
            if len(equipe_a) != len(equipe_b):
                raise ValueError("Número de jogadores diferentes por equipe")
            elif len(equipe_a) < 1 or len(equipe_a) > 3:
                raise ValueError("Número de jogadores inválido")
            # Valide para que um jogador não possa estar duas vezes nas listas
            return equipe_a, equipe_b
        raise ValueError("Jogadores inválido")

    def iniciar(self, baralho_limpo=True):
        self._baralho = Baralho(baralho_limpo)

        numero_mao = 1
        jogador_inicial = self._jogadores[0]
        while self.pontos_a < 12 and self.pontos_b < 12:
            cartas, vira = self._baralho.distribuir_cartas(len(self._equipe_a))
            for j in self.jogadores:
                j.iniciar_mao(cartas.pop(), vira)
            mao = Mao(numero_mao, self)
            lado_ganhador, pontos = mao.executar(jogador_inicial)
            self._pontuar(lado_ganhador, pontos)
            jogador_inicial = self._proximo_jogador()

    def _pontuar(self, lado_ganhador: Lado, pontos: int):
        if lado_ganhador == Lado.LADO_A:
            self._pontos_a += pontos
        else:
            self._pontos_b += pontos

    def _proximo_jogador(self) -> Jogador:
        self._vez = self._vez_mao + 1 if self._vez_mao < len(self._jogadores) - 1 else 0
        return self._jogadores[self._vez]

    def lado_jogador(self, jogador: Jogador):
        return self._lado_jogador[jogador]

    @property
    def jogadores(self):
        return self._jogadores

    @property
    def equipe_a(self):
        return self._equipe_a

    @property
    def equipe_b(self):
        return self._equipe_b

    @property
    def pontos_a(self):
        return self._pontos_a

    @property
    def pontos_b(self):
        return self._pontos_b


class Mao:

    def __init__(self, numero: int, partida: Partida):
        self._numero: int = numero
        self._partida: Partida = partida
        self._rodadas_a: int = 0
        self._rodadas_b: int = 0
        self._pontuacao: int = 1

    def executar(self, jogador_inicial: Jogador) -> tuple[Lado, int] | tuple[None, int]:
        rodadas = 1
        primeiro_vencedor = None
        while rodadas <= 3:
            rodada = Rodada(rodadas, self)
            vencedor = rodada.executar(jogador_inicial)
            if vencedor is not None:
                jogador_inicial = vencedor
            self._pontuar(vencedor)
            if rodadas == 1 and vencedor is not None:
                primeiro_vencedor = self._partida.lado_jogador(vencedor)
            resultado = self._avaliar_resultado(rodadas, primeiro_vencedor)
            if resultado is not None:
                return resultado, self._pontuacao
            rodadas += 1
        return None, 0

    def _pontuar(self, vencedor: Jogador | None):
        print("------------------------------------------------------------")
        if vencedor is not None:
            if self._partida.lado_jogador(vencedor) == Lado.LADO_A:
                self._rodadas_a += 1
                print(f"Rodada vencida por {vencedor.nome} [LADO A]")
            else:
                self._rodadas_b += 1
                print(f"Rodada vencida por {vencedor.nome} [LADO B]")
        else:
            print(f"Rodada terminada em empate")

    def _avaliar_resultado(self, rodada: int, primeiro_vencedor: Lado | None) -> Lado | None:
        if self._rodadas_a == 2:
            return Lado.LADO_A
        if self._rodadas_b == 2:
            return Lado.LADO_B
        if rodada == 2:
            if self._rodadas_a == 1 and self._rodadas_b == 0:
                return Lado.LADO_A
            elif self._rodadas_a == 0 and self._rodadas_b == 1:
                return Lado.LADO_B
        elif rodada == 3:
            if self._rodadas_a > self._rodadas_b:
                return Lado.LADO_A
            elif self._rodadas_b > self._rodadas_a:
                return Lado.LADO_B
            else:
                return primeiro_vencedor
        return None

    def rodadas_vencidas(self, jogador: Jogador) -> int:
        if jogador in self._partida.equipe_a:
            return self._rodadas_a
        elif jogador in self._partida.equipe_b:
            return self._rodadas_b
        raise ValueError("Este jogador não pertence a essa partida")

    @property
    def numero(self):
        return self._numero

    @property
    def jogadores(self):
        return self._partida.jogadores

    @property
    def rodadas_a(self):
        return self._rodadas_a

    @property
    def rodadas_b(self):
        return self._rodadas_b

    @property
    def pontuacao(self):
        return self._pontuacao

    @property
    def equipe_vencedora(self):
        return None


class Rodada:

    def __init__(self, numero: int, mao: Mao):
        self._numero: int = numero
        self._mao: Mao = mao
        self._vencedor: Jogador | None = None
        self._maior_carta: Carta | None = None
        self._vez: int = 0

    def executar(self, jogador_inicial: Jogador):
        self._vez = self.jogadores.index(jogador_inicial)
        jogador_atual = jogador_inicial
        for _ in self.jogadores:
            vencidas = self._mao.rodadas_vencidas(jogador_atual)
            jogada = jogador_atual.jogar(self._numero, vencidas, self._maior_carta)
            carta_jogada = jogada.carta if isinstance(jogada, JogadaCarta) else jogada
            self._avaliar_jogada(jogador_atual, carta_jogada)
            jogador_atual = self._proximo()
        return self._vencedor

    def _avaliar_jogada(self, jogador: Jogador, carta_jogada: Carta):
        if self._maior_carta is None or carta_jogada > self._maior_carta:
            self._maior_carta = carta_jogada
            self._vencedor = jogador
        elif carta_jogada == self._maior_carta:
            self._vencedor = None

    def _proximo(self):
        self._vez = self._vez + 1 if self._vez < len(self.jogadores) - 1 else 0
        return self.jogadores[self._vez]

    @property
    def numero(self):
        return self._numero

    @property
    def jogadores(self):
        return self._mao.jogadores

    @property
    def vencedor(self):
        return self._vencedor

    @property
    def maior_carta(self):
        return self._maior_carta

    @property
    def lado_vencedor(self):
        raise NotImplementedError()


def main():
    j1 = Jogador("Rhana")
    j2 = Jogador("Alan")
    j3 = Jogador("Vinicius")
    j4 = Jogador("Kleber")

    p1 = Partida(j1, j2)
    p1.iniciar()

    p2 = Partida([j1, j3], [j2, j4])
    p2.iniciar()


if __name__ == "__main__":
    main()
