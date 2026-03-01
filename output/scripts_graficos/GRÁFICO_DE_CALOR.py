from geopy.geocoders import Nominatim
import pandas as pd
import time
import os

df_riscos = pd.read_csv('/home/laurogobatto/Projeto_Alugueis/data/processed/BAIRROS_RENDA_TOTAL.csv')
geolocator = Nominatim(user_agent="meu_projeto_gentrificacao")

coluna_latitude = []
coluna_longitude = []

for bairro in df_riscos['BAIRRO']:
    local = geolocator.geocode(f"{bairro}, Rio de Janeiro")
    coluna_latitude.append(local.latitude)
    coluna_longitude.append(local.longitude)
    time.sleep(2)

df_riscos['LATITUDE'] = coluna_latitude
df_riscos['LONGITUDE'] = coluna_longitude

caminho_csv = os.path.join('data', 'processed', 'COORDENADAS.csv')
df_riscos.to_csv('/home/laurogobatto/Projeto_Alugueis/data/processed/COORDENADAS.csv', index = False)