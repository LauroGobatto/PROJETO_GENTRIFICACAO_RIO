import pandas as pd

df_renda = pd.read_csv('RENDA_POR_BAIRRO.csv')
df_score_final = pd.read_csv('SCORE_FINAL.csv')
df_renda.rename(columns={df_renda.columns[0]: 'BAIRRO'}, inplace=True)
df_renda.rename(columns={df_renda.columns[11]: 'RENDA MENSAL'}, inplace=True)
df_renda_bairro = df_renda[['BAIRRO','RENDA MENSAL']]
df_renda_bairro['RENDA MENSAL'] = (df_renda_bairro['RENDA MENSAL'] * 1212 * 1.165).round(2)
df_final = pd.merge(df_score_final, df_renda_bairro, on= "BAIRRO", how='inner')
df_final['ÍNDICE DE ACESSIBILIDADE'] = ((df_final['PREÇO POR METRO'] * 50) / df_final['RENDA MENSAL'])

df_final['ÍNDICE DE ACESSIBILIDADE'] = (df_final['ÍNDICE DE ACESSIBILIDADE'] * 1).round(2)
df_final = df_final.sort_values(by= 'ÍNDICE DE ACESSIBILIDADE', ascending= False).reset_index(drop= True)
df_final.to_csv('BAIRROS_RENDA.csv', index= False)
print(f"{df_final.to_string()}")