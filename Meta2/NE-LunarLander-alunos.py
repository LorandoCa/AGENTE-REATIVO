import random
import copy
import numpy as np
import gymnasium as gym 
import os
from multiprocessing import Process, Queue

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
PROB_CROSSOVER = 0.9

PROB_MUTATION = 1.0/GENOTYPE_SIZE
STD_DEV = 0.1


ELITE_SIZE = 0

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
    #Computes the quality of the individual based 
    #on the horizontal distance to the landing pad, the vertical velocity and the angle
    #second_to_last_observation = observation_history[-2]
    #x = second_to_last_observation[0]
    #y = second_to_last_observation[1]
    #return -abs(x) - abs(y), check_successful_landing(observation_history[-1])
    
    ultima_obs = observation_history[-1]
    
    x = ultima_obs[0]
    y = ultima_obs[1]
    vx = ultima_obs[2]
    vy = ultima_obs[3]
    theta = ultima_obs[4]
    vtheta = ultima_obs[5]
    perna_esquerda = ultima_obs[6]
    perna_direita = ultima_obs[7]
    
    penalidade_distancia = abs(x) + abs(y)
    penalidade_velocidade = abs(vx) + abs(vy)
    penalidade_angulo = abs(theta) + abs(vtheta)
    
    fitness = 1 / (1 + (2 * penalidade_distancia) + (1.5 * penalidade_velocidade) + (1.2 * penalidade_angulo))    
    # como a expressao anterior calcula a penalidade total, o objetivo da função fitness é maximizar a probabilidade de sobrevivencia.
    # Então quanto maior o acúmulo de penalidade, menor é o fitness. Portanto, tem que se fazer o inverso.
    
    return fitness, check_successful_landing(ultima_obs)
    
    
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
            
        ind['fitness'] = simulate(ind['genotype'], seed = None, env = env)[0]
                
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


def tournament_selection(population, k=10): # Considerar afinar o parâmetro
    #Escolhe k indivíduos aleatórios
    tournament = random.sample(population, k)
    
    #Retorna o melhor do torneio
    winner = max(tournament, key=lambda ind: ind['fitness'])
    return winner




def roulette_wheel_selection(population):
    # 1. Soma total do fitness de todos os indivíduos
    total_fitness = sum(ind['fitness'] for ind in population)
    
    # 2. Gera um número aleatório entre 0 e o total
    pick = random.uniform(0, total_fitness)
    
    # 3. Percorre a população acumulando fitness até ultrapassar o pick
    current = 0
    for ind in population:
        current += ind['fitness']
        if current >= pick:
            return ind


def Two_point_Crossover(p1, p2):
    genotype1 = p1['genotype']
    genotype2 = p2['genotype']
    
    point1 = random.randint(1, GENOTYPE_SIZE - 2)
    point2 = random.randint(point1 + 1, GENOTYPE_SIZE - 1)
    
    filho1 = genotype1[:point1] + genotype2[point1:point2] + genotype1[point2:]
    filho2 = genotype2[:point1] + genotype1[point1:point2] + genotype2[point2:]
    
    # Para determinar o filho com maior fitness tem que se fazer uma avaliação 
    
    # Avalia cada filho
    fitness1 = simulate(filho1)[0]
    fitness2 = simulate(filho2)[0]
    
    # Retorna o filho com maior fitness
    if fitness1 > fitness2:
        return {'genotype': filho1, 'fitness': None}
    else:
        return {'genotype': filho2, 'fitness': None}
    
     
def gaussian_mutation(individual):
    mutated = [
        max(-1, min(1, gene + random.gauss(0, STD_DEV))) 
        if random.random() < PROB_MUTATION 
        else gene
        for gene in individual['genotype']
    ]
    return {'genotype': mutated, 'fitness': None}
    
    

#--------------------------------------END-----------------------------------------#

def parent_selection(population):
    #Select an individual from the population
    
    # A Estratégia de escolha dos parents vai basear-se abordagem elitísta
        #Para isto vamos usar a tournament selection. Em que a probabilidade de escolha de um indivíduo depende da sua fitness e tambem de ser escolhida na primeira escolha aleatoria no grupo 
        #Consideramos tournament selection visto que dá mais probabilidade de escolha a elementos mais aptos, permitindo explorar regiões mais promissoras devido a 1ª escolha aleatoria de individuos.
        #Esta estratégia também é a mais indicada para uma população pequena. Para um aumento da populacao inicial, considerar a experimentação de roulet wheel.     
    return tournament_selection(population, 10)

def crossover(p1, p2):
    #Create an offspring from the individuals p1 and p2
    
    # Para a implementação do crossover escolhemos o two point crossover para populações reduzidas ( < 500, exemplo ) visto que permite manter uma maior diversidade de genótipo.
    # Esta diversidade é importante para manter o variedade de genes e permitir chegar a melhores soluções.
    
    return Two_point_Crossover(p1, p2)

def mutation(p):
    #Mutate the individual p
    
    #Para a implementação de mutation escolhemos a mutação gaussiana visto para populações reduzidas visto que a diversidade é reduzida.
    #Para evitar a destruição de genes, causamos ruidos moderados (sigma =  0.1) nos genes. Estes ruidos moderados causam uma pequena alteração em cada gene
    #Portanto a funcao devolve um genótipo alterado num distribuição gaussiana
    
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
    evolve = True
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
        #test evolved individuals
        #pick the file to test
        filename = 'log0.txt'
        bests = load_bests(filename)
        b = bests[-1]
        SHAPE = b[1]
        ind = b[2]
            
        ind = {'genotype': ind, 'fitness': None}
            
            
        ntests = TEST_EPISODES

        fit, success = 0, 0
        for i in range(1,ntests+1):
            f, s = simulate(ind['genotype'], render_mode=render_mode, seed = None)
            fit += f
            success += s
        print(fit/ntests, success/ntests)
