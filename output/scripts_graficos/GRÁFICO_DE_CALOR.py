from geopy.geocoders import Nominatim
import pandas as pd 

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

df_riscos.to_csv('COORDENADAS.csv', index = False)