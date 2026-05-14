def tournament_selection(population, k=10): # Considerar afinar o parâmetro k. Qual seria o melhor K para o caso de uma populacao maior ou menor. Ou seja, determinar a melhor proporção da população total.


 Para a implementação do crossover escolhemos o two point crossover para populações reduzidas ( < 500, exemplo ) . Fazer vários testes com várias populações para ver a partir de que nível faz sentido implementar outro crossover


# ------------------Coisas por fazer-----------------------------------#
1. Fazer testes com os pares de parâmetros disponibilizados no enunciado do projeto 
   
## ATENCAO/SUGESTAO: Escrever logo a seguir o relatório de análise dos resultados
2. Alterar valores de parametros de arquitetura da rede neural e verificar os resultados
Os parametros podem ser : 
nInputs
nOutputs
SHAPE 
GENOTYPE_SIZE
POPULATION_SIZE
NUMBER_OF_GENERATIONS
PROB_CROSSOVER
PROB_MUTATION
STD_DEV
ELITE_SIZE

# Fazer experimento alterando o valor destas variaveis e registar os seus resultados
## ATENCAO/SUGESTAO: Ponham os resultados de cada um numa pasta específica entitulada

3. logX.txt, onde X refere-se ao numero da experiencia. Cada linha destes ficheiros guarda, para cada geracao, a aptidao
do melhor indivıduo, a topologia da rede (SHAPE) e o seu genotipo. Esta
informacao nao so sera util para analisar o comportamento dos algoritmos,
bem como permitira carregar e utilizar os melhores indivıduos. Devera utilizar 
estes logs para testar os individuos evoluıdos em multiplos episodios,
podendo assim recolher metricas de aptidao media e taxa de sucesso. Estas
metricas permitirao aferir a performance media dos agentes evoluıdos e de
verao ser usadas (a par de outras que considere relevantes) para comparar as
diferentes abordagens. 
-> Será carregar o melhor individuo de cada experiencia e calcular a media e taxa de sucesso. 



Plano de horas de trabalho: Quando possivel, fazer um ponto do relatorio. Fazê-lo bem feito.




O que isto te diz para os próximos passos?
Se tivesses de entregar o trabalho agora, o teu "piloto" oficial seria o do log3.txt. No entanto, para tornar o algoritmo mais robusto (para que todas as rondas fossem como a 3), as recomendações seriam:

Aumentar o Elitismo: Se mantivesses os 5 ou 10 melhores, a "receita" do sucesso da Ronda 3 espalhar-se-ia com mais segurança.

Aumentar a Amostragem (N > 1): A Ronda 3 pode ter tido sorte com terrenos fáceis. Avaliar cada indivíduo 3 ou 5 vezes (tirando a média) filtraria os "falsos heróis".

Pressão Seletiva: O teu torneio de 10 em 100 é bom, mas talvez pudesses experimentar aumentar ligeiramente a mutação quando a população para de evoluir.