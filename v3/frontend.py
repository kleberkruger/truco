"""Classe abstrata base para o frontend do jogo de Truco.

O frontend é o **agente ativo**: ele possui o loop principal do jogo,
chama os métodos da máquina de estado passiva (`Partida`) e exibe os
estados retornados.  Subclasses concretas implementam os métodos de
exibição e entrada para o tipo de interface desejado (terminal, GUI, web).
"""

from abc import ABC, abstractmethod
from typing import Any

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
)
from partida import Partida


class Frontend(ABC):
    """Classe abstrata base para qualquer frontend de Truco.

    O frontend controla o fluxo do jogo:
    1. Pede a configuração ao usuário.
    2. Cria a partida (backend passivo).
    3. Entra no loop principal, exibindo estados e recolhendo entradas.
    4. Encerra quando a partida termina.

    Subclasses devem implementar os métodos abstratos de exibição e entrada.
    """

    def __init__(self):
        self._partida: Partida | None = None

    # =================================================================
    # Loop principal — método concreto (não sobrescrever)
    # =================================================================

    def executar(self) -> None:
        """Ponto de entrada principal. Orquestra toda a partida."""
        self.exibir_titulo()
        config = self.pedir_configuracao()
        self._partida = Partida(config, frontend=self)

        # Exibir placar inicial
        placar = self._partida.get_placar()
        self.exibir_placar(placar)

        # Loop principal da partida
        while not self._partida.is_partida_finalizada():
            self._executar_mao()

        # Fim de partida
        fim = self._partida.get_fim_partida()
        self.exibir_fim_partida(fim)

    def _executar_mao(self) -> None:
        """Executa uma mão completa, processando cada estado retornado."""
        assert self._partida is not None

        # Iniciar mão
        estado = self._partida.iniciar_mao()
        self._processar_estados(estado)

    def _processar_estados(self, estado: Any) -> None:
        """Processa uma cadeia de estados até encontrar um que requer interação.
        
        Cada tipo de estado é delegado a um método `_manipular_*` específico,
        mantendo o código modular e fácil de estender.
        """
        assert self._partida is not None

        while estado is not None:
            self.exibir_estado(estado)
            estado = self._manipular_estado(estado)

    def _manipular_estado(self, estado: Any) -> Any:
        """Despacha o estado para o manipulador adequado.
        
        Retorna o próximo estado a processar ou None para encerrar o loop.
        """
        if isinstance(estado, EstadoPedirCarta):
            return self._manipular_pedir_carta(estado)
        elif isinstance(estado, EstadoPropostaTruco):
            return self._manipular_proposta_truco(estado)
        elif isinstance(estado, EstadoPedirDecisaoTruco):
            return self._manipular_pedir_decisao_truco(estado)
        elif isinstance(estado, EstadoResultadoMao):
            return self._manipular_resultado_mao(estado)
        elif isinstance(estado, EstadoFimPartida):
            return self._manipular_fim_partida(estado)
        else:
            return self._manipular_informativo(estado)

    # ------------------------------------------------------------------
    # Manipuladores individuais de cada tipo de estado
    # ------------------------------------------------------------------

    def _manipular_pedir_carta(self, estado: EstadoPedirCarta) -> Any:
        """Humano escolhe uma carta ou propõe truco."""
        assert self._partida is not None
        acao = self.pedir_carta_ou_truco(estado)
        if isinstance(acao, ComandoPropostaTruco):
            return self._partida.propor_truco(acao)
        else:
            return self._partida.jogar_carta(acao)

    def _manipular_proposta_truco(self, estado: EstadoPropostaTruco) -> Any:
        """Proposta exibida — processar a resposta da IA se pendente."""
        assert self._partida is not None
        if self._partida.tem_proposta_pendente:
            return self._partida.processar_resposta_proposta_truco()
        else:
            proximo = self._partida.proximo()
            return proximo if proximo is not None else None

    def _manipular_pedir_decisao_truco(self, estado: EstadoPedirDecisaoTruco) -> Any:
        """Humano decide sobre proposta de truco da IA."""
        assert self._partida is not None
        decisao = self.pedir_decisao_truco(estado)
        return self._partida.responder_truco(decisao)

    def _manipular_resultado_mao(self, estado: EstadoResultadoMao) -> None:
        """Mão finalizada — verificar se a partida também terminou."""
        assert self._partida is not None
        if self._partida.is_partida_finalizada():
            fim = self._partida.get_fim_partida()
            self.exibir_fim_partida(fim)
        return None

    def _manipular_fim_partida(self, estado: EstadoFimPartida) -> None:
        """Fim de partida — encerrar o loop."""
        return None

    def _manipular_informativo(self, estado: Any) -> Any:
        """Estados informativos que apenas avançam para o próximo."""
        assert self._partida is not None

        if isinstance(estado, EstadoInicioMao):
            return self._manipular_inicio_mao()
        elif isinstance(estado, EstadoInicioRodada):
            return self._partida.proximo()
        elif isinstance(estado, EstadoCartaJogada):
            return self._partida.proximo()
        elif isinstance(estado, EstadoVencedorRodada):
            return self._manipular_vencedor_rodada()
        elif isinstance(estado, EstadoRespostaTruco):
            return self._partida.proximo()
        else:
            return None

    def _manipular_inicio_mao(self) -> Any:
        """Após início da mão, exibir placar e cartas, então obter próximo estado."""
        assert self._partida is not None
        placar = self._partida.get_placar()
        self.exibir_placar(placar)
        cartas = self._partida.get_cartas_humano()
        self.exibir_cartas_mao(cartas)

        proximo = self._partida.proximo()
        if isinstance(proximo, EstadoInicioRodada):
            # IA joga primeiro — obter o resultado da jogada
            proximo2 = self._partida.proximo()
            return proximo2 if proximo2 is not None else proximo
        else:
            return proximo

    def _manipular_vencedor_rodada(self) -> Any:
        """Após vencedor da rodada, verificar se a mão terminou ou continua."""
        assert self._partida is not None
        if self._partida.is_mao_finalizada():
            return self._partida.proximo()
        else:
            return self._partida.proximo()

    # =================================================================
    # Métodos abstratos — implementação pela subclass concreta
    # =================================================================

    @abstractmethod
    def exibir_titulo(self) -> None:
        """Exibe o título/tela inicial do jogo."""
        ...

    @abstractmethod
    def pedir_configuracao(self) -> ConfiguracaoJogo:
        """Pede ao usuário os dados iniciais do jogo."""
        ...

    @abstractmethod
    def exibir_placar(self, estado: EstadoPlacar) -> None:
        """Exibe o placar atual."""
        ...

    @abstractmethod
    def exibir_inicio_mao(self, estado: EstadoInicioMao) -> None:
        """Exibe mensagem de início de mão."""
        ...

    @abstractmethod
    def exibir_cartas_mao(self, estado: EstadoCartasMao) -> None:
        """Exibe as cartas da mão do humano e a carta virada."""
        ...

    @abstractmethod
    def exibir_inicio_rodada(self, estado: EstadoInicioRodada) -> None:
        """Exibe mensagem de início de rodada."""
        ...

    @abstractmethod
    def pedir_carta_ou_truco(self, estado: EstadoPedirCarta) -> ComandoCarta | ComandoPropostaTruco:
        """Pede ao humano que escolha uma carta para jogar ou proponha truco.
        
        Retorna ``ComandoCarta`` se o humano jogar uma carta, ou
        ``ComandoPropostaTruco`` se o humano propor truco/seis/nove/doze.
        """
        ...

    @abstractmethod
    def exibir_carta_jogada(self, estado: EstadoCartaJogada) -> None:
        """Exibe que um jogador jogou uma carta."""
        ...

    @abstractmethod
    def exibir_vencedor_rodada(self, estado: EstadoVencedorRodada) -> None:
        """Exibe o vencedor de uma rodada."""
        ...

    @abstractmethod
    def exibir_proposta_truco(self, estado: EstadoPropostaTruco) -> None:
        """Exibe uma proposta de truco."""
        ...

    @abstractmethod
    def pedir_decisao_truco(self, estado: EstadoPedirDecisaoTruco) -> ComandoDecisaoTruco:
        """Pede ao humano a decisão sobre uma proposta de truco."""
        ...

    @abstractmethod
    def exibir_resposta_truco(self, estado: EstadoRespostaTruco) -> None:
        """Exibe a resposta a uma proposta de truco."""
        ...

    @abstractmethod
    def exibir_resultado_mao(self, estado: EstadoResultadoMao) -> None:
        """Exibe o resultado de uma mão."""
        ...

    @abstractmethod
    def exibir_fim_partida(self, estado: EstadoFimPartida) -> None:
        """Exibe a tela de fim de partida."""
        ...

    # =================================================================
    # Método concreto que delega para os métodos abstratos
    # =================================================================

    def exibir_estado(self, estado: Any) -> None:
        """Despacha o estado para o método de exibição adequado."""
        if isinstance(estado, EstadoInicioMao):
            self.exibir_inicio_mao(estado)
        elif isinstance(estado, EstadoCartasMao):
            self.exibir_cartas_mao(estado)
        elif isinstance(estado, EstadoPlacar):
            self.exibir_placar(estado)
        elif isinstance(estado, EstadoInicioRodada):
            self.exibir_inicio_rodada(estado)
        elif isinstance(estado, EstadoCartaJogada):
            self.exibir_carta_jogada(estado)
        elif isinstance(estado, EstadoVencedorRodada):
            self.exibir_vencedor_rodada(estado)
        elif isinstance(estado, EstadoPropostaTruco):
            self.exibir_proposta_truco(estado)
        elif isinstance(estado, EstadoRespostaTruco):
            self.exibir_resposta_truco(estado)
        elif isinstance(estado, EstadoResultadoMao):
            self.exibir_resultado_mao(estado)
        elif isinstance(estado, EstadoFimPartida):
            self.exibir_fim_partida(estado)
