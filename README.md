
![Captura de tela 2023-12-21 235648](https://github.com/JulioDEVReis/BOT_frases_BD/assets/142347463/a94edaa3-0361-4ca9-a4d6-ef65fae6c390)

Recebi uma demanda para um aplicativo mobile, para eu colocar frases aleatórias ao usuário a cada inicialização do aplicativo.
Ao fazer uma consulta por APIs, não encontrei nenhuma API que me desse o conteúdo que eu desejava, em Português.
Uma API me interessou bastante, e ao verificar com a cliente, satisfazia suas necessidades no aplicativo mobile. Trata-se da API Forismatic (https://forismatic.com/en/), que entrega aleatoriamente frases em Inglês.
Para conseguir automatizar o processo de entrega das frases, em Português, para o usuário do aplicativo mobile, precisei pensar em uma solução para, além de buscar a frase na API Forismatic, traduzir seu conteúdo antes de mostrar ao usuário do app mobile.
Encontrei uma API bem interessante para tradução do ingles para o português, gratuita, mas com limitação sobre a quantidade de caracteres traduzidos, por mês.
As frases em inglês e português são então salvas em um Banco de Dados SQL, onde irei usar os dados no Aplicativo Mobile. 
Para contonar situações de erros nas obtenções de dados das APIs e gravação e leitura do Banco de Dados, usei vários loops e Try/Except para evitar as exceções e interrupção do aplicativo.
Um loop WHILE faz com que o aplicativo rode até atingir o limite de traduções, armazenando até 450.000 caracteres traduzidos no banco de dados.
Colocada várias instruções print para DEBUG e acompanhar o processo etapa por etapa.

![Captura de tela 2023-12-21 233439](https://github.com/JulioDEVReis/BOT_frases_BD/assets/142347463/a65fef7c-8a2c-49de-8ef6-450334413afe)

Passo a Passo a execução básica do Aplicativo:
1. Obter a frase aleatória da API Forismatic
2. Usar a API Deepl para traduzir a frase obtida acima.
3. Salvar a frase traduzida em um banco de dados para futuras consultas

Bibliotecas e APIs utilizadas:
- requests (para consultar a API Forismatic)
- deepl (Biblioteca da API Deepl)
- sqlite3 (para acesso, consulta e gravação em nosso banco de dados SQL)
- time (para uso da função sleep, para uma pequena pausa a cada loop do aplicativo, evitando possiveis bloqueios por uso de bot)
- datetime (para usarmos as funções relativas as datas, por conta da limitação da API Deepl, explicada abaixo)
- os (assim como acima, precisamos usar a biblioteca os para manipular o arquivo txt, usado para contornar também a limitação da API Deepl, explicada abaixo)
 
Limitações e soluções:
1. Os acessos a aplicações e sites de terceiros pode não ocorrer por diversos motivos, desde problemas na sua propria internet quanto também a problemas no provedor de serviços, no roteamento, etc... causando erros 404, 500, por exemplo. Para resolver esse problema, usei as instruções try / except para contornar e encerrar o aplicativo sem quebrá-lo. Fiz isso em todas as funções que necessitavam de acessos, como os acessos às APIs. Como o loop WHILE, no inicio do App, funciona enquanto run for True, uso a instrução except para alterar run para False, e assim parar o loop.
2. A API tem a limitação, na versão gratuita, a 500.000 caracteres traduzidos a cada mês. Para resolver isso criei funções para armazenar um arquivo .txt e obter a data de armazenamento, usando essa data para comparar à data do acesso ao App e garantir que somente seja executado uma vez por mês. Além disso usei a função len() para armazenar a quantidade de caracteres traduzidos e controlar a quantidade de traduções durante o loop WHILE. Assim que atingir 450.000 caracteres o loop WHILE é interrompido e o aplicativo é encerrado.

Problemas encontrados e soluções:
1. Ao obter as frases na API Forismatic, observei que várias frases eram repetidas, fazendo com que houvesse a tradução, e consequente aumento da quantidade de caracteres traduzidos (Limitação explicada acima). Além disso, o Banco de Dados começou a ter muitas frases repetidas, com IDs diferentes, afetando, consequentemente, no desempenho dos acessos e manipulação do Banco de Dados. Para resolver isso precisei incluir as frases obtidas na API Forismatic, em inglês, no banco de dados, criar uma função para consultar se a frase já existe no banco de dados e uma condicional para voltar ao inicio do loop WHILE caso a frase exista no banco de dados. Isso irá se repetir até a obtenção da frase na API que ainda não exista no banco de dados.
2. O aplicativo interrompia o loop toda vez que obtinha da API Forismatic um valor NULL. Como meu banco de dados foi configurado para não aceitar um valor NULL na coluna de frases, o aplicativo então parava por não conseguir traduzir e consequentemente gravar os dados. Para resolver isso inclui uma condição IF, onde verifico se a frase em ingles possui valor null ou uma string vazia. Caso sim, uso return para pular a execução da função, evitando a tentativa de tradução e gravação no banco de dados. Assim o aplicativo não interrompia seu loop principal While, e retomava para uma nova tentativa de obtenção de frase.
3. O aplicativo interrompia o loop toda vez que obtinha da API Forismatic frase com caractere \(barra invertida). Apresentava erro Erro Invalid \escape. Para resolver, precisei tratar esse erro no EXCEPT da propria função buscar_frase_dia(), usando uma condição para verificar se o codigo de erro possuia 'Invalid \\escape'. caso esteja presente, usei a instrução return, ignorando o restante do código na função. Nesse caso não podemos tratar esse erro com um except dedicado pois trata-se de uma exceção de sintaxe que é lançada pelo interpretador Python, e não é lançada como uma exceção padrão que pode ser capturada em um bloco except.

