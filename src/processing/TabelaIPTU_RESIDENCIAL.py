import pandas as pd
import numpy as np

df_iptu_residencial = pd.read_csv('IPTU_RESIDENCIAL.csv')
webscrappingfinal = pd.read_csv('PREÇO_POR_BAIRRO.csv')
df_iptu_residencial['nome'] = df_iptu_residencial['nome'].str.strip()
df_iptu_residencial = df_iptu_residencial.rename(columns= {
    'nome': 'BAIRRO',
    'tot_imoveis': 'UNIDADES RESIDENCIAIS'
})
imoveis_bairro = df_iptu_residencial.groupby('BAIRRO')['UNIDADES RESIDENCIAIS'].sum()
df_final = pd.merge(webscrappingfinal, imoveis_bairro, on='BAIRRO', how='inner')
df_final['ÍNDICE DE PRESSÃO'] = df_final['PREÇO POR METRO'] / df_final['UNIDADES RESIDENCIAIS']

p_min, p_max = df_final['ÍNDICE DE PRESSÃO'].min(), df_final['ÍNDICE DE PRESSÃO'].max()
df_final['ÍNDICE DE PRESSÃO'] = 1 + ((df_final['ÍNDICE DE PRESSÃO'] - p_min) / (p_max - p_min) * 4)
df_final['ÍNDICE DE PRESSÃO'] = df_final['ÍNDICE DE PRESSÃO'].round(3)

df_final = df_final.sort_values(by = 'ÍNDICE DE PRESSÃO', ascending = False).reset_index(drop=True)
df_final.to_csv('RESIDENCIA_POR_BAIRRO.csv', index= False)