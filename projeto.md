# Relatório

#### Definição de percepções do Agente:
    1. Distância do Agente ao solo (D);
    2. Agente a esquerda da plataforma (LP);
    3. Agente a direita da plataforma (RP);
    4. Agente a descer (F);
    5. Agente a subir (U); 
    6. Agente a girar em sentido horário (SC) ;
    7. Agente a girar em sentido anti-horário (SNC) ;
    8. Agente inclinada a direita (R) ;
    9. Agente inclinada a esquerda (L) .


#### Possíveis ações a executar:
    1. Pontenciar motor central / mover-se verticalmente na direção atual(PC);
    2. Potenciar motor lateral esquerdo / rodar para a direita(PE);
    3. Potenciar motor lateral direito / rodar para a esquerda(PD).
   

#### Sistema de produções que definem o comportamento do Agente
verificacaoDeSegurança(D, limiar), verificarTeta(teta, negativo) (R) -> PE  
verificacaoDeSegurança(D, limiar), verificarTeta(teta, positivo) (E) -> PD
verificacaoDeSegurança(D, limiar), verificarTeta(teta, zero) -> PC 
<!-- Se for possivel pôr mais de uma ação na queue de uma vez, é possivel fazer varios PE de acordo com a velocidade angular). -->

<!-- Situacao em que o agente se encontra a esquerda da plataforma -->
LP, verificarInclinacao(teta, -45) -> PE, PC
LP, not verificarInclinacao(teta, -45) -> PD, PC
LP -> PC

<!-- Situacao em que o agente se encontra a direita da plataforma -->
RP, verificarInclinacao(teta, 45) -> PD, PC
RP, not verificarInclinacao(teta, 45) -> PE, PC
RP -> PC








<!-- 
As funções de verificacao devolvem true ou false. Fazem 1º argumento < 2º argumento

verificacaoDeSegurança(D, limiar)
return D < limiar;


limiar - um limite estabelecido para nao deixar a nave passar enquanto nao estiver em cima da plataforma. Se passar esse limite pode-se correr o risco de bater numa montanha ou no chao antes de chegar a plataforma.




-->