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
        
    # Calcula as estatísticas por Assunto para o Ano e Comarca selecionados
    def estatisticas_a(self, comarca, ano):
    
        # Filtros iniciais
        filtro_comarca = self.df['comarca'] == comarca
        filtro_ano = self.df['data_distribuicao'].dt.year == ano
        df_filtrado = self.df[filtro_comarca & filtro_ano].copy()
        
        # Cálculo das métricas por área de ação e assunto
        estatisticas_a = df_filtrado.groupby(['nome_area_acao', 'nome_assunto']).agg(
            Distribuídos=('data_distribuicao', 'count'),
            Baixados=('data_baixa', lambda x: x.notna().sum()),
            Pendentes=('data_baixa', lambda x: x.isna().sum())
        ).reset_index()
        
        # Calcular taxa de congestionamento no ano
        estatisticas_a['Taxa de Congestionamento (%)'] = (
            (estatisticas_a['Pendentes'] / (estatisticas_a['Pendentes'] + estatisticas_a['Baixados'])) * 100
        ).round(2)

        # Adicionar linha de totais
        totais = {
            'nome_area_acao': 'TOTAL',
            'nome_assunto':'',
            'Distribuídos': estatisticas_a['Distribuídos'].sum(),
            'Baixados': estatisticas_a['Baixados'].sum(),
            'Pendentes': estatisticas_a['Pendentes'].sum(),
        }

        # Evitar divisão por zero
        if (totais['Pendentes'] + totais['Baixados']) > 0:
            totais['Taxa de Congestionamento (%)'] = round(
            (totais['Pendentes'] / (totais['Pendentes'] + totais['Baixados'])) * 100, 2
            )
        else:
            totais['Taxa de Congestionamento (%)'] = 0.00

        # Adicionar a linha de totais ao DataFrame
        estatisticas_a = pd.concat([estatisticas_a, pd.DataFrame([totais])], ignore_index=True)
                    
        return estatisticas_a
    
    # Calcula as estatísticas por Classe para o Ano e Comarca selecionados
    def estatisticas_c(self, comarca, ano):
    
        # Filtros iniciais
        filtro_comarca = self.df['comarca'] == comarca
        filtro_ano = self.df['data_distribuicao'].dt.year == ano
        df_filtrado = self.df[filtro_comarca & filtro_ano].copy()
        
        # Cálculo das métricas por área de ação e assunto
        estatisticas_c = df_filtrado.groupby(['nome_area_acao', 'natureza']).agg(
            Distribuídos=('data_distribuicao', 'count'),
            Baixados=('data_baixa', lambda x: x.notna().sum()),
            Pendentes=('data_baixa', lambda x: x.isna().sum())
        ).reset_index()
        
        # Calcular taxa de congestionamento no ano
        estatisticas_c['Taxa de Congestionamento (%)'] = (
            (estatisticas_c['Pendentes'] / (estatisticas_c['Pendentes'] + estatisticas_c['Baixados'])) * 100
        ).round(2)

        # Adicionar linha de totais
        totais = {
            'nome_area_acao': 'TOTAL',
            'natureza':'',
            'Distribuídos': estatisticas_c['Distribuídos'].sum(),
            'Baixados': estatisticas_c['Baixados'].sum(),
            'Pendentes': estatisticas_c['Pendentes'].sum(),
        }

        # Evitar divisão por zero
        if (totais['Pendentes'] + totais['Baixados']) > 0:
            totais['Taxa de Congestionamento (%)'] = round(
            (totais['Pendentes'] / (totais['Pendentes'] + totais['Baixados'])) * 100, 2
            )
        else:
            totais['Taxa de Congestionamento (%)'] = 0.00

        # Adicionar a linha de totais ao DataFrame
        estatisticas_c = pd.concat([estatisticas_c, pd.DataFrame([totais])], ignore_index=True)
                    
        return estatisticas_c
