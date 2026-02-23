import pandas as pd
import sqlite3
from datetime import datetime

mes_ano = datetime.now().strftime('%Y_%m')

df = pd.read_csv('data/processed/RISCO DE GENTRIFICAÇÃO.csv')
df.columns = ['BAIRRO', 'PREÇO_POR_METRO', 'UNIDADES_RESIDENCIAIS', 'INDICE_DE_PRESSAO', 'AREA_TERRITORIAL_DISPONIVEL', 'MAGNITUDE', 'RENDA_MENSAL', 'TX_ESFORCO', 'RISCO_GENTRIFICACAO']
with sqlite3.connect('data/processed/GENTRIFICACAO_TOTAL.db') as conn:
    df.to_sql('bairros', conn, if_exists='replace', index=False)

df_mes = pd.read_csv(f'data/processed/monthly/BAIRROS_RENDA_{mes_ano}.csv')
with sqlite3.connect(f'data/processed/monthly/GENTRIFICACAO_{mes_ano}.db') as conn:
    df_mes.to_sql('bairros', conn, if_exists='replace', index=False)
