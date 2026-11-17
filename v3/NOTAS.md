# Truco v3 — Notas de Implementação Modular

## Visão Geral da Arquitetura

Esta versão do jogo de Truco segue o padrão **Frontend Ativo + Backend Passivo (Máquina de Estado)**.

- **Backend passivo**: a classe `Partida` é uma máquina de estado que não possui loops nem faz I/O. Cada método avança o estado do jogo e retorna um objeto de estado para o frontend consumir.
- **Frontend ativo**: a classe `Frontend` (e suas subclasses) possui o loop principal do jogo. Ela chama os métodos do backend, exibe os estados retornados e recolhe as entradas do usuário.
- **Objetos de estado**: os arquivos `estados.py` definem os dataclasses que fazem a ponte entre backend e frontend, servindo como contratos de comunicação.

Esta arquitetura permite que qualquer tipo de frontend (terminal, GUI com PyQt6, web) seja implementado sem alterar o backend.

---

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Ativo)                   │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Frontend (ABC) — classe abstrata               │ │
│  │  - executar() → loop principal                  │ │
│  │  - métodos abstratos de exibição/entrada        │ │
│  └──────────────────────┬──────────────────────────┘ │
│                         │ herda                      │
│  ┌──────────────────────▼──────────────────────────┐ │
│  │  FrontendTerminal — implementação concreta       │ │
│  │  - print() / input()                            │ │
│  └──────────────────────┬──────────────────────────┘ │
│                         │ chama                      │
└─────────────────────────┼─────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────┐
│                 Backend (Passivo)                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Partida — máquina de estado                    │  │
│  │  - iniciar_mao() → EstadoInicioMao              │  │
│  │  - jogar_carta() → EstadoCartaJogada            │  │
│  │  - responder_truco() → EstadoRespostaTruco      │  │
│  │  - get_placar() → EstadoPlacar                  │  │
│  └──────────────────────┬──────────────────────────┘  │
│                         │ usa                          │
│  ┌──────────────────────▼──────────────────────────┐  │
│  │  Baralho, Carta, Rank, Naipe                    │  │
│  │  Jogador, JogadorHumano, JogadorIA              │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## Atividades de Implementação

Cada atividade abaixo corresponde a um módulo (arquivo) da implementação. Elas foram desenhadas para serem aplicadas em uma disciplina de Algoritmos 2 e POO, com objetivos claros e progressivos.

---

### Atividade 1: Baralho e Cartas (`baralho.py`)

**Objetivo:** Implementar a representação de um baralho de cartas com as regras do Truco.

**Conceitos de POO:**
- **Enums** (`StrEnum`): `Rank` e `Naipe` representam os valores e naipes das cartas.
- **Propriedades computadas**: `forca` em `Rank`, `Naipe` e `Carta` calculam o poder da carta dinamicamente.
- **Comparação de objetos**: os métodos `__lt__` e `__eq__` em `Carta` permitem comparar cartas por força.
- **Métodos de classe**: `baralho_limpo()` e `baralho_sujo()` em `Rank` criam conjuntos diferentes de cartas.
- **Encapsulamento**: os atributos de `Carta` são privados, acessíveis apenas via propriedades.

**Tarefas:**
1. Criar o enum `Rank` com os 10 valores do Truco (7 a 3, mais Q, J, K, A, 2).
2. Criar o enum `Naipe` com os 4 naipes (♦, ♠, ♥, ♣).
3. Implementar a classe `Carta` com comparação por força.
4. Implementar a classe `Baralho` com embaralhamento e distribuição.
5. Implementar o sistema de manilha (carta seguinte à virada).

**Desafio:** Por que a manilha usa `len(Rank) * 10 + naipe.forca` em vez de apenas um valor fixo?

---

### Atividade 2: Jogadores (`jogador.py`)

**Objetivo:** Implementar os jogadores do jogo usando abstração e polimorfismo.

**Conceitos de POO:**
- **Classe abstrata** (`ABC`): `Jogador` define a interface comum para todos os jogadores.
- **Métodos abstratos**: `jogar()` e `decidir_proposta()` devem ser implementados por subclasses.
- **Padrão Strategy**: `JogadorIA` usa estratégias diferentes conforme o nível de dificuldade.
- **Protocolos** (`Protocol`): `JogadorHumanoFrontend` define um contrato de tipo para injeção de dependência.
- **Injeção de dependência**: `JogadorHumano` recebe o frontend no construtor, não o cria.

**Tarefas:**
1. Criar a classe abstrata `Jogador` com métodos abstratos.
2. Implementar `JogadorHumano` que delega ao frontend.
3. Implementar `JogadorIA` com 3 níveis de dificuldade.
4. Criar o protocolo `JogadorHumanoFrontend` para separar backend de frontend.
5. Implementar as classes de ação: `JogadaCarta`, `JogadaTruco`, `JogadaCorrer`.

**Desafio:** Como o padrão Strategy permite trocar a dificuldade da IA sem modificar o código da partida?

---

### Atividade 3: Objetos de Estado (`estados.py`)

**Objetivo:** Definir os objetos de transferência de dados (Data Transfer Objects — DTOs) que comunicam backend e frontend.

**Conceitos de POO:**
- **Dataclasses**: objetos imutáveis que carregam dados entre módulos.
- **Separação de responsabilidades**: os estados não contêm lógica, apenas dados.
- **Tipagem estática**: cada estado tem campos tipados, facilitando a verificação de contrato.
- **Enums**: `Lado` e `FaseMao` representam estados do jogo de forma explícita.
- **Padrão Command**: `ComandoCarta` e `ComandoDecisaoTruco` representam ações do frontend para o backend.

**Tarefas:**
1. Definir os enums `Lado` e `FaseMao`.
2. Criar dataclasses para cada estado do jogo (placar, início de mão, cartas, etc.).
3. Criar dataclasses para comandos do frontend (jogar carta, decidir truco).
4. Documentar cada classe com docstrings claras.

**Desafio:** Por que usar dataclasses em vez de dicionários? Quais garantias isso oferece?

---

### Atividade 4: Máquina de Estado (`partida.py`)

**Objetivo:** Implementar o backend passivo como uma máquina de estado que responde a chamadas do frontend.

**Conceitos de POO:**
- **Máquina de estado**: cada método avança o estado interno e retorna um objeto de estado.
- **Padrão State**: a classe `Partida` encapsula todo o estado do jogo.
- **Separação backend/frontend**: a classe nunca faz `print()` nem `input()`.
- **Encapsulamento**: o estado interno é privado; o frontend só acessa via métodos públicos.
- **Composição**: `Partida` compõe `Baralho`, `JogadorHumano` e `JogadorIA`.

**Tarefas:**
1. Implementar o construtor que cria os jogadores e inicializa o estado.
2. Implementar `iniciar_mao()` que distribui cartas e retorna `EstadoInicioMao`.
3. Implementar `jogar_carta()` que processa a jogada do humano e da IA.
4. Implementar `_finalizar_rodada()` com as regras de vitória do Truco.
5. Implementar `_verificar_fim_mao()` com todas as condições de término.
6. Implementar os métodos de truco/seis/nove/doze.
7. Implementar os métodos de consulta (`get_placar()`, `is_partida_finalizada()`).

**Desafio:** Como a máquina de estado garante que o frontend não possa "pular" etapas do jogo?

---

### Atividade 5: Frontend Abstrato (`frontend.py`)

**Objetivo:** Implementar a classe abstrata base do frontend, que é o agente ativo do sistema.

**Conceitos de POO:**
- **Classe abstrata** (`ABC`): define o contrato que todos os frontends devem seguir.
- **Template Method**: `executar()` define o esqueleto do algoritmo; os métodos abstratos são preenchidos pelas subclasses.
- **Padrão Observer/Dispatcher**: `exibir_estado()` despacha cada tipo de estado para o método adequado.
- **Loop principal**: o frontend controla o fluxo, não o backend.
- **Polimorfismo**: o mesmo loop funciona para terminal, GUI, ou web.

**Tarefas:**
1. Criar a classe abstrata `Frontend` com o método concreto `executar()`.
2. Implementar o loop principal que itera enquanto a partida não termina.
3. Implementar `_executar_mao()` que processa uma mão completa.
4. Implementar `_processar_estados()` como um loop simples que delega a `_manipular_estado()`.
5. Implementar `_manipular_estado()` como dispatcher que encaminha cada tipo de estado para o manipulador correto.
6. Criar os métodos `_manipular_*` para cada tipo de estado, seguindo o Princípio de Responsabilidade Única.
7. Definir todos os métodos abstratos de exibição e entrada.
8. Implementar `exibir_estado()` como dispatcher genérico de exibição.

**Desafio:** Qual a diferença entre Template Method (usado aqui) e Strategy (usado na IA)?

---

### Atividade 6: Frontend Terminal (`frontend_terminal.py`)

**Objetivo:** Implementar a versão terminal concreta do frontend.

**Conceitos de POO:**
- **Herança**: `FrontendTerminal` herda de `Frontend` e implementa todos os métodos abstratos.
- **Implementação concreta**: cada método abstrato é preenchido com `print()` e `input()`.
- **Validação de entrada**: loops `while` com tratamento de exceções garantem entradas válidas.
- **Formatação de saída**: uso de emojis e formatação para melhorar a experiência do usuário.

**Tarefas:**
1. Herdar de `Frontend` e implementar `exibir_titulo()`.
2. Implementar `pedir_configuracao()` com validação de entrada.
3. Implementar os métodos de exibição de cada tipo de estado.
4. Implementar `pedir_carta_ou_truco()` com menu numerado e opção de truco.
5. Implementar `pedir_decisao_truco()` com opções de aceitar, correr e contra-oferecer.
6. Implementar `_pedir_proposta_truco()` para escolher o nível de proposta.

**Desafio:** Como seria a implementação de um `FrontendPyQt6`? Quais métodos mudariam?

---

### Atividade 7: Ponto de Entrada (`truco.py`)

**Objetivo:** Criar o arquivo principal que inicia o jogo.

**Conceitos:**
- **Separation of Concerns**: o ponto de entrada é mínimo, apenas instancia e executa.
- **Injeção de dependência**: o frontend é escolhido aqui, permitindo trocar a implementação.
- **Padrão `if __name__ == "__main__"`**: permite importar os módulos sem executar o jogo.

**Tarefas:**
1. Importar `FrontendTerminal`.
2. Criar a função `main()` que instancia e executa o frontend.
3. Adicionar o guard `if __name__ == "__main__"`.

**Desafio:** Como trocar o frontend terminal por um frontend GUI apenas neste arquivo?

---

### Atividade 8: Frontend Terminal para Jogador Humano (`jogador_terminal.py`)

**Objetivo:** Implementar o frontend específico para o jogador humano, usado pela classe `JogadorHumano`.

**Conceitos de POO:**
- **Protocolo**: a classe implementa implicitamente o protocolo `JogadorHumanoFrontend`.
- **Injeção de dependência**: o frontend é injetado no `JogadorHumano`, não hard-coded.
- **Dupla responsabilidade do frontend**: o frontend principal (`FrontendTerminal`) também serve como `JogadorHumanoFrontend`.

**Tarefas:**
1. Entender que `FrontendTerminal` já implementa os métodos do protocolo `JogadorHumanoFrontend`.
2. Verificar que o `Frontend` abstrato define os métodos compatíveis com o protocolo.

**Nota:** Na arquitetura atual, o `FrontendTerminal` serve tanto como o frontend principal quanto como o frontend do jogador humano, pois os métodos são compatíveis com o protocolo `JogadorHumanoFrontend`.

---

## Resumo dos Conceitos de POO Aplicados

| Conceito | Onde Aplicado |
|---|---|
| **Abstração (ABC)** | `Jogador`, `Frontend` |
| **Polimorfismo** | `JogadorIA`/`JogadorHumano`, `FrontendTerminal` |
| **Encapsulamento** | `Carta`, `Partida`, `Baralho` |
| **Herança** | `FrontendTerminal(Frontend)`, `JogadorIA(Jogador)` |
| **Padrão Strategy** | `JogadorIA` com dificuldades |
| **Padrão State** | `Partida` como máquina de estado |
| **Template Method** | `Frontend.executar()` |
| **Injeção de Dependência** | `JogadorHumano` recebe frontend |
| **Protocolos (Duck Typing)** | `JogadorHumanoFrontend` |
| **Dataclasses (DTOs)** | Todos os estados em `estados.py` |
| **Padrão Command** | `ComandoCarta`, `ComandoDecisaoTruco`, `ComandoPropostaTruco` |
| **Princípio SRP** | Manipuladores `_manipular_*` em `frontend.py` |
| **Enums** | `Rank`, `Naipe`, `Lado`, `FaseMao`, `Dificuldade` |

---

### Atividade 9: Propostas de Truco pelo Humano

**Objetivo:** Permitir que o jogador humano proponha truco/seis/nove/doze durante o jogo, antes de jogar uma carta.

**Conceitos de POO:**
- **União de tipos** (`Union` / `|`): o método `pedir_carta_ou_truco` retorna `ComandoCarta | ComandoPropostaTruco`, demonstrando como um método pode retornar tipos diferentes.
- **Máquina de estado com estados pendentes**: o backend armazena `_pontuacao_proposta_pendente` para separar a exibição da proposta da decisão da IA.
- **Validação no backend**: o método `propor_truco` valida se a proposta é maior que a pontuação atual e se é um valor válido (3, 6, 9, 12).
- **Fluxo assíncrono de estados**: a proposta do humano gera `EstadoPropostaTruco` para exibição, depois `processar_resposta_proposta_truco()` retorna a decisão da IA.

**Tarefas:**
1. Criar `ComandoPropostaTruco` em `estados.py` para representar a proposta do humano.
2. Adicionar `pontuacao_mao` a `EstadoPedirCarta` para informar a pontuação atual ao frontend.
3. Modificar `propor_truco()` em `partida.py` para aceitar `ComandoPropostaTruco` e validar a proposta.
4. Adicionar `processar_resposta_proposta_truco()` em `partida.py` para obter a decisão da IA após a proposta.
5. Substituir `pedir_carta_para_jogar()` por `pedir_carta_ou_truco()` no frontend abstrato.
6. Implementar `pedir_carta_ou_truco()` no frontend terminal com a opção "T" para truco.
7. Tratar `EstadoPropostaTruco` em `_processar_estados` para encadear a resposta da IA.

**Desafio:** Por que a proposta de truco é dividida em dois estados (`EstadoPropostaTruco` + `EstadoRespostaTruco`) em vez de um único estado? Como isso beneficia a separação entre exibição e lógica?

---

### Atividade 10: Propostas de Truco pela IA durante o Jogo

**Objetivo:** Permitir que a IA proponha truco/seis/nove/doze automaticamente após jogar uma carta, considerando a força da mão, o contexto do jogo e até mesmo blefando.

**Conceitos de POO:**
- **Método público vs. privado**: o método `forca_mao()` em `JogadorIA` expõe publicamente a força da mão, evitando o uso frágil de name mangling (`_JogadorIA__forca_relativa_mao`). Isso demonstra a importância de APIs estáveis entre módulos.
- **Propriedades de consulta**: o property `tem_proposta_pendente` em `Partida` permite que o frontend verifique se há uma proposta pendente sem acessar atributos privados diretamente.
- **Integração no fluxo**: após a IA jogar (`_ia_joga`), o método `verificar_proposta_ia()` é chamado antes de pedir a carta ao humano. Se a IA propor, o próximo estado é `EstadoPedirDecisaoTruco`.
- **Aleatoriedade controlada**: o uso de `random.random()` para blefe demonstra como adicionar comportamento estocástico a uma IA de forma controlada.
- **Fator de contexto**: a IA considera não só a força da mão, mas também as rodadas vencidas (`rodadas_vantagem`) para decidir se propõe truco.

**Tarefas:**
1. Adicionar o método público `forca_mao()` em `JogadorIA` para consulta externa.
2. Adicionar o property `tem_proposta_pendente` em `Partida` para o frontend verificar propostas pendentes.
3. Implementar `verificar_proposta_ia()` com lógica de força, contexto e blefe.
4. Integrar a verificação em `_ia_joga()` — após a IA jogar, verificar se ela quer propor truco.
5. Registrar o propositor em `_propositor_atual` para saber quem ganha se o outro correr.
6. Corrigir `_obter_propositor()` para usar `_propositor_atual` em vez de sempre retornar a IA.
7. Remover o acesso a `_pontuacao_proposta_pendente` do frontend, substituindo por `tem_proposta_pendente`.

**Desafio:** Por que a IA pode propor truco mesmo com uma mão fraca (blefe)? Como isso torna o jogo mais interessante e realista? Qual o risco de blefar demais?

---

### Atividade 11: Refatoração do Loop de Estados (`frontend.py`)

**Objetivo:** Refatorar o método `_processar_estados()` — que era um bloco gigante de 100+ linhas — em manipuladores individuais modulares, seguindo o princípio de responsabilidade única.

**Conceitos de POO:**
- **Princípio de Responsabilidade Única (SRP)**: cada método `_manipular_*` trata apenas um tipo de estado, facilitando leitura, teste e manutenção.
- **Padrão Command/Dispatcher**: `_manipular_estado()` atua como um dispatcher que encaminha cada estado para o manipulador correto.
- **Métodos auxiliares**: `_manipular_inicio_mao()` e `_manipular_vencedor_rodada()` encapsulam a lógica de transição de estados complexos.
- **Legibilidade**: o loop principal `_processar_estados()` passa de 100+ linhas para 10 linhas, com a lógica delegada a métodos nomeados.

**Tarefas:**
1. Criar o método `_manipular_estado()` como dispatcher central.
2. Extrair `_manipular_pedir_carta()` para tratar a escolha de carta ou proposta de truco.
3. Extrair `_manipular_proposta_truco()` para processar a resposta da IA.
4. Extrair `_manipular_pedir_decisao_truco()` para tratar a decisão do humano.
5. Extrair `_manipular_resultado_mao()` e `_manipular_fim_partida()` para estados terminais.
6. Extrair `_manipular_informativo()` para estados que apenas avançam.
7. Extrair `_manipular_inicio_mao()` e `_manipular_vencedor_rodada()` para transições complexas.

**Desafio:** Como a refatoração facilita adicionar um novo tipo de estado no futuro? Compare a legibilidade do código antes e depois.

---

## Próximas Etapas Sugeridas

1. **Frontend PyQt6**: Criar `FrontendPyQt6` que herda de `Frontend` e usa widgets gráficos.
2. **Persistência de Placar**: Salvar o histórico de partidas em arquivo JSON.
3. **Jogo por Rede**: Implementar um frontend WebSocket para jogar com outros humanos.
4. **Testes Unitários**: Criar testes para cada módulo, começando por `baralho.py` e `partida.py`.
5. **Multi-jogador local**: Suportar 2x2 jogadores no mesmo terminal.
6. **IA com Aprendizado**: Implementar uma IA que melhora com base nas partidas anteriores.
