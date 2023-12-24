"""
API FRASES em PORTUGUÊS
Essa API é baseada na API Forismatic, que possui frases em inglês. Usamos então a API Deepl para fazer as traduções e incluir no Banco de Dados as frases em ingês e português.
Como há limitação de uso da API Deepl fazemos uma contagem de caracteres e data de ultimo uso para que o APP somente execute uma vez por mês, obtendo até 450.000 caracteres traduzidos.
O Banco de dados obtido será usado em outros Apps
"""

import requests
import deepl
import sqlite3
from time import sleep
import datetime
import os
from tradutor import key

# módulo para gravação da key da API Deepl e ocultação no repositório
tradutor = deepl.Translator(key())
db = 'C:\\Users\\julio\\PycharmProjects\\UniversoApp\\database\\frases.db'
run = True
contagem_caracteres_dia = 0

# Função para obter, do arquivo TXT que vamos gravar sempre que executar o app, a data da sua ultima execução.
def pegar_data_ultima_execucao():
    if os.path.exists('ultima_execucao.txt'):
        with open('ultima_execucao.txt', 'r') as file:
            return datetime.datetime.strptime(file.read(), '%Y-%m-%d')
    else:
        return None

# Função para gravar o arquivo ultima_execucao.txt para podermos extrair futuramente sua data de gravação     
def gravar_data_ultima_execucao(date):
    with open('ultima_execucao.txt', 'w') as file:
        file.write(date.strftime('%Y-%m-%d'))

# Função para verificar se a data do arquivo ultima_execucao.txt tem 32 dias passados.        
def verificar_passou_32d():
    data_ultima_execucao = pegar_data_ultima_execucao()
    if data_ultima_execucao is None:
        return True
    else:
        # return ((datetime.datetime.now() - data_ultima_execucao).days) >= 32
        return True   

"""Loop para o App buscar frases, traduzir e incluir no BD enquanto não tivermos um erro na obtenção da frase, na tradução ou na inclusão ao BD,
ou a contagem de caracteres das frases em Ingles for menor que 450.000"""
while run:
    if contagem_caracteres_dia == 450000:
        run = False
    
    if not verificar_passou_32d():
        print("Ainda não podemos fazer as traduções. Precisa aguardar completar o mês.")
        run = False
    
    # Conecta o Banco de Dados, posiciona o cursor e executa ações no Banco de Dados
    def db_consulta(consulta, parametros=()):
            with sqlite3.connect(db) as con:
                cursor = con.cursor()
                resultado = cursor.execute(consulta, parametros)
                con.commit()
                return resultado

    # Vai a API Forismatic e busca a frase do dia em Inglês (Não há em Português)
    def buscar_frase_dia():
        try:
            response = requests.get('http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
            print('solicitacao enviada a API Forismatic')
            quote = response.json()['quoteText']
            print('frase EN obtida ma API Forismatic')
            # print(f"quote is: {quote}")
            return quote
        except Exception as e:
            if 'Invalid \\escape' in str(e):
                print('A frase contém barra invertida e será ignorada.')
                sleep(1)
                return
            else:
                print(f"Erro {e} encontrado")
                run = False
            
    frase_do_dia_EN = buscar_frase_dia()
    
    
    # Função para verificar se a frase do dia, retirada da API Forismatic, já existe no BD. Existindo, vai retornar True se a frase já existe.    
    def verificar_frase_EN_BD(frase_ingles):
        try:
            query = 'SELECT EXISTS(SELECT 1 FROM frase WHERE frase_EN = ?)'
            resultado = db_consulta(query, (frase_ingles,))
            print('frase EN verificada no BD')
            return resultado.fetchone()[0] != 0
        except Exception as e:
            print(f"Erro ao tentar verificar a frase {frase_ingles} no BD. Erro: {e}")
            run = False
    # Condição que verifica se a função 'verificar_frase_EN_BD' is TRUE. Sendo True é porque a frase já existe no Bando de Dados, e então volta ao loop inicial.
    if verificar_frase_EN_BD(frase_do_dia_EN):
        sleep(1)
        print('A frase já existe no BD')
        print()
        continue    

    # Caso a verificação acima seja FALSE, segue o código, e verifica SE a frase do dia is not None. Não sendo None, faz a soma de caracteres_dia para não atingir limite do DEEPL
    if frase_do_dia_EN is not None:
        contagem_caracteres_dia += len(frase_do_dia_EN)
    else:
        continue

    # Utiliza a API DEEPL para traduzir a frase para o Português
    def traduzir_mensagem(mensagem):
        try:
            if mensagem is None or mensagem == '':
                sleep(1)
                return
            frase_traduzida_deepl = tradutor.translate_text(mensagem, target_lang="PT-BR")
            frase_traduzida = frase_traduzida_deepl.text
            print('frase traduzida para PT-BR')
            return frase_traduzida
        except Exception as e:
            print(f"A tradução parou por causa do erro: {e}")
            run = False

    frase_do_dia_PT = traduzir_mensagem(frase_do_dia_EN)
    # print(f"A frase do dia em PT-BR é: {frase_do_dia_PT}")

    # Inclui a frase do dia, em Português, no Banco de Dados.
    def incluir_frase_dia_BD(frase_EN, frase):
        try:
            if frase_EN is None or frase_EN == '' or frase is None or frase == '':
                print('A frase não pode ser None ou uma string vazia - Definição NOT NULL no banco de dados para essa coluna. Vamos tentar obter novamente a frase')
                sleep(1)
                return           
            query = 'INSERT INTO frase VALUES(NULL, ?, ?, NULL)'
            # Atenção para inclusão da frase como uma tupla para que o App não entenda que cada palavra seja um parâmetro para o BD. Assim, toda frase será um parâmetro apenas.
            db_consulta(query, (frase_EN, frase,))
            print('frase PT incluida no BD')
        except Exception as e:
            print(f"Erro na inclusão da frase no banco de dados. Motivo: {e}")
            run = False
        
    incluir_frase_dia_BD(frase_do_dia_EN, frase_do_dia_PT)
    print(contagem_caracteres_dia)
    print()
    sleep(10)

# Executar a função para gravar a data da ultima execução do aplicativo, para então somente correr as traduções 1x por mês.    
gravar_data_ultima_execucao(datetime.datetime.now())
