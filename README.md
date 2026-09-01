# 🚀 Lunar Lander: Agente Reativo & Neuroevolução

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gymnasium](https://img.shields.io/badge/Gymnasium-v3.0.0-green.svg)](https://gymnasium.farama.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Este repositório contém a implementação e comparação de duas abordagens distintas de Inteligência Artificial para resolver o ambiente contínuo **LunarLander-v3** do [Gymnasium](https://gymnasium.farama.org/environments/box2d/lunar_lander/):
1. **Agente Reativo baseado em Regras:** Controlo heurístico com janelas de tolerância e realimentação sensorial.
2. **IA Evolutiva / Neuroevolução:** Algoritmo Evolutivo (EA) para otimização dos pesos de uma Rede Neuronal Feedforward (MLP) utilizando multiprocessamento.

---

## 📋 Índice

- [Descrição do Problema](#-descrição-do-problema)
- [Parte 1: Agente Reativo](#-parte-1-agente-reativo)
  - [Arquitetura de Perceção e Ação](#arquitetura-de-perceção-e-ação)
  - [Lógica de Controlo](#lógica-de-controlo)
- [Parte 2: Neuroevolução (Algoritmo Evolutivo)](#-parte-2-neuroevolução-algoritmo-evolutivo)
  - [Arquitetura da Rede Neuronal](#arquitetura-da-rede-neuronal)
  - [Operadores Evolutivos & Fitness](#operadores-evolutivos--fitness)
  - [Grelha de Experiências (Meta 1 & Meta 2)](#grelha-de-experiências)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Requisitos e Instalação](#-requisitos-e-instalação)
- [Como Executar](#-como-executar)
- [Resultados Obtidos](#-resultados-obtidos)
- [Autores](#-autores)

---

## 🎯 Descrição do Problema

O objetivo do ambiente `LunarLander-v3` é aterrar uma nave espacial no centro da plataforma de aterragem $(x = 0)$, mantendo a velocidade e a inclinação dentro de limites de segurança.

* **Espaço de Estados (8 Perceções):**
  1. $x$: Posição horizontal
  2. $y$: Posição vertical
  3. $v_x$: Velocidade horizontal
  4. $v_y$: Velocidade vertical
  5. $\theta$: Ângulo de inclinação
  6. $v_\theta$: Velocidade angular
  7. `leg_left`: Contacto da perna esquerda com o solo ($0$ ou $1$)
  8. `leg_right`: Contacto da perna direita com o solo ($0$ ou $1$)
* **Espaço de Ações Contínuo (2 Saídas):**
  * `Main Engine` $[0, 1]$: Propulsor principal inferior.
  * `Side Engines` $[-1, 1]$: Propulsores laterais (esquerdo/direito).

---

## 🧠 Parte 1: Agente Reativo

O Agente Reativo utiliza regras condicionais e funções de controlo proporcional para tomar decisões em tempo real sem aprendizagem prévia.

### Arquitetura de Perceção e Ação
1. **Mapeamento de Perceções:**
   * Cálculo da velocidade vertical alvo ($v_{y, target} = -0.15$).
   * Cálculo da inclinação alvo ajustada ($\theta_{target} = \text{clip}(0.75x + 1.2v_x, -0.4, 0.4)$).
   * Correção de erro angular com amortecimento ($(\theta - \theta_{target}) \times 2.0 + v_\theta \times 1.5$).
   * Deteção de situações de emergência (ex: $v_y < -0.3$ ou desalinhamento a baixa altitude).

### Lógica de Controlo
* **Motor Principal:** Força proporcional ao erro de velocidade vertical e altitude, com reforço em descidas perigosas.
* **Motores Laterais (Zona Morta):** Aplicação de uma zona morta no intervalo $[-0.5, 0.5]$ para evitar oscilações excessivas no controlo de atitude da nave.

---

## 🧬 Parte 2: Neuroevolução (Algoritmo Evolutivo)

A segunda abordagem evolui os pesos de uma **Rede Neuronal Artificial (MLP)** de modo a encontrar a política de controlo ideal.

### Arquitetura da Rede Neuronal
* **Entradas:** 8 sensores do ambiente.
* **Camada Escondida:** 12 neurónios (Meta 1) / 24 neurónios (Meta 2) com ativação $\tanh$.
* **Saídas:** 2 controlos contínuos $[u_{\text{main}}, u_{\text{side}}]$.
* **Genótipo:** Vetor unidimensional codificando todas as matrizes de pesos da rede.

### Operadores Evolutivos & Fitness
* **Função de Aptidão (Fitness):** Penaliza desvios horizontais, velocidade de queda excessiva, inclinação angular e desalinhamento dos pés de aterragem.
* **Seleção de Progenitores:** *Tournament Selection* ($k=20$) vs. *Roulette Wheel Selection*.
* **Recombinação (Crossover):** *Uniform Crossover* vs. *Two-Point Crossover* (probabilidade de $0.5$ a $0.9$).
* **Mutação:** *Gaussian Mutation* ($\sigma = 0.2$) vs. *Uniform Mutation* (probabilidade de $0.008$ a $0.1$).
* **Elitismo:** Preservação do melhor indivíduo da geração anterior ($ELITE\_SIZE \in \{0, 1\}$).
* **Multiprocessamento:** Distribuição da avaliação da população por múltiplos processos concorrentes (`multiprocessing.Queue`).

### Grelha de Experiências
O algoritmo foi testado através de 8 experiências distintas parametrizadas da seguinte forma:

| Exp | Prob. Mutação ($\mathbf{P_m}$) | Prob. Crossover ($\mathbf{P_c}$) | Elitismo ($\mathbf{E}$) |
| :---: | :---: | :---: | :---: |
| **1** | $0.008$ | $0.5$ | 0 |
| **2** | $0.050$ / $0.100$ | $0.5$ | 0 |
| **3** | $0.008$ | $0.9$ | 0 |
| **4** | $0.050$ | $0.9$ | 0 |
| **5** | $0.008$ | $0.5$ | 1 |
| **6** | $0.050$ | $0.5$ | 1 |
| **7** | $0.008$ | $0.9$ | 1 |
| **8** | $0.050$ | $0.9$ | 1 |

---

## 📁 Estrutura do Repositório

```text
.
├── agente_reativo.py         # Agente reativo baseado em regras e controlo proporcional
├── AI_agent_withoutWind.py   # Neuroevolução no ambiente sem vento (12 neurónios ocultos)
├── AI_agent_withWind.py      # Neuroevolução no ambiente com vento e turbulência (24 neurónios ocultos)
└── README.md                 # Documentação do projeto
```

## 🛠️ Requisitos e Instalação

### **Pré-requisitos**
* **Python 3.10+** 
  *(Nota: As bibliotecas `random`, `copy`, `os` e `multiprocessing` pertencem à biblioteca padrão do Python e não requerem instalação).*

---

### **Bibliotecas Necessárias**

| Módulo Importado | Pacote `pip` | Função no Projeto |
| :--- | :--- | :--- |
| `numpy` | `numpy` | Computação vetorial e operações matriciais da rede neuronal |
| `gymnasium` | `gymnasium[box2d]` | Ambiente de simulação física do Lunar Lander (`LunarLander-v3`) |
| `matplotlib.pyplot` | `matplotlib` | Geração de gráficos comparativos de fitness ao longo das gerações |

---

### **Comando de Instalação Rápida**

Executa o seguinte comando no terminal (WSL / Linux / Windows) para instalar todas as dependências do projeto:

```bash
pip install "gymnasium[box2d]" numpy matplotlib pygame
