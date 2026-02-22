from geopy.geocoders import Nominatim
import pandas as pd 
import os

df_riscos = pd.read_csv('data/processed/RISCO DE GENTRIFICAÇÃO.csv')

geolocator = Nominatim(user_agent="meu_projeto_gentrificacao")
coluna_latitude = []
coluna_longitude = []
for bairro in df_riscos['BAIRRO']:
    local = geolocator.geocode(f"{bairro}, Rio de Janeiro")
    coluna_latitude.append(local.latitude)
    coluna_longitude.append(local.longitude)

df_riscos['LATITUDE'] = coluna_latitude
df_riscos['LONGITUDE'] = coluna_longitude

caminho_csv = os.path.join('data', 'raw', 'COORDENADAS.csv')
df_riscos.to_csv(caminho_csv, index= False)