import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def bloquear_pesos(route):
    if route.request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()

async def scrapper_olx():
	async with async_playwright() as p:
		navegador = await p.chromium.launch(headless=True)
		contexto = await navegador.new_context(
			user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
			)
		
		pagina = await contexto.new_page()
		mapa_bairros = {
			"Braz de Pina": "Brás de Pina",
			"Imperial de São Cristóvão": "São Cristóvão",
			"Todos Os Santos": "Todos os Santos",
			  "Oswaldo Cruz": "Osvaldo Cruz",
			"Barra Olímpica": "Barra da Tijuca",
			"Barra Olimpica": "Barra da Tijuca",
			"Tubiacanga": "Galeão",
			"Arpoador": "Ipanema",
			"Freguesia de Jacarepaguá": "Freguesia (Jacarepaguá)",
			"Freguesia": "Freguesia (Jacarepaguá)",
			"Freguesia (jacarepaguá)": "Freguesia (Jacarepaguá)",
			"Quintino Bocaiuva": "Quintino Bocaiúva",
            "1465 - Bonsucesso": "Bonsucesso",
			"Vl Valqueire": "Vila Valqueire",
			"Váz Lobo": "Vaz Lobo"
		}

		nomes_unicos = set()
		for i in range(1, 199):
			if i <= 100:
				site = f"https://www.olx.com.br/imoveis/aluguel/estado-rj/rio-de-janeiro-e-regiao?o={i}"
			elif i <= 199:
				site = f"https://www.olx.com.br/imoveis/aluguel/estado-rj/rio-de-janeiro-e-regiao?sf=100&o={i}"
			else:
				site = f"https://www.olx.com.br/imoveis/aluguel/estado-rj/rio-de-janeiro-e-regiao?f=c&o={i}"		
			
			await pagina.goto(site, wait_until="domcontentloaded")
			await pagina.wait_for_load_state("domcontentloaded") 

			await pagina.route("**/*", bloquear_pesos)
			
			cards = pagina.locator('.olx-adcard__content')
			todoselementos = await cards.all()
			banco_de_dados_olx = []
			for imovel in todoselementos:
				try:
					nome = await imovel.locator('.typo-body-large.olx-adcard__title.font-semibold').text_content()
					precos = await imovel.locator('h3.typo-body-large.olx-adcard__price.font-semibold').text_content()
					loc = await imovel.locator('.typo-caption.olx-adcard__location').text_content()
					todos_os_precos = await imovel.locator('.olx-adcard__detail').all_text_contents()
					precos_limpos = precos.replace('R$', '.').replace('.', '').strip()
					if nome not in nomes_unicos:
						if len(todos_os_precos) >= 2:
							area = todos_os_precos[1]
							area_limpa = area[:-2].strip()
							if area[-2:] != "m²":
								area = "Não informado"
						else:
							area = "Não informado"

						loc_limpeza = loc.split(",")
						if len(loc_limpeza) >= 2:
							cidade = loc_limpeza[0].strip()
							bairro = loc_limpeza[1].strip()
						else: 
							bairro = "Não informado"
							cidade = loc_limpeza
						if (cidade == "Rio de Janeiro"):
							bairro = mapa_bairros.get(bairro, bairro)
							if area != "Não informado":
								banco_de_dados_olx.append({
									'BAIRRO': bairro,
									'PREÇO': int(precos_limpos),
									'ÁREA': int(area_limpa)
								})
								nomes_unicos.add(nome)

				except Exception:
					precos = "Preço não encontrado"
					loc = "Localização não encontrado"

		await navegador.close()
	return pd.DataFrame(banco_de_dados_olx)

if __name__ == "__main__":
    asyncio.run(scrapper_olx())