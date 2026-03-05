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
	total_linhas_quinto = df_quinto.shape[0]
	total_linhas_olx = df_olx.shape[0]
	print(f"Números de anúncios coletados do site QuintoAndar: {total_linhas_quinto}")
	print(f"Números de anúncios coletados do site OLX: {total_linhas_olx}")

	df_alugueis = pd.concat([df_olx, df_quinto], ignore_index = True)
	df_alugueis['PREÇO POR METRO'] = (df_alugueis['PREÇO'] / df_alugueis['ÁREA']).round(1)
	df_precos_bairro = df_alugueis.groupby('BAIRRO')['PREÇO POR METRO'].median().reset_index()

	mes_ano = datetime.now().strftime('%Y_%m')

	caminho_csv = os.path.join('data', 'processed', 'monthly', f'PREÇO_POR_BAIRRO_{mes_ano}.csv')
	df_precos_bairro.to_csv(caminho_csv, index=False)

	arquivo_total = 'data/processed/PREÇO_POR_BAIRRO_TOTAL.csv'

	df_antigo = pd.read_csv(arquivo_total)
	df_peso = df_antigo.copy()
	df_acumulado = pd.concat([df_antigo, df_precos_bairro, df_peso], ignore_index = True)

	# A MELHOR FORMA DE JUNTAR OS DOIS DADOS É COM UMA MÉDIA, EM VEZ DA MEDIANA, mas com a cópia o df_antigo tem peso 2
	df_final = df_acumulado.groupby('BAIRRO')['PREÇO POR METRO'].mean().reset_index()
	df_final.to_csv(arquivo_total, index=False)

	return 0

if __name__ == "__main__":
    asyncio.run(scrapper_final())
