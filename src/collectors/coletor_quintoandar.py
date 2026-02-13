import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def bloquear_pesos(route):
    if route.request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()

async def scrapper_quintoandar():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context(
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
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
       

        pagina = await contexto.new_page ()
        await pagina.route("**/*", bloquear_pesos)
        await pagina.goto ("https://www.quintoandar.com.br/alugar/imovel/rio-de-janeiro-rj-brasil", wait_until = "domcontentloaded")
        await pagina.wait_for_load_state("load")


        for i in range(370):
            botao_ver_mais = pagina.get_by_role("button", name="Ver mais")
            try:
                if await botao_ver_mais.is_visible():
                    await botao_ver_mais.click()
                    await pagina.wait_for_timeout(6000)
            except:
                break

        cards = pagina.locator('.Cozy__CardBlock-Container._2pfuCF.znH6Fs')
        todoselementos = await cards.all()
        bairros_unicos = set()

        banco_de_dados_quintoandar = []

        for i, imovel in enumerate(todoselementos, 1):

            loc = await imovel.locator('h2.CozyTypography.xih2fc._72Hu5c.Ci-jp3').text_content()
            area = await imovel.locator('.CozyTypography.FindHouseCard_amenitiesText__QNzFn.xih2fc.EKXjIf.A68t3o').text_content()
            precos = await imovel.locator('.CozyTypography.xih2fc._72Hu5c.Ci-jp3').all_text_contents()
            precos1 = precos[0]
            precos_limpos = precos1.replace('R$', '.').replace('total', '.').replace('.', '').strip()
            area_limpa = area.split("·")
            area_boa = area_limpa[0].replace('m²', '').strip()
            loc_limpa = loc.replace('·', ',').split(',')
            bairro = loc_limpa[1].strip()
            bairro = mapa_bairros.get(bairro, bairro)
            bairros_unicos.add(bairro)

            banco_de_dados_quintoandar.append({
                'ID': 1000 + i,
                'BAIRRO': bairro.strip(),
                'PREÇO': int(precos_limpos),
                'ÁREA': int(area_boa),
            })

        await navegador.close()
    return pd.DataFrame(banco_de_dados_quintoandar)


if __name__ == "__main__":
    asyncio.run(scrapper_quintoandar())