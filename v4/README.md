# Truco Paulista — arquitetura modular

Projeto Python com domínio independente da interface. A mesma sessão e as mesmas regras são utilizadas pelo terminal e pelo Pygame.

## Estrutura

```text
truco/
├── dominio/                 # Cartas, jogadores, equipes e regras da partida
│   ├── baralho.py
│   ├── participante.py
│   └── truco.py
├── aplicacao/               # Orquestra a partida, bots e ações do jogador
│   └── sessao.py
├── interfaces/              # Adaptadores de apresentação
│   ├── view.py
│   ├── terminal.py
│   └── pygame_ui.py
├── assets/                  # Mesa e imagens das cartas
├── tests/
├── main.py
└── requirements.txt
```

## Instalação

Recomendado Python 3.12 ou 3.13. Para a interface gráfica, instale as dependências no mesmo interpretador que será usado para executar o jogo:

```bash
python -m pip install -r requirements.txt
```

A interface de terminal não depende do Pygame:

```bash
python main.py --interface terminal
```

A interface gráfica:

```bash
python main.py --interface gui
```

No macOS, por exemplo, use o mesmo executável nos dois comandos:

```bash
python3 -m pip install -r requirements.txt
python3 main.py --interface terminal
python3 main.py --interface gui
```

## Responsabilidades

- **dominio/**: regras do truco, distribuição, cartas, vazas, apostas, mão de onze e pontuação. Não importa Pygame, terminal ou `input()`.
- **aplicacao/sessao.py**: coordena o jogador humano, os bots, as ações e os eventos. Não desenha nem lê teclado.
- **interfaces/terminal.py**: interação textual usando `input()` e `print()`.
- **interfaces/pygame_ui.py**: interface gráfica, eventos de mouse/teclado e temporização dos bots.
- **main.py**: escolhe qual adaptador de apresentação iniciar.

As interfaces dependem da camada de aplicação; domínio e aplicação não dependem de nenhuma interface.

## Regras implementadas

Truco Paulista com manilha móvel, baralho limpo (24 cartas) ou sujo (40 cartas), partidas individual/duplas/trios, mão até 12 pontos, pedidos de truco/seis/nove/doze, aceitar/correr/aumentar e mão de onze simplificada. Trios usam obrigatoriamente baralho sujo.

Limitações atuais: bots com estratégia simples; mão de ferro e multiplayer em rede não implementados. A mão de onze é decidida por um representante da equipe.

## Testes

```bash
python -m unittest discover -s tests -v
```
