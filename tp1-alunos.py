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
def perceptions(observation):
    x, y, vx, vy, theta, vtheta, leg_left, leg_right = observation
    
    # --- Cálculos de Apoio (Controle Proporcional) ---
    # Alvo: velocidade vertical suave
    target_vy = -0.15
    erro_vertical = target_vy - vy
    
    # Alvo: ângulo ideal para voltar ao centro (x=0)
    # Se x > 0 (direita), target_theta deve ser positivo para inclinar para a esquerda
    target_theta = np.clip(x * 0.7 + vx * 1.2, -0.4, 0.4)
    # Erro de inclinação considerando a velocidade de rotação para amortecimento
    erro_angular_com_amortecimento = (theta - target_theta) * 2.0 + (vtheta) * 1.5

    return {
        # Estado vertical (Main Engine)
        "precisa_potencia_vertical": erro_vertical * 0.5 + (0.5 - y) * 0.1,
        "queda_perigosa": vy < -0.3,
        "muito_baixo_fora_do_alvo": y < 0.2 and abs(x) > 0.1,
        
        # Estado Lateral (Side Engine)
        "comando_lateral_bruto": erro_angular_com_amortecimento,
        
        # Estados booleanos de segurança
        "pernas_no_chao": leg_left == 1 and leg_right == 1,
        "em_voo": leg_left == 0 or leg_right == 0
    }


# TODO: Defina as suas ações aqui
def reactive_agent(observation):
    # Obtém o dicionário de percepções
    p = perceptions(observation)
    
    # 1. Condição de paragem (Pousou!)
    if p["pernas_no_chao"]:
        return np.array([0, 0])
    
    # --- MOTOR PRINCIPAL (MAIN ENGINE) ---
    # Começamos com o cálculo proporcional da percepção
    main = p["precisa_potencia_vertical"]

    # Adicionamos potência extra baseada em percepções de risco
    if p["queda_perigosa"]: 
        main += 0.4
    if p["muito_baixo_fora_do_alvo"]: 
        main += 0.3
        
    main = np.clip(main, 0, 1)

    # --- MOTOR LATERAL (SIDE ENGINE) ---
    # Extraímos o comando calculado na percepção
    side = p["comando_lateral_bruto"]
    
    # Aplicação da Zona Morta do Enunciado (-0.5 a 0.5)
    # Se o comando for necessário (correção mínima), forçamos para 0.51 ou -0.51
    if 0.05 < abs(side) < 0.5:
        side = 0.51 if side > 0 else -0.51
    elif abs(side) <= 0.05:
        side = 0.0 # Dentro de uma margem de erro desprezível
        
    side = np.clip(side, -1, 1)

    return np.array([main, side])
    
    
    
    
    
    
    
    
    
    
    
    
    """
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
        """

    
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
