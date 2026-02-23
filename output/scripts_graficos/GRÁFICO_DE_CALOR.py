from geopy.geocoders import Nominatim
import pandas as pd 
import os
import time

df_riscos = pd.read_csv('data/processed/RISCO DE GENTRIFICAÇÃO.csv')
df_coordenadas = pd.read_csv('data/raw/COORDENADAS.csv')
geolocator = Nominatim(user_agent="meu_projeto_gentrificacao")
df_novo = pd.DataFrame()
coluna_bairro = []
coluna_latitude = []
coluna_longitude = []
coordenadas = df_riscos['BAIRRO'].unique().tolist()
for bairro in coordenadas:
    if bairro not in df_coordenadas['BAIRRO'].values:
        local = geolocator.geocode(f"{bairro}, Rio de Janeiro")
        if local: 
            coluna_bairro.append(bairro)
            coluna_latitude.append(local.latitude)
            coluna_longitude.append(local.longitude)
            time.sleep(1)

if len(coluna_bairro) > 0:
    df_novo['BAIRRO'] = coluna_bairro
    df_novo['LATITUDE'] = coluna_latitude
    df_novo['LONGITUDE'] = coluna_longitude
    df = pd.concat([df_coordenadas, df_novo], axis = 0, ignore_index= True)
    caminho_csv = os.path.join('data', 'raw', 'COORDENADAS.csv')
    df.to_csv(caminho_csv, index= False)