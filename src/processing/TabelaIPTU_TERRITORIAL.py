import pandas as pd
import numpy as np

df_iptu_territorial = pd.read_csv('IPTU_TERRITORIAL.csv')
df_iptu_territorial['nome'] = df_iptu_territorial['nome'].str.strip()
df_iptu_territorial = df_iptu_territorial.rename(columns= {
    'nome': 'BAIRRO',
    'area_territ': 'ÁREA TERRITORIAL DISPONÍVEL'
})
bairro_territorio = df_iptu_territorial.groupby('BAIRRO')['ÁREA TERRITORIAL DISPONÍVEL'].sum()
df_iptu_residencial = pd.read_csv('RESIDENCIA_POR_BAIRRO.csv')
df_final = pd.merge(df_iptu_residencial, bairro_territorio, on = 'BAIRRO', how = 'inner' )
df_final['ÁREA_TRATADA'] = np.sqrt(df_final['ÁREA TERRITORIAL DISPONÍVEL'])
df_final['SCORE FINAL'] = df_final['ÁREA_TRATADA'] * df_final['ÍNDICE DE PRESSÃO']

p_min, p_max = df_final['SCORE FINAL'].min(), df_final['SCORE FINAL'].max()
df_final['SCORE FINAL'] = 1 + ((df_final['SCORE FINAL'] - p_min) / (p_max - p_min) * 4)
df_final['SCORE FINAL'] = df_final['SCORE FINAL'].round(3)

df_final = df_final.drop(columns= ['ÁREA_TRATADA'])
df_final = df_final.sort_values( by= 'SCORE FINAL', ascending= False).reset_index(drop= True)
df_final.to_csv('SCORE_FINAL.csv', index= False)
print (f"{df_final.to_string()}")