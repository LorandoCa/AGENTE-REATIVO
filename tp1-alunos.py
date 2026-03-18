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



# TODO: Defina as suas perceções aqui
# --- PERCEÇÕES ---
def perceptions(observation):
    x, y, vx, vy, theta, vtheta, leg_left, leg_right = observation
    
    # Alvo de descida segura
    target_vy = -0.15
    # Alvo de inclinação para corrigir posição (x) e velocidade horizontal (vx)
    target_theta = np.clip(x * 0.75 + vx * 1.2, -0.4, 0.4)

    return {
        "erro_vertical": target_vy - vy,
        "altura": y,
        "distancia_centro": abs(x),
        "queda_perigosa": vy < -0.3,
        "fora_do_alvo_e_baixo": y < 0.2 and abs(x) > 0.1,
        
        # O cálculo do erro angular já inclui o amortecimento (vtheta)
        "erro_angular_ajustado": (theta - target_theta) * 2.0 + (vtheta) * 1.5,
        
        "pousado": leg_left == 1 and leg_right == 1
    }

# --- AÇÕES (Funções de Controle) ---

def control_main_engine(p):
    """Calcula a força do motor principal (0 a 1)"""
    # Base proporcional: erro de velocidade + compensação de altitude
    main = p["erro_vertical"] * 0.5 + (0.5 - p["altura"]) * 0.1
    
    # Reforços de segurança
    if p["queda_perigosa"]: 
        main += 0.4
    if p["fora_do_alvo_e_baixo"]: 
        main += 0.3
        
    return np.clip(main, 0, 1)


def control_side_engines(p):
    """Calcula a força dos motores laterais (-1 a 1)"""
    side = p["erro_angular_ajustado"]
    
    # Regra do Enunciado: Zona Morta entre -0.5 e 0.5
    if abs(side) < 0.5:
        # Se o erro for relevante (> 0.05), forçamos a ativação mínima (0.51)
        if abs(side) > 0.05:
            side = 0.51 if side > 0 else -0.51
        else:
            side = 0.0 # Erro desprezível, desliga motores
            
    return np.clip(side, -1, 1)



# --- AGENTE REATIVO ---

def reactive_agent(observation):
    # 1. Perceber o ambiente
    p = perceptions(observation)
    
    # 2. Se já pousou, desliga tudo
    if p["pousado"]:
        return np.array([0, 0])
    
    # 3. Executar ações baseadas nas perceções
    main_power = control_main_engine(p)
    side_power = control_side_engines(p)
    
    return np.array([main_power, side_power])
    
    
    
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
