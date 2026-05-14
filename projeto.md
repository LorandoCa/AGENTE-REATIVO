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


TIPOS DE MUTAÇÕES A NÃO USAR:

Não deves implementar a Tree-Based Mutation. O vosso trabalho utiliza neuroevolução, onde a rede neuronal tem uma arquitetura fixa e o algoritmo evolui apenas os parâmetros (pesos). O genótipo de cada indivíduo é simplesmente uma lista de números reais (floats).
A Tree-Based Mutation é usada em Programação Genética (onde o código é estruturado em árvore), o que quebraria o vosso código atual. Como a vossa lista é de números reais, devem focar-se nas Real-Valued Mutations (Gaussian e Uniform). O teu colega Lorando referiu que ia fazer a Uniform, e a Gaussian já está no código, por isso a parte das mutações já está coberta!

Tal como a Tree-Based, as Binary Mutations (Bit Flip e Bitwise Inversion) não se aplicam ao vosso caso.
Porquê? As mutações binárias são usadas estritamente quando o genótipo do indivíduo é composto por uma cadeia de zeros e uns (ex: [0, 1, 1, 0]). No vosso trabalho prático de neuroevolução, o genótipo é uma lista de números reais (floats) amostrados de uma distribuição uniforme entre -1 e 1. Estes valores representam os parâmetros (pesos) da rede neuronal. Aplicar uma inversão de bits ou um "bit flip" numa lista de floats contínuos não é compatível com a representação matemática do vosso agente.
A regra de ouro nos Algoritmos Evolucionários é que os operadores (como a mutação e o crossover) têm de estar perfeitamente alinhados com a representação do indivíduo. Como a vossa representação é estritamente de números reais, o grupo só tem de se preocupar com as Real-Valued Mutations.