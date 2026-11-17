# Truco Paulista — Versão 5

**Arquitetura modular com classes bem definidas e responsabilidades claras.**

A versão 5 é a evolução definitiva do Truco Paulista, combinando o melhor de todas as versões anteriores em uma arquitetura limpa, testável e extensível.

---

## Arquitetura

```
v5/
├── dominio/              # Regras puras do jogo (sem dependência de UI)
│   ├── __init__.py
│   ├── rank.py           # Valores das cartas (4, 5, 6, 7, Q, J, K, A, 2, 3)
│   ├── naipe.py          # Naipes (♦, ♠, ♥, ♣)
│   ├── carta.py          # Carta individual com rank, naipe e manilha
│   ├── baralho.py        # Criação, embaralhamento e distribuição
│   ├── jogador.py        # Jogador com nome, ID e mão de cartas
│   ├── equipe.py         # Grupo de 1-3 jogadores (imutável)
│   ├── estado.py         # Estados da partida e modalidades
│   ├── vaza.py           # Jogada e ResultadoVaza (dados imutáveis)
│   ├── mao.py            # Máquina de estados de uma mão (passiva)
│   └── partida.py        # Partida completa com placar e mãos sequenciais
├── estrategia/           # Inteligência Artificial
│   ├── __init__.py
│   └── ia.py             # IA com 3 níveis de dificuldade
├── aplicacao/            # Orquestração entre domínio e interface
│   ├── __init__.py
│   ├── evento.py         # Sistema de eventos (dados imutáveis)
│   └── sessao.py         # Sessão: turnos, bots, ações do humano
├── interfaces/           # Apresentação (terminal ou PyQt6)
│   ├── __init__.py
│   ├── terminal.py       # Interface de texto interativa
│   └── pyqt.py           # Interface gráfica moderna com PyQt6
├── tests/                # Testes automatizados
│   └── test_jogo.py
├── main.py               # Ponto de entrada
├── requirements.txt      # Dependências
└── README.md
```

## Camadas

### 1. Domínio (`dominio/`)
Regras puras do Truco. Não importa Pygame, PyQt, terminal ou qualquer biblioteca de interface. Cada módulo tem uma responsabilidade única e concisa:

- **`rank.py`** e **`naipe.py`**: Enums atômicos para valores e naipes
- **`carta.py`**: Carta com força calculada dinamicamente (manilha > normal)
- **`baralho.py`**: Embaralha e distribui cartas, define manilhas
- **`jogador.py`**: Jogador com mão de cartas (imutável via tupla)
- **`equipe.py`**: Grupo imutável de jogadores
- **`estado.py`**: Estados da partida (AGUARDANDO, JOGANDO, PEDIDO_PENDENTE, ENCERRADA)
- **`vaza.py`**: Dados imutáveis de jogadas e resultados
- **`mao.py`**: Máquina de estados passiva para uma mão — vazas, truco, mão de onze
- **`partida.py`**: Orquestra múltiplas mãos, placar global, detecta vencedor

### 2. Estratégia (`estrategia/`)
Inteligência Artificial modular com 3 níveis de dificuldade:

- **`EstrategiaCarta`**: Decide qual carta jogar (fraca/forte/contextual)
- **`EstrategiaAposta`**: Decide se pede/aceita truco
- **`IA`**: Combina as duas estratégias

### 3. Aplicação (`aplicacao/`)
Orquestra tudo sem saber como a interface funciona:

- **`evento.py`**: Eventos imutáveis emitidos pela Sessão
- **`sessao.py`**: Cria partida, controla bots, gerencia ações do humano

### 4. Interfaces (`interfaces/`)
Adaptadores intercambiáveis:

- **`terminal.py`**: Interface de texto com menu interativo
- **`pyqt.py`**: Interface gráfica moderna com mesa de jogo visual

## Como Rodar

### Interface gráfica (PyQt6)
```bash
cd v5
pip install -r requirements.txt
python main.py
```

### Interface de terminal
```bash
cd v5
python main.py --interface terminal
```

### Testes
```bash
cd v5
python -m pytest tests/ -v
# ou
python -m unittest tests.test_jogo -v
```

## Diferenciais da V5

| Recurso | V4 | V5 |
|---|---|---|
| Módulos atômicos | ❌ Arquivos grandes | ✓ Cada classe em seu módulo |
| Mão como máquina de estados | ❌ Misturada na Partida | ✓ Classe Mao separada |
| IA com dificuldades | ❌ Simples | ✓ 3 níveis (Fácil, Médio, Difícil) |
| Estratégia modular | ❌ | ✓ Strategy pattern |
| Dados imutáveis | ⚠️ Parcial | ✓ Extensivo (slots, frozen) |
| Testes | ✓ Básicos | ✓ Completos |
| Escolha de dificuldade | ❌ | ✓ No menu |

## Regras Implementadas

- **Modalidades**: Individual (1×1), Duplas (2×2), Trios (3×3)
- **Baralho**: Limpo (24 cartas) ou Sujo (40 cartas)
- **Manilha móvel**: Definida pela carta virada
- **Truco**: Progressão 1→3→6→9→12 com contra-aumento
- **Mão de onze**: Decisão quando alguém chega em 11 pontos
- **Vencedor**: Primeiro a 12 pontos
