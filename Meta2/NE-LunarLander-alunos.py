import random
import copy
import numpy as np
import gymnasium as gym 
import os
from multiprocessing import Process, Queue

import matplotlib.pyplot as plt

# CONFIG
ENABLE_WIND = False
WIND_POWER = 15.0
TURBULENCE_POWER = 0.0
GRAVITY = -10.0
RENDER_MODE = 'human'
TEST_EPISODES = 1000
STEPS = 500

NUM_PROCESSES = os.cpu_count()
evaluationQueue = Queue()
evaluatedQueue = Queue()


nInputs = 8
nOutputs = 2
SHAPE = (nInputs,12,nOutputs)
GENOTYPE_SIZE = 0
for i in range(1, len(SHAPE)):
    GENOTYPE_SIZE += SHAPE[i-1]*SHAPE[i]

POPULATION_SIZE = 100
NUMBER_OF_GENERATIONS = 100
PROB_CROSSOVER = 0.5

PROB_MUTATION = 0.008
STD_DEV = 0.2


ELITE_SIZE = 1

def network(shape, observation,ind):
    #Computes the output of the neural network given the observation and the genotype
    x = observation[:]
    for i in range(1,len(shape)):
        y = np.zeros(shape[i])
        for j in range(shape[i]):
            for k in range(len(x)):
                y[j] += x[k]*ind[k+j*len(x)]
        x = np.tanh(y)
    return x

def check_successful_landing(observation):
    #Checks the success of the landing based on the observation
    x = observation[0]
    vy = observation[3]
    theta = observation[4]
    contact_left = observation[6]
    contact_right = observation[7]

    legs_touching = contact_left == 1 and contact_right == 1

    on_landing_pad = abs(x) <= 0.2

    stable_velocity = vy > -0.2
    stable_orientation = abs(theta) < np.deg2rad(20)
    stable = stable_velocity and stable_orientation
 
    if legs_touching and on_landing_pad and stable:
        return True
    return False




def objective_function(observation_history):
    # Vamos olhar para as ultimas 3 observações
    last_observation = np.mean(observation_history[-3:], axis = 0)
    
    # Extração dos parâmetros:
    x_dist = last_observation[0]    # Distância horizontal ao centro
    y_vel  = last_observation[3]    # Velocidade vertical
    angle  = last_observation[4]    # Ângulo (em radianos)

    # --- Cálculo da Qualidade (Fitness) ---
    

    # 1. Penalizar a distância horizontal (queremos x perto de 0)
    fitness = -abs(x_dist) * 100
    
    # 2. Penalizar a velocidade vertical 
    # (Se cair muito rápido, o valor de y_vel é muito negativo, ex: -1.5)
    # Queremos que no momento do toque a velocidade seja próxima de 0.
    fitness -= abs(y_vel) * 50
    
    # 3. Penalizar o ângulo 
    # (Queremos o lander o mais "em pé" possível, ou seja, ângulo 0)
    fitness -= abs(angle) * 50

    # 4. Bónus de Sucesso
    success = check_successful_landing(last_observation)
    if success:
        fitness += 500  # Recompensa por pousar em segurança
        
    return fitness, success



def simulate(genotype, render_mode = None, seed=None, env = None):
    #Simulates an episode of Lunar Lander, evaluating an individual
    env_was_none = env is None
    if env is None:
        env = gym.make("LunarLander-v3", render_mode =render_mode, 
        continuous=True, gravity=GRAVITY, 
        enable_wind=ENABLE_WIND, wind_power=WIND_POWER, 
        turbulence_power=TURBULENCE_POWER)    
        
    observation, info = env.reset(seed=seed)

    observation_history = [observation]
    for _ in range(STEPS):
        #Chooses an action based on the individual's genotype
        action = network(SHAPE, observation, genotype)
        observation, reward, terminated, truncated, info = env.step(action)        
        observation_history.append(observation)

        if terminated == True or truncated == True:
            break
    
    if env_was_none:    
        env.close()

    return objective_function(observation_history)

def evaluate(evaluationQueue, evaluatedQueue):
    #Evaluates individuals until it receives None
    #This function runs on multiple processes
    
    env = gym.make("LunarLander-v3", render_mode =None, 
        continuous=True, gravity=GRAVITY, 
        enable_wind=ENABLE_WIND, wind_power=WIND_POWER, 
        turbulence_power=TURBULENCE_POWER)    
    while True:
        ind = evaluationQueue.get()

        if ind is None:
            break
        
        # alterado para obter um accuracy melhor do genotipo. Obtendo uma media, faz com que o resultado seja livre de ruidos de uma só execução   
        N = 1
        fitnesses = [simulate(ind['genotype'], seed=None, env=env)[0] for _ in range(N)]
        ind['fitness'] = np.mean(fitnesses)

        evaluatedQueue.put(ind)
    env.close()
    
def evaluate_population(population):
    #Evaluates a list of individuals using multiple processes
    for i in range(len(population)):
        evaluationQueue.put(population[i])
    new_pop = []
    for i in range(len(population)):
        ind = evaluatedQueue.get()
        new_pop.append(ind)
    return new_pop

def generate_initial_population():
    #Generates the initial population
    population = []
    for i in range(POPULATION_SIZE):
        #Each individual is a dictionary with a genotype and a fitness value
        #At this time, the fitness value is None
        #The genotype is a list of floats sampled from a uniform distribution between -1 and 1
        
        genotype = []
        for j in range(GENOTYPE_SIZE):
            genotype += [random.uniform(-1,1)]
        population.append({'genotype': genotype, 'fitness': None})
    return population





#------------------Funções adicionadas para maior percepção-----------------------#


def tournament_selection(population, k=20): # Considerar afinar o parâmetro
    #Escolhe k indivíduos aleatórios
    tournament = random.sample(population, k)
    
    #Retorna o melhor do torneio
    winner = max(tournament, key=lambda ind: ind['fitness'])
    return winner




def roulette_wheel_selection(population):
    # Handle empty population
    if not population:
        return None

    # For LunarLander, fitness is often negative. 
    # We shift everyone's fitness so the minimum is at least a small positive number.
    min_fitness = min(ind['fitness'] for ind in population)
    
    # Use an offset so even the worst individual has a tiny chance (and total_fitness > 0)
    offset = abs(min_fitness) + 1.0
    
    total_fitness = sum(ind['fitness'] + offset for ind in population)
    pick = random.uniform(0, total_fitness)
    
    current = 0
    for ind in population:
        current += (ind['fitness'] + offset)
        if current >= pick:
            return ind
            
    # Fallback: If floating point errors happen, return the last individual
    return population[-1]



def Two_point_Crossover(p1, p2):
    genotype1 = p1['genotype']
    genotype2 = p2['genotype']
    
    point1 = random.randint(1, GENOTYPE_SIZE - 2)
    point2 = random.randint(point1 + 1, GENOTYPE_SIZE - 1)
    
    filho1 = genotype1[:point1] + genotype2[point1:point2] + genotype1[point2:]
    filho2 = genotype2[:point1] + genotype1[point1:point2] + genotype2[point2:]
    
    # Para determinar o filho com maior fitness tem que se fazer uma avaliação 
    
    # Devolve um dos filhos aleatoriamente — a avaliação fica para evaluate_population
    return {'genotype': random.choice([filho1, filho2]), 'fitness': None}
    
    
def uniform_crossover(p1, p2):
    g1 = p1['genotype']
    g2 = p2['genotype']
    
    child = []
    for i in range(GENOTYPE_SIZE):
        if random.random() < 0.5:
            child.append(g1[i])
        else:
            child.append(g2[i])
    
    return {'genotype': child, 'fitness': None}


def arithmetic_crossover(p1, p2):
    g1 = p1['genotype']
    g2 = p2['genotype']
    
    alpha = random.random()  # entre 0 e 1
    
    child = []
    for i in range(GENOTYPE_SIZE):
        gene = alpha * g1[i] + (1 - alpha) * g2[i]
        child.append(gene)
    
    return {'genotype': child, 'fitness': None}
    
    
    
def gaussian_mutation(individual):
    mutated = [
        max(-1, min(1, gene + random.gauss(0, STD_DEV))) 
        if random.random() < PROB_MUTATION 
        else gene
        for gene in individual['genotype']
    ]
    return {'genotype': mutated, 'fitness': None}
    


'''     
def uniform_mutation(individual):
    mutated = [
        # Adiciona um valor aleatório uniforme entre -STD_DEV e STD_DEV
        # O max(-1, min(1, ...)) garante que o gene não ultrapassa os limites físicos dos motores [-1, 1]
        max(-1, min(1, gene + random.uniform(-STD_DEV, STD_DEV))) 
        if random.random() < PROB_MUTATION 
        else gene
        for gene in individual['genotype']
    ]
    return {'genotype': mutated, 'fitness': None}
'''
    
#--------------------------------------END-----------------------------------------#

def parent_selection(population):
    #Select an individual from the population
    
    # A Estratégia de escolha dos parents vai basear-se abordagem elitísta
        #Para isto vamos usar a tournament selection. Em que a probabilidade de escolha de um indivíduo depende da sua fitness e tambem de ser escolhida na primeira escolha aleatoria no grupo 
        #Consideramos tournament selection visto que dá mais probabilidade de escolha a elementos mais aptos, permitindo explorar regiões mais promissoras devido a 1ª escolha aleatoria de individuos.
        #Esta estratégia também é a mais indicada para uma população pequena. Para um aumento da populacao inicial, considerar a experimentação de roulet wheel.     
    return roulette_wheel_selection(population)

def crossover(p1, p2):
    #Create an offspring from the individuals p1 and p2
    
    # Para a implementação do crossover escolhemos o two point crossover para populações reduzidas ( < 500, exemplo ) visto que permite manter uma maior diversidade de genótipo.
    # Esta diversidade é importante para manter o variedade de genes e permitir chegar a melhores soluções.
    
    return Two_point_Crossover(p1, p2)

def mutation(p):
    #Mutate the individual p
    
    #Para a implementação de mutation escolhemos a mutação uniforme visto para populações reduzidas visto que a diversidade é reduzida.
    #Para evitar a destruição de genes, causamos ruidos moderados (sigma =  0.1) nos genes. Estes ruidos moderados causam uma pequena alteração em cada gene
    #Portanto a funcao devolve um genótipo alterado num distribuição uniforme
    
    return gaussian_mutation(p) 
    
def survival_selection(population, offspring):
    #reevaluation of the elite
    offspring.sort(key = lambda x: x['fitness'], reverse=True)
    p = evaluate_population(population[:ELITE_SIZE])
    new_population = p + offspring[ELITE_SIZE:]
    new_population.sort(key = lambda x: x['fitness'], reverse=True)
    return new_population    
        
def evolution():
    #Create evaluation processes
    evaluation_processes = []
    for i in range(NUM_PROCESSES):
        evaluation_processes.append(Process(target=evaluate, args=(evaluationQueue, evaluatedQueue)))
        evaluation_processes[-1].start()
    
    #Create initial population
    bests = []
    population = list(generate_initial_population())
    population = evaluate_population(population)
    population.sort(key = lambda x: x['fitness'], reverse=True)
    best = (population[0]['genotype']), population[0]['fitness']
    bests.append(best)
    
    #Iterate over generations
    for gen in range(NUMBER_OF_GENERATIONS):
        offspring = []
        
        #create offspring
        while len(offspring) < POPULATION_SIZE:
            if random.random() < PROB_CROSSOVER:
                p1 = parent_selection(population)
                p2 = parent_selection(population)
                ni = crossover(p1, p2)

            else:
                ni = parent_selection(population)
                
            ni = mutation(ni)
            offspring.append(ni)
            
        #Evaluate offspring
        offspring = evaluate_population(offspring)

        #Apply survival selection
        population = survival_selection(population, offspring)
        
        #Print and save the best of the current generation
        best = (population[0]['genotype']), population[0]['fitness']
        bests.append(best)
        print(f'Best of generation {gen}: {best[1]}')

    #Stop evaluation processes
    for i in range(NUM_PROCESSES):
        evaluationQueue.put(None)
    for p in evaluation_processes:
        p.join()
        
    #Return the list of bests
    return bests

def load_bests(fname):
    #Load bests from file
    bests = []
    with open(fname, 'r') as f:
        for line in f:
            fitness, shape, genotype = line.split('\t')
            bests.append(( eval(fitness),eval(shape), eval(genotype)))
    return bests

if __name__ == '__main__':

    #Pick a setting from below
    #--to evolve the controller--    
    evolve = False
    render_mode = None

    #--to test the evolved controller without visualisation--
    #evolve = False
    #render_mode = None

    #--to test the evolved controller with visualisation--
    #evolve = False
    #render_mode = 'human'
    
    
    if evolve:
        #evolve individuals
        n_runs = 5
        seeds = [964, 952, 364, 913, 140, 726, 112, 631, 881, 844, 965, 672, 335, 611, 457, 591, 551, 538, 673, 437, 513, 893, 709, 489, 788, 709, 751, 467, 596, 976]
        for i in range(n_runs):    
            random.seed(seeds[i])
            bests = evolution()
            with open(f'log{i}.txt', 'w') as f:
                for b in bests:
                    f.write(f'{b[1]}\t{SHAPE}\t{b[0]}\n')

                
    else:
        filenames = [f'log{i}.txt' for i in range(5)]
        results = []
        
        # Criamos uma figura grande para os 5 gráficos
        plt.figure(figsize=(15, 10))

        for idx, filename in enumerate(filenames):
            # 1. Carregar dados para o gráfico de convergência
            bests = load_bests(filename)
            generations_fitness = [b[0] for b in bests]
            
            # 2. Testar o melhor indivíduo para obter a taxa de sucesso
            # Usamos o último da lista (final da evolução)
            b = bests[-1]
            SHAPE = b[1]
            ind = b[2]
            
            fit_total, success_total = 0, 0
          
            ntests = TEST_EPISODES 
            
            print(f"A testar {filename}...")
            for _ in range(ntests):
                f, s = simulate(ind, render_mode=render_mode, seed=None)
                fit_total += f
                success_total += s
            
            success_rate = (success_total / ntests) * 100
            avg_fitness = fit_total / ntests
            results.append((avg_fitness, success_rate/100))

            # 3. Criar o Subplot associado
            plt.subplot(2, 3, idx + 1)
            plt.plot(generations_fitness, color='blue', linewidth=2)
            
            # Título dinâmico com a taxa de sucesso
            plt.title(f"{filename}\nSucesso: {success_rate:.1f}%", fontsize=12, fontweight='bold')
            plt.xlabel("Geração")
            plt.ylabel("Fitness (Melhor da Gen)")
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Adiciona uma linha horizontal no 0 para referência
            plt.axhline(0, color='red', linewidth=0.8, linestyle='-')

        plt.tight_layout()
        plt.savefig('graficos_convergencia.png')
        print("Gráfico guardado como 'graficos_convergencia.png'")


