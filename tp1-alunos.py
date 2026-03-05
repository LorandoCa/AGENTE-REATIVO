import gymnasium as gym
import numpy as np
import pygame
import math

ENABLE_WIND = False
WIND_POWER = 15.0
TURBULENCE_POWER = 0.0
GRAVITY = -10.0
#RENDER_MODE = 'human'
RENDER_MODE = None #seleccione esta opção para não visualizar o ambiente (testes mais rápidos)
EPISODES = 1000
LIMIAR = 0.6

env = gym.make("LunarLander-v3", render_mode =RENDER_MODE, 
    continuous=True, gravity=GRAVITY, 
    enable_wind=ENABLE_WIND, wind_power=WIND_POWER, 
    turbulence_power=TURBULENCE_POWER)


def check_successful_landing(observation):
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
        print("Aterragem bem sucedida!")
        return True

    print("Aterragem falhada!")        
    return False
        
def simulate(steps=1000,seed=None, policy = None):    
    observ, _ = env.reset(seed=seed)
    for step in range(steps):
        action = policy(observ)

        observ, _, term, trunc, _ = env.step(action)

        if term or trunc:
            break

    success = check_successful_landing(observ)
    return step, success


#Perceptions
##TODO: Defina as suas perceções aqui
def perceptions(observation):
    x, y, vx, vy, theta, vtheta, leg_left, leg_right = observation
    return {
        # Estado vertical
        "queda_muito_rapida": vy < -0.9,
        "queda_rapida": vy < -0.4,
        "queda_moderada": vy < -0.25,
        "queda_lenta": vy > -0.2,
        
        # Estado horizontal
        "esquerda_do_centro": x < -0.2,
        "direita_do_centro": x > 0.2,
        "movendo_para_esquerda": vx < -0.5,
        "movendo_para_direita": vx > 0.5,
        
        # Orientação 
        "inclinado": abs(theta) > math.radians(8),
        "inclinado_para_esquerda": theta > 0,
        "velocidade_angular_alta": abs(vtheta) > 0.6,
        "velocidade_angular_para_esquerda": vtheta > 0,
        
        # Altura
        "alto": y > 1,
        "medio": y > 0.5,
        "baixo": y < LIMIAR,
        
        "pernas_no_chao": leg_left == 1 and leg_right == 1
    }
    

#Actions
##TODO: Defina as suas ações aqui

def acao_rodar_para_direita():
    return np.array([0.0, 1])     # rodar direita

def acao_rodar_para_esquerda():
    return np.array([0.0, -1])    # rodar esquerda

def acao_rodar_para_direita_leve():
    return np.array([0.0, 0.4])     # rodar direita

def acao_rodar_para_esquerda_leve():
    return np.array([0.0, -0.4])    # rodar esquerda

def acao_motor_potencia_muito_alta():
    return np.array([0.9, 0.0])

def acao_motor_potencia_media():
    return np.array([0.7, 0.0])

def acao_motor_potencia_alta():
    return np.array([0.8, 0.0])

def acao_motor_maximo():
    return np.array([1, 0.0])       # motor principal potência máxima

def action_correcao_eixo_esquerdo():
    return np.array([0.3, -0.6])

def action_correcao_eixo_direito():
    return np.array([0.6, 0.3])

def action_correcao_eixo_esquerdo_leve():
    return np.array([0.2, -0.5])

def action_correcao_eixo_direito_leve():
    return np.array([0.2, 0.5])

def no_action():
    return np.array([0.0, 0.0])  # sem ação


def reactive_agent(observation):
    ##TODO: Implemente aqui o seu agente reativo
    ##Substitua a linha abaixo pela sua implementação
    #action = env.action_space.sample()
    
    #print('observação:', observation)
    
    # Voltar a elevar a nave se estiver muito embaixo e fora da zona de pouso
    
    p = perceptions(observation)
    x, y, vx, vy, theta, vtheta, left_leg, right_leg = observation
    
    if left_leg == 1 and right_leg == 1:
        return np.array([0, 0])
    
    main = 0.0
    side = 0.0

    if vy < -0.14 : main = 0.2

    if abs(x) > 0.2:
        
        #Diminuir velocidade para quando estiver perto da plataforma
        if x < 0 : # do lado esquerdo da plataforma
            
            if vx > 0 and x > -0.6: #muito perto da plataforma nao é preciso mais impulso
                side = 0
            else:
                side = 0.51
                
        else: # do lado direito da plataforma
            
            if vx < 0 and x < 0.6: #muito perto da plataforma nao é preciso mais impulso
                side = 0
            else:
                side = -0.51

            
    if abs(vx) > 0.2:
        
        if vx > 0:
            side = -0.52
        else :
            side = 0.52
        
    #  Corrigir ângulo (suave)
    if theta < np.deg2rad(-4):
        side = -0.51
    elif theta > np.deg2rad(4):# angulo a definir margem de erro(inclinação min)
        side = 0.51
        
    # Controlar queda
    if vy < -0.2:
        main = 0.3
    
    # Salvar a nave de quedas fora da zona de pouso 
    if y <= 0.5 and abs(x) > 0.2:
        main = 0.4
        

    return np.array([main, side])
        

    
def keyboard_agent(observation):
    action = [0,0] 
    keys = pygame.key.get_pressed()
    
    print('observação:', observation)

    if keys[pygame.K_UP]:  
        action =+ np.array([1,0])
    if keys[pygame.K_LEFT]:  
        action =+ np.array( [0,-1])
    if keys[pygame.K_RIGHT]: 
        action =+ np.array([0,1])

    return action
    

success = 0.0
steps = 0.0
for i in range(EPISODES):
    st, su = simulate(steps=1000000, policy=reactive_agent)

    if su:
        steps += st
    success += su
    
    if su>0:
        print('Média de passos das aterragens bem sucedidas:', steps/success*100)
    print('Taxa de sucesso:', success/(i+1)*100)