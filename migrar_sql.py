import pandas as pd
import sqlite3

db_path = 'data/processed/GENTRIFICACAO.db'
csv_path = 'data/processed/RISCO DE GENTRIFICAÇÃO.csv'


df = pd.read_csv(csv_path)
df.columns = ['BAIRRO', 'PREÇO_POR_METRO', 'UNIDADES_RESIDENCIAIS', 'INDICE_DE_PRESSAO', 'AREA_TERRITORIAL_DISPONIVEL', 'MAGNITUDE', 'RENDA_MENSAL', 'TX_ESFORCO', 'RISCO_GENTRIFICACAO']

with sqlite3.connect(db_path) as conn:
    df.to_sql('bairros', conn, if_exists='replace', index=False)
    
print(f"🚀 SUCESSO! Tabela 'bairros' criada com {len(df)} linhas.")
