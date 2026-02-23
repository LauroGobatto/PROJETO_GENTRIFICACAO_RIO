from geopy.geocoders import Nominatim
import pandas as pd 
import os

df_riscos = pd.read_csv('data/processed/RISCO DE GENTRIFICAÇÃO.csv')
df_coordenadas = pd.read_csv('data/raw/COORDENADAS.csv')
geolocator = Nominatim(user_agent="meu_projeto_gentrificacao")
df_novo = pd.DataFrame()
coluna_bairro = []
coluna_latitude = []
coluna_longitude = []
for bairro in df_riscos['BAIRRO']:
    if bairro not in df_coordenadas['BAIRRO']:
        local = geolocator.geocode(f"{bairro}, Rio de Janeiro")
        coluna_bairro.append(bairro)
        coluna_latitude.append(local.latitude)
        coluna_longitude.append(local.longitude)

if not coluna_bairro.isna():
    df_novo['BAIRRO'] = coluna_bairro
    df_novo['LATITUDE'] = coluna_latitude
    df_novo['LONGITUDE'] = coluna_longitude
    df = pd.concat([df_coordenadas, df_novo], axis = 0, ignore_index= True)
    caminho_csv = os.path.join('data', 'raw', 'COORDENADAS.csv')
    df.to_csv(caminho_csv, index= False)