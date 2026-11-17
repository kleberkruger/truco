"""Objetos de estado e eventos retornados pela máquina de estado do backend.

Cada classe representa um "snapshot" do que o frontend deve exibir ou uma
ação que o frontend deve solicitar ao usuário. O backend nunca exibe nada
diretamente — ele apenas retorna esses objetos, e o frontend ativo decide
como apresentá-los.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from baralho import Carta
from jogador import Dificuldade


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Lado(StrEnum):
    """Lado de uma equipe na partida."""
    LADO_A = "A"
    LADO_B = "B"


class FaseMao(StrEnum):
    """Indica se a mão continua em andamento ou já teve um vencedor."""
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"


# ---------------------------------------------------------------------------
# Configuração do jogo
# ---------------------------------------------------------------------------

@dataclass
class ConfiguracaoJogo:
    """Dados de configuração recolhidos pelo frontend antes da partida."""
    nome_humano: str
    nome_ia: str
    dificuldade: Dificuldade
    baralho_limpo: bool


# ---------------------------------------------------------------------------
# Estados da partida
# ---------------------------------------------------------------------------

@dataclass
class EstadoPlacar:
    """Placar atual da partida — o frontend deve exibi-lo."""
    pontos_a: int
    pontos_b: int
    nome_a: str
    nome_b: str


@dataclass
class EstadoInicioMao:
    """Sinaliza o início de uma nova mão com o número da mão."""
    numero_mao: int


@dataclass
class EstadoCartasMao:
    """Cartas distribuídas ao jogador humano e a carta virada."""
    cartas: list[Carta]
    vira: Carta


@dataclass
class EstadoInicioRodada:
    """Início de uma rodada: indica de quem é a vez de jogar."""
    numero_rodada: int
    nome_jogador: str
    vez_humano: bool


@dataclass
class EstadoPedirCarta:
    """Backend solicita ao frontend que o humano escolha uma carta.
    
    O campo `pontuacao_mao` indica a pontuação atual da mão, permitindo
    que o frontend ofereça a opção de propor truco se a pontuação for < 12.
    """
    cartas_disponiveis: list[Carta]
    numero_rodada: int
    rodadas_vencidas: int
    maior_carta_mesa: Carta | None
    vira: Carta | None
    pontuacao_mao: int = 1


@dataclass
class EstadoCartaJogada:
    """Um jogador jogou uma carta na mesa."""
    nome_jogador: str
    carta: Carta


@dataclass
class EstadoVencedorRodada:
    """Resultado de uma rodada: quem venceu (ou empate)."""
    nome_vencedor: str | None
    lado_vencedor: Lado | None


@dataclass
class EstadoPropostaTruco:
    """Proposta de truco/seis/nove/doze feita por um jogador."""
    nome_propositor: str
    pontuacao_atual: int
    pontuacao_proposta: int


@dataclass
class EstadoPedirDecisaoTruco:
    """Backend solicita ao frontend a decisão sobre uma proposta de truco."""
    pontuacao_atual: int
    pontuacao_proposta: int


@dataclass
class EstadoRespostaTruco:
    """Resposta do jogador humano a uma proposta de truco."""
    aceita: bool
    pontuacao_contra_oferta: int | None


@dataclass
class EstadoResultadoMao:
    """Resultado de uma mão: lado vencedor e pontos conquistados."""
    lado_ganhador: Lado | None
    pontos: int
    nome_a: str
    nome_b: str


@dataclass
class EstadoFimPartida:
    """Fim da partida: lado vencedor e placar final."""
    lado_ganhador: Lado
    pontos_a: int
    pontos_b: int
    nome_a: str
    nome_b: str


# ---------------------------------------------------------------------------
# Comandos do frontend para o backend
# ---------------------------------------------------------------------------

@dataclass
class ComandoCarta:
    """Frontend informa qual carta o humano jogou."""
    carta: Carta


@dataclass
class ComandoDecisaoTruco:
    """Frontend informa a decisão do humano sobre uma proposta de truco."""
    aceita: bool
    pontuacao_contra_oferta: int | None


@dataclass
class ComandoPropostaTruco:
    """Frontend informa que o humano propõe truco/seis/nove/doze."""
    pontuacao_proposta: int
