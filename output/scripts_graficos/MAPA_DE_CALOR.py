import folium
from folium.plugins import HeatMap
import pandas as pd

df_base = pd.read_csv('data/raw/COORDENADAS.csv')

mapa_rio = folium.Map(location=[-22.9068, -43.1729], zoom_start=11)
dados_calor = df_base[['LATITUDE', 'LONGITUDE', 'RISCO ALTO']].dropna().values.tolist()

HeatMap(
    data=dados_calor,
    radius=25,      
    blur=15, 
    gradient=
        {
    0.0: '#0000FF', # Azul (Seguro - Classe 0)
    0.2: '#00FFFF', # Cyan
    0.4: '#00FF00', # Verde (Início de transição)
    0.6: '#FFFF00', # Amarelo (Risco Médio - Classe 1)
    0.8: '#FF8C00', # Laranja (Quase crítico)
    1.0: '#FF0000'  # Vermelho (Risco Alto - Classe 2 - 100% de Precisão!)
}
).add_to(mapa_rio)
mapa_rio.save('mapa_calor_gentrificacao.html')
