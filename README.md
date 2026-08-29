# 🃏 Jogo de Truco

## 📚 Sobre o Projeto

Este projeto tem como objetivo desenvolver um jogo simplificado de **Truco Paulista**, utilizando os conceitos de **Programação Orientada a Objetos (POO)**.

A aplicação deverá permitir que um jogador humano dispute uma partida de Truco contra um jogador controlado por uma **Inteligência Artificial (IA)**.

O foco principal do projeto não é apenas fazer o jogo funcionar, mas também aplicar corretamente conceitos como:

- Classes e objetos;
- Encapsulamento;
- Herança e polimorfismo, quando apropriado;
- Abstração;
- Enumerações;
- Composição entre objetos;
- Separação de responsabilidades;
- Organização e modelagem de um domínio;
- Desenvolvimento de uma estratégia para tomada de decisão da IA.

---

# 🎯 Objetivo

Implementar um jogo de **Truco Paulista simplificado**, disputado inicialmente entre:

> 👤 **Jogador Humano** × 🤖 **Jogador controlado pela IA**

A partida deverá seguir as regras básicas do Truco, envolvendo:

- Baralho;
- Distribuição de cartas;
- Disputa de mãos;
- Disputa de rodadas;
- Pontuação;
- Pedidos de Truco;
- Decisões tomadas pela Inteligência Artificial.

O jogo deverá ser desenvolvido utilizando **Programação Orientada a Objetos**, evitando uma implementação baseada exclusivamente em funções e variáveis globais.

---

# 🃏 Como funciona o jogo?

Uma partida é disputada entre dois jogadores.

Cada jogador recebe **3 cartas** no início de cada rodada.

Uma rodada pode possuir até **3 mãos**.

Em cada mão:

1. Cada jogador escolhe uma carta de sua mão.
2. As cartas são comparadas.
3. O jogador que possuir a carta mais forte vence a mão.
4. As cartas utilizadas são removidas da mão dos jogadores.

O jogador que vencer **2 mãos** vence a rodada.

A partida continua até que um dos jogadores alcance a quantidade máxima de pontos definida para o jogo.

Neste projeto, inicialmente, a partida deverá terminar quando um jogador atingir:

> 🏆 **12 pontos**

---

# 🂠 O Baralho

O jogo utilizará um baralho simplificado com **40 cartas**, composto por quatro naipes:

- ♦️ Ouros;
- ♥️ Copas;
- ♠️ Espadas;
- ♣️ Paus.

Os valores das cartas serão:

```text
4, 5, 6, 7, Q, J, K, A, 2 e 3
```

As cartas **8, 9 e 10 não fazem parte do baralho utilizado**.

Cada valor deverá existir nos quatro naipes.

Portanto:

```text
10 valores × 4 naipes = 40 cartas
```

---

# ⚔️ Força das Cartas

No Truco, as cartas não seguem a ordem tradicional de um baralho.

Para este projeto simplificado, as cartas deverão possuir a seguinte ordem de força:

```text
3 > 2 > A > K > J > Q > 7 > 6 > 5 > 4
```

Ou seja:

- O `3` é a carta mais forte;
- O `4` é a carta mais fraca.

Exemplo:

```text
Jogador: 2♠
IA: A♥
```

Como:

```text
2 > A
```

O jogador vence a mão.

---

# 🎮 Rodadas e Mãos

Cada rodada começa com os dois jogadores recebendo:

```text
3 cartas
```

Uma rodada pode possuir até:

```text
3 mãos
```

Cada mão funciona da seguinte forma:

1. O jogador humano escolhe uma carta.
2. A IA escolhe uma carta.
3. As cartas são reveladas.
4. As cartas são comparadas.
5. O vencedor da mão é determinado.

O jogador que vencer **duas mãos** vence automaticamente a rodada.

Exemplo:

```text
Mão 1 → Jogador vence
Mão 2 → IA vence
Mão 3 → Jogador vence

Resultado: Jogador vence a rodada.
```

---

# 🤝 Empate de uma Mão

Caso os dois jogadores joguem cartas de mesma força, a mão deverá ser considerada empatada.

O aluno deverá definir e implementar uma regra clara para lidar com essa situação.

Algumas possibilidades incluem:

- Considerar a mão empatada;
- Dar vantagem ao jogador que venceu a mão anterior;
- Utilizar regras simplificadas específicas para o projeto.

O importante é que a regra escolhida esteja:

- Documentada;
- Implementada corretamente;
- Aplicada de maneira consistente durante toda a partida.

---

# 📢 Truco e Apostas

Inicialmente, cada rodada vale:

```text
1 ponto
```

Durante uma rodada, um jogador pode pedir:

> 🃏 **TRUCO!**

Quando isso acontece, o adversário deverá decidir como responder.

As possibilidades são:

- ✅ Aceitar;
- ❌ Recusar;
- 📈 Aumentar a aposta.

A progressão de pontos será:

```text
1 → 3 → 6 → 9 → 12
```

Por exemplo:

```text
Rodada atual vale: 1 ponto

Jogador pede TRUCO!

IA aceita.

A rodada passa a valer: 3 pontos
```

Posteriormente:

```text
Jogador pede 6!

Adversário aceita.

A rodada passa a valer: 6 pontos
```

E assim sucessivamente:

```text
1 → 3 → 6 → 9 → 12
```

---

## ❌ Recusa de uma Aposta

Caso um jogador recuse uma aposta, o adversário vence a rodada imediatamente.

Nesse caso, o vencedor recebe os pontos correspondentes ao valor anterior da aposta.

Exemplo:

```text
Rodada vale 3 pontos.

Jogador pede 6.

IA recusa.
```

O jogador que pediu `6` vence a rodada e recebe:

```text
3 pontos
```

---

# 🤖 Inteligência Artificial

O jogo deverá possuir um jogador controlado por uma **Inteligência Artificial**.

A IA será responsável por tomar decisões durante a partida.

Entre essas decisões estão:

- Escolher qual carta jogar;
- Decidir se aceita uma aposta;
- Decidir se recusa uma aposta;
- Decidir se aumenta uma aposta;
- Decidir quando pedir Truco.

---

## 🧠 Estratégia da IA

A estratégia utilizada pela Inteligência Artificial **deverá ser desenvolvida pelo aluno**.

Uma implementação extremamente básica poderia ser:

```text
Escolher uma carta aleatoriamente.
```

Por exemplo:

```java
Carta carta = cartas.get(random.nextInt(cartas.size()));
```

Embora essa abordagem possa ser utilizada como ponto de partida, ela não representa uma estratégia interessante.

O objetivo é que o aluno desenvolva uma IA capaz de tomar decisões com base no estado atual da partida.

---

## 💡 Sugestões para a estratégia da IA

A IA poderá considerar diversos fatores.

### 🃏 Força das cartas

A IA pode analisar as cartas disponíveis em sua mão.

Por exemplo:

```text
3, 2, A
```

representa uma mão muito forte.

Enquanto:

```text
4, 5, 6
```

representa uma mão fraca.

A IA pode utilizar essa informação para decidir:

- Se deve pedir Truco;
- Se deve aceitar uma aposta;
- Qual carta jogar.

---

### ⚔️ Cartas já jogadas

A IA pode considerar quais cartas já foram utilizadas durante a rodada.

Por exemplo:

```text
IA possui:

3
5
4
```

Se a IA possui uma carta muito forte, pode decidir guardá-la para uma situação estratégica.

---

### 📊 Situação da rodada

A IA pode considerar o resultado das mãos anteriores.

Exemplo:

```text
Jogador: 1 vitória
IA: 0 vitórias
```

A IA está perdendo a rodada e pode precisar adotar uma estratégia diferente.

Outro exemplo:

```text
Jogador: 0 vitórias
IA: 1 vitória
```

Nesse caso, a IA pode jogar de maneira mais conservadora.

---

### 🏆 Pontuação da partida

A IA também pode considerar a pontuação geral.

Exemplo:

```text
Jogador: 11 pontos
IA: 5 pontos
```

A IA pode perceber que permitir uma rodada valendo muitos pontos pode ser perigoso.

Da mesma forma:

```text
Jogador: 5 pontos
IA: 11 pontos
```

A IA pode adotar uma estratégia mais agressiva para tentar encerrar a partida.

---

# 🏗️ Requisitos de Implementação

A aplicação deverá ser desenvolvida utilizando **Programação Orientada a Objetos**.

O sistema deverá possuir uma modelagem adequada para representar os elementos do jogo.

Uma possível estrutura inicial é apresentada abaixo.

---

# 📦 Entidades do Sistema

## 🃏 Carta

A classe `Carta` representa uma carta do baralho.

Ela deverá possuir, pelo menos:

```text
- valor
- naipe
```

Exemplo:

```text
3 de Espadas
A de Copas
7 de Ouros
```

Uma carta também deverá ser capaz de informar sua força.

Exemplo:

```java
int getForca();
```

Também é recomendado que a própria classe `Carta` possua um comportamento para comparar sua força com outra carta.

Por exemplo:

```java
Resultado comparar(Carta outraCarta);
```

ou:

```java
boolean ehMaisForteQue(Carta outraCarta);
```

Evite concentrar toda a lógica de comparação de cartas na classe `Jogo`.

---

# 🔢 Valor ou Rank

É recomendado representar os valores das cartas utilizando uma enumeração.

Exemplo:

```java
public enum Rank {
    QUATRO,
    CINCO,
    SEIS,
    SETE,
    DAMA,
    VALETE,
    REI,
    AS,
    DOIS,
    TRES
}
```

A enumeração pode possuir informações adicionais, como:

```text
- símbolo da carta;
- força da carta.
```

Por exemplo:

```java
TRES("3", 10)
```

Dessa forma, a regra de força das cartas ficará encapsulada no próprio domínio.

---

# ♠️ Naipe

Os naipes também podem ser representados por uma enumeração.

Exemplo:

```java
public enum Naipe {
    OUROS,
    COPAS,
    ESPADAS,
    PAUS
}
```

---

# 🂠 Baralho

A classe `Baralho` será responsável por gerenciar as cartas disponíveis.

Entre suas responsabilidades estão:

- Criar as 40 cartas;
- Armazenar as cartas;
- Embaralhar o baralho;
- Distribuir cartas;
- Informar se ainda existem cartas disponíveis.

Exemplo de operações:

```java
embaralhar();
comprarCarta();
temCartas();
```

O baralho não deve ser responsável por controlar a pontuação da partida ou decidir quem venceu uma rodada.

---

# 👤 Jogador

A classe `Jogador` representa um participante da partida.

Ela deverá possuir informações como:

```text
- nome;
- cartas na mão;
- pontuação.
```

Além disso, deverá possuir comportamentos relacionados ao jogador.

Por exemplo:

```text
- receberCarta();
- jogarCarta();
- possuirCartas();
- receberPontos();
```

A mão do jogador deverá possuir, inicialmente:

```text
3 cartas
```

---

# 🤖 JogadorIA

A Inteligência Artificial pode ser implementada como uma especialização de `Jogador`.

Por exemplo:

```text
Jogador
    ├── JogadorHumano
    └── JogadorIA
```

O `JogadorIA` poderá possuir comportamentos específicos, como:

```java
Carta escolherCartaParaJogar();
```

Também poderá possuir métodos relacionados às decisões de apostas:

```java
DecisaoTruco responderTruco();
```

ou:

```java
boolean aceitarTruco();
```

A implementação exata fica a critério do aluno.

---

# 🧠 Estratégia da IA

Uma possibilidade interessante é separar a estratégia da IA do próprio jogador.

Por exemplo:

```text
JogadorIA
        |
        ▼
EstrategiaIA
```

Nesse caso:

```java
public interface EstrategiaIA {

    Carta escolherCarta(Contexto context);
}
```

Diferentes estratégias poderiam ser implementadas:

```text
EstrategiaAleatoria
EstrategiaBasica
EstrategiaAgressiva
EstrategiaConservadora
```

Isso permitiria trocar o comportamento da IA sem alterar a classe principal do jogador.

Essa abordagem não é obrigatória, mas é fortemente recomendada.

---

# 🔄 Rodada

É recomendável criar uma classe específica para representar uma rodada.

A `Rodada` poderá ser responsável por:

- Controlar as mãos disputadas;
- Registrar o vencedor de cada mão;
- Controlar o valor atual da rodada;
- Controlar os pedidos de Truco;
- Determinar o vencedor da rodada.

Exemplo:

```text
Rodada
    |
    ├── Jogador
    ├── JogadorIA
    │
    ├── Mão 1
    ├── Mão 2
    └── Mão 3
```

---

# ✋ Mão

Uma possível melhoria na modelagem é criar uma classe `Mao`.

Essa classe pode representar uma disputa individual entre os jogadores.

Ela poderia armazenar:

```text
- carta jogada pelo jogador;
- carta jogada pela IA;
- vencedor da mão.
```

Exemplo:

```text
Jogador joga: 7♠
IA joga: A♥

Vencedor: IA
```

---

# 🎮 Partida

A classe `Partida` deverá controlar o fluxo geral do jogo.

Entre suas responsabilidades:

- Criar e iniciar rodadas;
- Controlar a pontuação dos jogadores;
- Determinar quando uma rodada termina;
- Determinar quando a partida termina;
- Declarar o vencedor da partida.

Exemplo:

```text
Partida

Jogador: 7 pontos
IA: 9 pontos

↓

Nova rodada

↓

Resultado da rodada

↓

Atualização da pontuação
```

A partida termina quando um jogador atingir:

```text
12 pontos
```

---

# 🖥️ Interface do Jogo

A aplicação não precisa ser implementada como uma API REST.

A interação com o usuário poderá ser feita inicialmente através de uma interface de console.

Exemplo:

```text
================================
        JOGO DE TRUCO
================================

Jogador: Kleber
IA: Computador

Pontuação:
Jogador: 5
IA: 4

Suas cartas:

[1] 3 de Paus
[2] 7 de Copas
[3] A de Espadas

Escolha uma carta:
>
```

Durante o jogo, o sistema deverá informar claramente:

- Cartas disponíveis;
- Carta jogada pela IA;
- Vencedor da mão;
- Vencedor da rodada;
- Pontuação atual;
- Valor atual da rodada;
- Pedidos de Truco;
- Decisões da IA;
- Vencedor da partida.

---

# 🚫 O que a IA não deve conhecer?

A IA **não deve ter acesso às cartas do jogador humano**.

Por exemplo, esta abordagem seria incorreta:

```java
if (jogadorHumano.getCartas().contains(cartaMuitoForte)) {
    ...
}
```

A IA deverá tomar decisões utilizando apenas informações que seriam visíveis para um jogador real.

Por exemplo:

- Suas próprias cartas;
- Cartas já jogadas;
- Resultado das mãos;
- Pontuação atual;
- Valor atual da aposta.

Esse requisito é importante para evitar que a IA "trapaceie".

---

# 💡 Dicas de Implementação

## 1️⃣ Comece pelo domínio

Antes de criar menus e interações com o usuário, implemente corretamente as entidades principais:

```text
Carta
Baralho
Jogador
JogadorIA
Mao
Rodada
Partida
```

Teste essas classes individualmente.

---

## 2️⃣ Utilize enums

Utilize `enum` para representar conceitos que possuem uma quantidade fixa de valores.

Por exemplo:

```text
Naipe
Rank
DecisaoTruco
ResultadoMao
```

Isso evita o uso excessivo de `String`.

Exemplo:

❌ Evite:

```java
if (decisao.equals("ACEITAR"))
```

✅ Prefira:

```java
if (decisao == DecisaoTruco.ACEITAR)
```

---

## 3️⃣ Evite colocar toda a lógica no `main`

O método `main()` não deve conter toda a lógica do jogo.

Evite algo semelhante a:

```java
public static void main(String[] args) {

    // cria cartas

    // embaralha

    // distribui

    // compara cartas

    // calcula pontos

    // controla rodadas

    // controla truco

    // ...
}
```

Prefira utilizar o `main()` apenas para iniciar a aplicação.

Por exemplo:

```java
public static void main(String[] args) {

    Jogo jogo = new Jogo();
    jogo.iniciar();
}
```

A lógica deverá estar distribuída entre as classes responsáveis.

---

## 4️⃣ Cada classe deve possuir responsabilidades claras

Exemplo:

### Carta

Responsável por:

```text
Representar uma carta.
```

### Baralho

Responsável por:

```text
Gerenciar as cartas do baralho.
```

### Jogador

Responsável por:

```text
Gerenciar o estado e ações de um jogador.
```

### Rodada

Responsável por:

```text
Controlar uma rodada.
```

### Partida

Responsável por:

```text
Controlar a partida completa.
```

Evite criar uma única classe que faça tudo.

---

## 5️⃣ Implemente a IA progressivamente

Uma boa estratégia é desenvolver a IA em etapas.

### Etapa 1

A IA escolhe cartas aleatoriamente.

```text
IA Aleatória
```

### Etapa 2

A IA analisa a força das próprias cartas.

```text
IA Básica
```

### Etapa 3

A IA considera o resultado da rodada.

```text
IA Estratégica
```

### Etapa 4

A IA considera:

- Pontuação;
- Cartas disponíveis;
- Histórico da rodada;
- Risco das apostas.

```text
IA Avançada
```

Essa evolução permite melhorar gradualmente o comportamento da IA.

---

# 🚀 Funcionalidades Futuras

A implementação inicial deverá ser:

> 👤 Humano × 🤖 IA

Entretanto, como evolução futura do projeto, o aluno poderá implementar novas funcionalidades.

---

## 👥 Truco em Duplas

Uma possível evolução é permitir partidas com quatro jogadores.

Exemplo:

```text
Jogador 1 + Jogador 2

        VS

Jogador 3 + Jogador 4
```

Nesse caso, seria necessário modelar conceitos adicionais, como:

- Equipe;
- Parceiros;
- Ordem dos jogadores;
- Alternância entre os jogadores;
- Pontuação da dupla.

Uma possível estrutura seria:

```text
Partida
   |
   ├── Equipe A
   │      ├── Jogador
   │      └── IA
   │
   └── Equipe B
          ├── IA
          └── IA
```

Essa funcionalidade **não é obrigatória para a versão inicial**.

---

# 📋 Requisitos Mínimos

Para considerar o projeto funcional, ele deverá possuir:

- [ ] Baralho com 40 cartas;
- [ ] Quatro naipes;
- [ ] Ordem correta de força das cartas;
- [ ] Dois jogadores;
- [ ] Jogador humano;
- [ ] Jogador controlado por IA;
- [ ] Distribuição de três cartas;
- [ ] Disputa de até três mãos;
- [ ] Controle de vitória da rodada;
- [ ] Sistema de pontuação;
- [ ] Pedidos de Truco;
- [ ] Aceitar ou recusar apostas;
- [ ] IA capaz de escolher cartas;
- [ ] Estratégia de decisão desenvolvida pelo aluno;
- [ ] Partida até 12 pontos;
- [ ] Interface para interação com o jogador;
- [ ] Código organizado utilizando Programação Orientada a Objetos.

---

# ⭐ Desafios Extras

Os alunos que desejarem ir além da implementação mínima poderão adicionar:

- [ ] Estratégias mais avançadas para a IA;
- [ ] Diferentes níveis de dificuldade;
- [ ] Histórico das partidas;
- [ ] Sistema de estatísticas;
- [ ] Interface gráfica;
- [ ] Persistência de dados;
- [ ] Ranking de jogadores;
- [ ] Salvamento de partidas;
- [ ] Truco em duplas;
- [ ] Diferentes regras regionais do Truco;
- [ ] Manilhas;
- [ ] Interface gráfica utilizando JavaFX ou Swing.

---

# 🏆 Considerações Finais

Este projeto tem como objetivo permitir a aplicação prática dos conceitos de **Programação Orientada a Objetos** em um problema mais complexo e próximo de um sistema real.

Além da correta implementação das regras do jogo, será avaliada a qualidade da modelagem e da organização do código.

A pergunta principal que deve orientar o desenvolvimento é:

> **Qual objeto deveria ser responsável por esta ação?**

Evite criar classes excessivamente grandes e concentre cada responsabilidade no objeto que melhor representa aquele comportamento.

A implementação deve buscar um código:

- Organizado;
- Coeso;
- Fácil de entender;
- Fácil de testar;
- Fácil de modificar;
- Extensível para novas funcionalidades.

---

# 🎓 Bom desenvolvimento!

> 🃏 **TRUUUUUCOOOOO!!!**
