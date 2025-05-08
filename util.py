# Importando Bibliotecas
import pandas as pd
import numpy as np 
import plotly.express as px

class ProcessosAnalisador:
    def __init__(self, arquivo_csv):
        # Carrega os dados do arquivo CSV e realiza o pré-processamento
        self.df = self._carregar_dados(arquivo_csv)
        
    def _carregar_dados(self, arquivo_csv):
        # Carrega o arquivo CSV e realiza o pré-processamento dos dados
        df = pd.read_csv(arquivo_csv, sep=',', encoding='utf-8', low_memory=False) 
        
        # Converter colunas de data para datetime com tratamento de erros
        df['data_distribuicao'] = pd.to_datetime(df['data_distribuicao'], errors='coerce')
        df['data_baixa'] = pd.to_datetime(df['data_baixa'], errors='coerce')

        return df

    # Retorna as comarcas disponíveis
    def obter_comarcas_disponiveis(self):
        
        return sorted(self.df['comarca'].unique())
        
    # Retorna os anos disponíveis na coluna de data de distribuição
    def obter_anos_disponiveis(self):
        
        return sorted(self.df['data_distribuicao'].dt.year.unique())
        
    # Calcula as estatísticas por área de ação para o ano selecionado
    def calcular_estatisticas(self, comarca, ano_selecionado):
    
        # Filtrar pela comarca
        df_comarca = self.df[self.df['comarca'] == comarca]
            
        # Filtrar processos distribuídos no ano selecionado
        df_ano = df_comarca[df_comarca['data_distribuicao'].dt.year == ano_selecionado]
            
        # Agrupar por nome_area_acao
        estatisticas = df_ano.groupby(['nome_area_acao', 'nome_assunto']).agg(
            Distribuídos=('data_distribuicao', 'count') # Quantidade de datas distribuídas
        ).reset_index()
            
        # Calcular baixados no ano
        baixados_no_ano = df_comarca[
            (df_comarca['data_baixa'].dt.year == ano_selecionado) & 
            (df_comarca['data_baixa'].notnull())
        ]
            
        # Agrupar baixados da mesma forma que os distribuídos
        baixados_por_area = baixados_no_ano.groupby(
            ['nome_area_acao', 'nome_assunto']
            ).size()
            
        # Mesclar corretamente com estatisticas

        estatisticas = estatisticas.merge(
            baixados_por_area.rename('Baixados'), 
            on=['nome_area_acao', 'nome_assunto'], 
            how='left'
        ).fillna(0).astype({'Baixados': 'int'})
            
        # Calcular pendentes
        pendentes_por_area = df_ano[df_ano['data_baixa'].isnull()].groupby(
            ['nome_area_acao', 'nome_assunto']
        ).size()
            
        estatisticas = estatisticas.merge(
            pendentes_por_area.rename('Pendentes'), 
            on=['nome_area_acao','nome_assunto'], 
            how='left'
        ).fillna(0).astype({'Pendentes': 'int'})
        print (pendentes_por_area)
        # Calcular taxa de congestionamento no ano
        estatisticas['Taxa de Congestionamento (%)'] = (
            (estatisticas['Pendentes'] / (estatisticas['Pendentes'] + estatisticas['Baixados'])) * 100
        ).round(2)

        # Adicionar linha de totais
        totais = {
            'nome_area_acao': 'TOTAL',
            'nome_assunto':'',
            'Distribuídos': estatisticas['Distribuídos'].sum(),
            'Baixados': estatisticas['Baixados'].sum(),
            'Pendentes': estatisticas['Pendentes'].sum(),
        }

        # Evitar divisão por zero
        if (totais['Pendentes'] + totais['Baixados']) > 0:
            totais['Taxa de Congestionamento (%)'] = round(
            (totais['Pendentes'] / (totais['Pendentes'] + totais['Baixados'])) * 100, 2
            )
        else:
            totais['Taxa de Congestionamento (%)'] = 0.00

        # Adicionar a linha de totais ao DataFrame
        estatisticas = pd.concat([estatisticas, pd.DataFrame([totais])], ignore_index=True)
                    
        return estatisticas
