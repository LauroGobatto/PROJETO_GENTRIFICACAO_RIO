import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsRegressor
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import zscore
import os
import shap


df_total = pd.read_csv('data/processed/COORDENADAS.csv')
df_anterior = pd.read_csv('data/processed/monthly/BAIRROS_RENDA_2026_01.csv')
df_atual = pd.read_csv('data/processed/monthly/BAIRROS_RENDA_2026_02.csv')

df_anterior.rename(columns={
    'PREÇO POR METRO': 'PREÇO POR METRO ANTERIOR'},
    inplace= True)
df_atual.rename(columns={
    'PREÇO POR METRO': 'PREÇO POR METRO ATUAL'},
    inplace= True
)

df_comparacao = pd.merge(df_anterior[['BAIRRO', 'PREÇO POR METRO ANTERIOR']], df_atual[['BAIRRO', 'PREÇO POR METRO ATUAL']], on='BAIRRO', how='inner')
df_comparacao['VARIAÇÃO DE PREÇO MENSAL'] = ((df_comparacao['PREÇO POR METRO ATUAL'] - df_comparacao['PREÇO POR METRO ANTERIOR']) * 100) / df_comparacao['PREÇO POR METRO ANTERIOR']
df = pd.merge(df_total, df_comparacao[['BAIRRO', 'VARIAÇÃO DE PREÇO MENSAL']], on='BAIRRO', how= 'left')
df['VARIAÇÃO DE PREÇO MENSAL'] = df['VARIAÇÃO DE PREÇO MENSAL'].fillna(0)

media_renda = df['RENDA MENSAL'].mean()
media_preco = df['PREÇO POR METRO'].mean()
area_maior80 = df['ÁREA TERRITORIAL DISPONÍVEL'].quantile(0.80)
mediana_score = df['SCORE FINAL'].median()
mediana_pressao = df['ÍNDICE DE PRESSÃO'].median()
preço_maior85 = df['PREÇO POR METRO'].quantile(0.85)
renda_maior85 = df['RENDA MENSAL'].quantile(0.85)
area_menor50 = df['ÁREA TERRITORIAL DISPONÍVEL'].quantile(0.50)

def rotular_risco(row):
    if (row['ÍNDICE DE ACESSIBILIDADE'] > 0.8) and (row['SCORE FINAL'] > mediana_score) and (row['ÍNDICE DE PRESSÃO'] > mediana_pressao):
        return 2  # Risco Alto
    elif (row['RENDA MENSAL'] < media_renda) and (row['ÍNDICE DE PRESSÃO'] > mediana_pressao) and (row['ÁREA TERRITORIAL DISPONÍVEL'] > area_maior80):
        return 1
    elif (row['ÍNDICE DE ACESSIBILIDADE'] > 0.5) and (row['RENDA MENSAL'] < media_renda) and (row['ÁREA TERRITORIAL DISPONÍVEL'] > area_maior80):
        return 1
    else:
        return 0  # Risco Baixo


df['POTENCIAL_TRANSFORMACAO'] = (zscore(df['ÍNDICE DE PRESSÃO']) + 
                                zscore(df['ÍNDICE DE ACESSIBILIDADE'])) / 2

df['RISCO_TARGET'] = df.apply(rotular_risco, axis=1)

features_base = [
    'PREÇO POR METRO', 'ÍNDICE DE PRESSÃO', 'ÁREA TERRITORIAL DISPONÍVEL', 
    'RENDA MENSAL', 'ÍNDICE DE ACESSIBILIDADE', 'SCORE FINAL', 
    'VARIAÇÃO DE PREÇO MENSAL', 'POTENCIAL_TRANSFORMACAO'
]

X = df[features_base]
y = df['RISCO_TARGET']
coords = df[['LATITUDE', 'LONGITUDE'] ]

X_train, X_test, y_train, y_test, coords_train, coords_test = train_test_split(
    X, y, coords, test_size=0.2, random_state=42, stratify=y
)

knn_contagio = KNeighborsRegressor(n_neighbors=3)
knn_contagio.fit(coords_train, y_train)

X_train = X_train.copy()
X_test = X_test.copy()

X_train['RISCO_VIZINHANCA'] = knn_contagio.predict(coords_train)
X_test['RISCO_VIZINHANCA'] = knn_contagio.predict(coords_test)

# 3. Normalização para o SHAP não "esmagar" o dado
scaler = MinMaxScaler()
X_train['RISCO_VIZINHANCA'] = scaler.fit_transform(X_train[['RISCO_VIZINHANCA']])
X_test['RISCO_VIZINHANCA'] = scaler.transform(X_test[['RISCO_VIZINHANCA']])

# O modelo 'knn_contagio' já foi treinado lá atrás com coords_train e y_train
df['RISCO_VIZINHANCA'] = knn_contagio.predict(df[['LATITUDE', 'LONGITUDE']])

# 2. Aplicar o Scaler (importante: use o scaler que foi fitado no treino!)
df['RISCO_VIZINHANCA'] = scaler.transform(df[['RISCO_VIZINHANCA']])

# Agora o SMOTE vai funcionar sobre dados equilibrados
smote_custom = SMOTE(random_state=42, k_neighbors=3) 
smote = SMOTETomek(random_state=42, smote=smote_custom)

X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

rf_base = RandomForestClassifier(random_state=42, class_weight='balanced')
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]

}
grid_search = GridSearchCV(rf_base , param_grid, cv=5)
grid_search.fit(X_train_res, y_train_res)
melhor_rf = grid_search.best_estimator_
modelo_gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=3, random_state=42)
modelo = VotingClassifier(
    estimators=[('rf', melhor_rf), ('gb', modelo_gb)],
    voting='soft'
)


modelo.fit(X_train_res, y_train_res)


y_pred = modelo.predict(X_test)
print("\n--- RELATÓRIO DE DESEMPENHO ---")
print(classification_report(y_test, y_pred, zero_division=0))


features = [
    'PREÇO POR METRO', 'ÍNDICE DE PRESSÃO', 'ÁREA TERRITORIAL DISPONÍVEL', 
    'RENDA MENSAL', 'ÍNDICE DE ACESSIBILIDADE', 'SCORE FINAL', 
    'VARIAÇÃO DE PREÇO MENSAL', 'POTENCIAL_TRANSFORMACAO', 'RISCO_VIZINHANCA'
]


probabilidades = modelo.predict_proba(df[features])

df['RISCO ALTO'] = ((probabilidades[:, 1] * 50) + (probabilidades[:, 2] * 100)).round(2)

df = df.drop(columns= ['POTENCIAL_TRANSFORMACAO'])
df = df.drop(columns= ['RISCO_TARGET'])
df = df.drop(columns= ['RISCO_VIZINHANCA'])

df = df.sort_values(by='RISCO ALTO', ascending=False).reset_index(drop = True)
print("\n--- RADAR DE GENTRIFICAÇÃO (RISCO 2) ---")
print(df.to_string())

diretorio_atual = os.path.dirname(os.path.abspath(__file__)) 
raiz = os.path.dirname(os.path.dirname(diretorio_atual))

caminho_csv = os.path.join(raiz, 'data', 'processed', 'RISCO DE GENTRIFICAÇÃO.csv')
df.to_csv(caminho_csv, index= False)

background = shap.sample(X_train, 50) 

model_func = lambda x: modelo.predict_proba(x)


explainer = shap.KernelExplainer(model_func, background)


X_test_sample = X_test.sample(10, random_state=42)
shap_values = explainer.shap_values(X_test_sample)


if isinstance(shap_values, list):
    shap.summary_plot(shap_values[2], X_test_sample)
else:
    shap.summary_plot(shap_values[:,:,2], X_test_sample)