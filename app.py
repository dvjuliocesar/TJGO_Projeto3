from flask import Flask, request, render_template, Response, session
from util import ProcessosAnalisador  # Certifique-se de que a classe está no arquivo correto
import pandas as pd


app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = '125blablabla'

filepath = 'uploads/dados_je_geral_25042025.csv'  # Caminho para o arquivo CSV

# Inicializa a classe ProcessosAnalisador com o arquivo CSV
analisador = ProcessosAnalisador(filepath)

@app.route('/')
def tabela():

    # Pega o parâmetro de filtro da URL
    filtro_comarca = request.args.get('comarca', 'GOIANIRA')
    filtro_ano = request.args.get('ano', '2020')

    # Verifica se o filtro de ano está vazio ou é inválido
    if filtro_ano == '' or not filtro_ano.isdigit():
        filtro_ano = '2020'  # Se vazio ou inválido, força o valor padrão '2020'

    # Converte filtro_ano para inteiro
    filtro_ano = int(filtro_ano)

    session['args']=[filtro_comarca,filtro_ano]

    comarcas = analisador.obter_comarcas_disponiveis()
    anos = analisador.obter_anos_disponiveis()
    anos = [str(ano) for ano in anos]


    estatisticas = analisador.estatisticas_a(filtro_comarca, filtro_ano)

    # Agrupa os dados por área de ação e calcula as estatísticas
    estatisticas_df = pd.DataFrame(estatisticas)
    estatisticas_df = estatisticas_df.rename(
        columns={
            "nome_assunto":"Assunto",
            "data_distribuicao":"Distribuídos",
            "data_baixa":"Baixados"
    })
    #print(estatisticas_df)
    
    # Reorganiza as colunas para exibição
    estatisticas_df = estatisticas_df[
        ["Assunto",
         "Distribuídos", 
         "Baixados",
         "Pendentes", 
         "Taxa de Congestionamento (%)"
    ]]
    
    # Converte o DataFrame filtrado e com as estatísticas em HTML para exibição no dashboard
    tabela_html = estatisticas_df.to_html(classes='table table-bordered')

    return render_template('base.html', 
                           tabela_html=tabela_html, comarcas=comarcas, anos=anos)

@app.route('/classe')
def tabela_classe():

    # Pega o parâmetro de filtro da URL
    filtro_comarca = request.args.get('comarca', 'GOIANIRA')
    filtro_ano = request.args.get('ano', '2020')

    # Verifica se o filtro de ano está vazio ou é inválido
    if filtro_ano == '' or not filtro_ano.isdigit():
        filtro_ano = '2020'  # Se vazio ou inválido, força o valor padrão '2020'

    # Converte filtro_ano para inteiro
    filtro_ano = int(filtro_ano)

    session['args']=[filtro_comarca,filtro_ano]

    comarcas = analisador.obter_comarcas_disponiveis()
    anos = analisador.obter_anos_disponiveis()
    anos = [str(ano) for ano in anos]


    estatisticas = analisador.estatisticas_c(filtro_comarca, filtro_ano)

    # Agrupa os dados por área de ação e calcula as estatísticas
    estatisticas_df = pd.DataFrame(estatisticas)
    estatisticas_df = estatisticas_df.rename(
        columns={
            "natureza":"Classe",
            "data_distribuicao":"Distribuídos",
            "data_baixa":"Baixados"
    })
    
    # Reorganiza as colunas para exibição
    estatisticas_df = estatisticas_df[
        ["Classe",
         "Distribuídos", 
         "Baixados",
         "Pendentes", 
         "Taxa de Congestionamento (%)"
    ]]
    
    # Converte o DataFrame filtrado e com as estatísticas em HTML para exibição no dashboard
    tabela_html = estatisticas_df.to_html(classes='table table-bordered')

    return render_template('pagina-classe.html', 
                           tabela_html=tabela_html, comarcas=comarcas, anos=anos)

@app.route('/grafico-assunto')
def grafico_assunto():
    # Pega o parâmetro de filtro da URL
    filtro_comarca = request.args.get('comarca', 'GOIANIRA')
    filtro_ano = request.args.get('ano', '2020')

    # Verifica se o filtro de ano está vazio ou é inválido
    if filtro_ano == '' or not filtro_ano.isdigit():
        filtro_ano = '2020'  # Se vazio ou inválido, força o valor padrão '2020'
    filtro_ano = int(filtro_ano)
    
    session['args']=[filtro_comarca, filtro_ano]

    comarcas = analisador.obter_comarcas_disponiveis()
    anos = analisador.obter_anos_disponiveis()
    anos = [str(ano) for ano in anos]
    
    # Gráfico 
    fig = analisador.grafico_assunto_ano(comarca=filtro_comarca, ano=filtro_ano)
    fig.update_layout(
        title= None,
        xaxis_title="Assunto",
        yaxis_title="Taxa de Congestionamento (%)",
        legend_title="Assunto"
    )
    figura_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('grafico-assunto.html',  
                            figura_html=figura_html, comarcas=comarcas,anos=anos)

@app.route('/grafico-classe')
def grafico_classe():
    # Pega o parâmetro de filtro da URL
    filtro_comarca = request.args.get('comarca', 'GOIANIRA')
    filtro_ano = request.args.get('ano', '2020')

    # Verifica se o filtro de ano está vazio ou é inválido
    if filtro_ano == '' or not filtro_ano.isdigit():
        filtro_ano = '2020'  # Se vazio ou inválido, força o valor padrão '2020'
    filtro_ano = int(filtro_ano)
    
    session['args']=[filtro_comarca, filtro_ano]

    comarcas = analisador.obter_comarcas_disponiveis()
    anos = analisador.obter_anos_disponiveis()
    anos = [str(ano) for ano in anos]
    
    # Gráfico 
    fig = analisador.grafico_classe_ano(comarca=filtro_comarca, ano=filtro_ano)
    fig.update_layout(
        title= None,
        xaxis_title="Classe",
        yaxis_title="Taxa de Congestionamento (%)",
        legend_title="Classe"
    )
    figura_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('grafico-classe.html',  
                            figura_html=figura_html, comarcas=comarcas,anos=anos,
                            comarca_selecionada=filtro_comarca, ano_selecionado=filtro_ano)

if __name__ == '__main__':
    app.run(debug=True)