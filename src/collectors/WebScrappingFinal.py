import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from coletor_quintoandar import scrapper_quintoandar
from coletor_olx import scrapper_olx

async def scrapper_final():
	df_quinto = await scrapper_quintoandar()
	df_olx = await scrapper_olx()
	df_quinto['Fonte'] = 'Quinto Andar'
	df_olx['Fonte'] = 'OLX'

	df_alugueis = pd.concat([df_olx, df_quinto], ignore_index = True)
	df_alugueis['PREÇO POR METRO'] = (df_alugueis['PREÇO'] / df_alugueis['ÁREA']).round(1)
	df_precos_bairro = df_alugueis.groupby('BAIRRO')['PREÇO POR METRO'].median().reset_index()
	df_precos_bairro.to_csv('PREÇO_POR_BAIRRO.csv', index=False)
	return df_precos_bairro

if __name__ == "__main__":
    asyncio.run(scrapper_final())
