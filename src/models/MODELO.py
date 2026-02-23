import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import os

df = pd.read_csv('data/processed/BAIRROS_RENDA_TOTAL.csv')

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
    elif (row['RENDA MENSAL'] < media_renda) and (row['PREÇO POR METRO'] < media_preco) and (row['ÁREA TERRITORIAL DISPONÍVEL'] > area_maior80):
        return 1  # Risco Médio
    else:
        return 0  # Risco Baixo


df['PROXIMIDADE_RISCO'] = (
    (df['ÍNDICE DE PRESSÃO'] / mediana_pressao) + 
    (df['ÍNDICE DE ACESSIBILIDADE'] / 0.8) + 
    (df['SCORE FINAL'] / mediana_score)
) / 3
df['PRESSAO_VALORIZACAO'] = df['PREÇO POR METRO'] / (df['RENDA MENSAL'] + 1)


df['RISCO_TARGET'] = df.apply(rotular_risco, axis=1)


features = df[['PREÇO POR METRO', 'ÍNDICE DE PRESSÃO', 'ÁREA TERRITORIAL DISPONÍVEL', 'RENDA MENSAL', 'ÍNDICE DE ACESSIBILIDADE', 'SCORE FINAL', 'PROXIMIDADE_RISCO', 'PRESSAO_VALORIZACAO']]
X = features
y = df['RISCO_TARGET']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
smote = SMOTE(random_state=42, k_neighbors=1)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)


param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]

}
rf_base = RandomForestClassifier(random_state=42, class_weight='balanced')

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


probabilidades = modelo.predict_proba(features)

df['RISCO ALTO'] = ((probabilidades[:, 1] * 50) + (probabilidades[:, 2] * 100)).round(2)

df = df.drop(columns= ['PROXIMIDADE_RISCO'])
df = df.drop(columns= ['PRESSAO_VALORIZACAO'])
df = df.drop(columns= ['RISCO_TARGET'])

df = df.sort_values(by='RISCO ALTO', ascending=False).reset_index(drop = True)
print("\n--- RADAR DE GENTRIFICAÇÃO (RISCO 2) ---")
print(df.to_string())

diretorio_atual = os.path.dirname(os.path.abspath(__file__)) 
raiz = os.path.dirname(os.path.dirname(diretorio_atual))

caminho_csv = os.path.join(raiz, 'data', 'processed', 'RISCO DE GENTRIFICAÇÃO.csv')
df.to_csv(caminho_csv, index= False)