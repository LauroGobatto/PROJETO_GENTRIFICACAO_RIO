import pandas as pd
import sqlite3
from pathlib import Path

# 1. Caminhos Oficiais (Fora do venv!)
raiz = Path("/home/laurogobatto/Projeto_Alugueis")
db_path = raiz / 'data' / 'radar_alugueis.db'
csv_path = raiz / 'data' / 'processed' / 'RISCO DE GENTRIFICAÇÃO.csv'

# 2. Ingestão
if csv_path.exists():
    print(f"✅ Arquivo encontrado! Iniciando ingestão...")
    df = pd.read_csv(csv_path)
    
    # Padronizando nomes para o SQL (sem espaços e sem acentos)
    df.columns = ['BAIRRO', 'PREÇO_POR_METRO', 'UNIDADES_RESIDENCIAIS', 'INDICE_DE_PRESSAO', 'AREA_TERRITORIAL_DISPONIVEL', 'MAGNITUDE', 'RENDA_MENSAL', 'TX_ESFORCO', 'RISCO_GENTRIFICACAO']

    with sqlite3.connect(db_path) as conn:
        df.to_sql('bairros', conn, if_exists='replace', index=False)
    
    print(f"🚀 SUCESSO! Tabela 'bairros' criada com {len(df)} linhas.")
else:
    print(f"❌ O arquivo sumiu de novo? Verifique: {csv_path}")