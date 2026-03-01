import pandas as pd
import numpy as np
import os
from datetime import datetime

df_iptu_residencial = pd.read_csv(
        'data/raw/IPTU_RESIDENCIAL.csv', 
        encoding='utf-8-sig', 
        sep=',',
        skipinitialspace=True 
    )

mes_ano = datetime.now().strftime('%Y_%m')
arquivos = ['TOTAL', mes_ano ]

diretorio_atual = os.path.dirname(os.path.abspath(__file__)) 
raiz = os.path.dirname(os.path.dirname(diretorio_atual))

for i in arquivos:
    if i == 'TOTAL':
        webscrappingfinal = pd.read_csv(f'data/processed/PREÇO_POR_BAIRRO_TOTAL.csv')
    else:
        webscrappingfinal = pd.read_csv(f'data/processed/monthly/PREÇO_POR_BAIRRO_{i}.csv')
    
    df_iptu_residencial = df_iptu_residencial.rename(columns= {
        'nome': 'BAIRRO',
        'tot_imoveis': 'UNIDADES RESIDENCIAIS'
    })
    df_iptu_residencial['BAIRRO'] = df_iptu_residencial['BAIRRO'].str.strip()

    imoveis_bairro = df_iptu_residencial.groupby('BAIRRO')['UNIDADES RESIDENCIAIS'].sum()
    df_merge_residencial = pd.merge(webscrappingfinal, imoveis_bairro, on='BAIRRO', how='inner')
    df_merge_residencial['ÍNDICE DE PRESSÃO'] = df_merge_residencial['PREÇO POR METRO'] / df_merge_residencial['UNIDADES RESIDENCIAIS']

    p_min, p_max = df_merge_residencial['ÍNDICE DE PRESSÃO'].min(), df_merge_residencial['ÍNDICE DE PRESSÃO'].max()
    df_merge_residencial['ÍNDICE DE PRESSÃO'] = 1 + ((df_merge_residencial['ÍNDICE DE PRESSÃO'] - p_min) / (p_max - p_min) * 4)
    df_merge_residencial['ÍNDICE DE PRESSÃO'] = df_merge_residencial['ÍNDICE DE PRESSÃO'].round(3)



    df_iptu_territorial = pd.read_csv('data/raw/IPTU_TERRITORIAL.csv', encoding = 'utf-8-sig', sep = ',')
    df_iptu_territorial.columns = df_iptu_territorial.columns.str.strip().str.replace('\ufeff', '')
    df_iptu_territorial['nome'] = df_iptu_territorial['nome'].str.strip()
    df_iptu_territorial = df_iptu_territorial.rename(columns= {
        'nome': 'BAIRRO',
        'area_territ': 'ÁREA TERRITORIAL DISPONÍVEL'
    })
    bairro_territorio = df_iptu_territorial.groupby('BAIRRO')['ÁREA TERRITORIAL DISPONÍVEL'].sum()

    df_merge_territorial = pd.merge(df_merge_residencial, bairro_territorio, on = 'BAIRRO', how = 'inner' )
    df_merge_territorial['ÁREA_TRATADA'] = np.sqrt(df_merge_territorial['ÁREA TERRITORIAL DISPONÍVEL'])
    df_merge_territorial['SCORE FINAL'] = df_merge_territorial['ÁREA_TRATADA'] * df_merge_territorial['ÍNDICE DE PRESSÃO']

    p_min, p_max = df_merge_territorial['SCORE FINAL'].min(), df_merge_territorial['SCORE FINAL'].max()
    df_merge_territorial['SCORE FINAL'] = 1 + ((df_merge_territorial['SCORE FINAL'] - p_min) / (p_max - p_min) * 4)
    df_merge_territorial['SCORE FINAL'] = df_merge_territorial['SCORE FINAL'].round(3)

    df_merge_territorial = df_merge_territorial.drop(columns= ['ÁREA_TRATADA'])

    df_favela = pd.read_csv(
        'data/raw/LIMITE_FAVELAS.csv', 
        encoding='utf-8-sig', 
        sep=',',
    )

    df_bairro_favela = (df_favela.groupby('bairro')['shape_Area'].sum()).reset_index()

    df_bairro_favela.columns = ['BAIRRO', 'AREA_FAVELA_BAIRRO']
    
    df_bairro = pd.read_csv(
        'data/raw/LIMITE_BAIRROS.csv', 
        encoding='utf-8-sig', 
        sep=',',
    )
    df_bairro = df_bairro[['nome', 'st_areashape']]
    df_bairro.rename(columns={
        'nome':'BAIRRO',
        'st_areashape':'AREA_BAIRRO'
    }, inplace= True)

    df_merge_bairro = pd.merge(df_bairro, df_bairro_favela, on='BAIRRO', how='left').fillna(0)
    df_merge_bairro['INDICE_INFORMALIDADE'] = df_merge_bairro['AREA_FAVELA_BAIRRO'] / df_bairro['AREA_BAIRRO']
    
    df_merge_favela = pd.merge(df_merge_territorial, df_merge_bairro, on='BAIRRO', how='left').fillna(0)
    df_merge_favela = df_merge_favela.drop(columns=['AREA_FAVELA_BAIRRO'])
    df_merge_favela = df_merge_favela.drop(columns=['AREA_BAIRRO'])


    df_renda = pd.read_csv('data/raw/RENDA_POR_BAIRRO.csv')
    df_renda.rename(columns={df_renda.columns[0]: 'BAIRRO'}, inplace=True)
    df_renda.rename(columns={df_renda.columns[11]: 'RENDA MENSAL'}, inplace=True)
    df_renda_bairro = df_renda[['BAIRRO','RENDA MENSAL']].copy()
    df_renda_bairro['RENDA MENSAL'] = (df_renda_bairro['RENDA MENSAL'] * 1212 * 1.248).round(2)
    df_final = pd.merge(df_merge_favela, df_renda_bairro, on= "BAIRRO", how='inner')
    df_final['ÍNDICE DE ACESSIBILIDADE'] = ((df_final['PREÇO POR METRO'] * 50) / df_final['RENDA MENSAL'])

    df_final['ÍNDICE DE ACESSIBILIDADE'] = (df_final['ÍNDICE DE ACESSIBILIDADE'] * 1).round(2)
    df_final = df_final.sort_values(by= 'ÍNDICE DE ACESSIBILIDADE', ascending= False).reset_index(drop= True)
    
    if i == 'TOTAL':
        caminho_csv = os.path.join(raiz, 'data', 'processed', 'BAIRROS_RENDA_TOTAL.csv')
        df_final.to_csv(caminho_csv, index= False)
    else:
        caminho_csv = os.path.join(raiz, 'data', 'processed', 'monthly', f'BAIRROS_RENDA_{i}.csv')
        df_final.to_csv(caminho_csv, index= False)
