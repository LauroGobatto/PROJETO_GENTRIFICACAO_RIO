import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from coletor_quintoandar import scrapper_quintoandar
from coletor_olx import scrapper_olx
import os
from datetime import datetime

async def scrapper_final():
	df_quinto = await scrapper_quintoandar()
	df_olx = await scrapper_olx()
	df_quinto['Fonte'] = 'Quinto Andar'
	df_olx['Fonte'] = 'OLX'

	df_alugueis = pd.concat([df_olx, df_quinto], ignore_index = True)
	df_alugueis['PREÇO POR METRO'] = (df_alugueis['PREÇO'] / df_alugueis['ÁREA']).round(1)
	df_precos_bairro = df_alugueis.groupby('BAIRRO')['PREÇO POR METRO'].median().reset_index()
	
	# 1. Definir o nome do mês atual para o arquivo individual
	mes_ano = datetime.now().strftime('%Y_%m')

	caminho_csv = os.path.join('data', 'processed', 'monthly', f'PREÇO_POR_BAIRRO_{mes_ano}.csv')
	df_precos_bairro.to_csv(caminho_csv, index=False)

	# 3. ATUALIZAR O TOTAL (Este aqui junta o novo com o que já existia)
	arquivo_total = 'data/processed/PREÇO_POR_BAIRRO_TOTAL.csv'

	df_antigo = pd.read_csv(arquivo_total)
	df_acumulado = pd.concat([df_antigo, df_precos_bairro]).drop_duplicates()
	df_acumulado.to_csv(arquivo_total, index=False)
      
	return 0

if __name__ == "__main__":
    asyncio.run(scrapper_final())
