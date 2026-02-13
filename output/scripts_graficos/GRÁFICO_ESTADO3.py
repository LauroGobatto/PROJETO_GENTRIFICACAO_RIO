import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_base = pd.read_csv('data/processed/BAIRROS_RENDA.csv')
df_estado3 = df_base[(df_base['RENDA MENSAL'] >= 7500) & (df_base['PREÇO POR METRO'] >= 40)]
df_estado3 = df_estado3.sort_values(by='ÁREA TERRITORIAL DISPONÍVEL', ascending = False)

plt.figure(figsize=(10,6))
sns.scatterplot(data = df_estado3,
                x = 'RENDA MENSAL',
                y = 'PREÇO POR METRO',
                size = 'ÁREA TERRITORIAL DISPONÍVEL',
                hue = 'ÁREA TERRITORIAL DISPONÍVEL',
                sizes = (100, 2000),
                alpha = 0.7,
                palette = 'viridis')

plt.axhline(y = df_base['PREÇO POR METRO'].quantile(0.85), color = 'red', linestyle = '--', linewidth= 1.5)
plt.axvline(x = df_base['RENDA MENSAL'].quantile(0.85), color = 'blue', linestyle = '--', linewidth= 1.5)
plt.text(16000, 283, 'PÓS GENTRIFICAÇÃO', fontsize = 15, weight = 'bold', verticalalignment = 'top')

destaques = df_estado3[df_base['ÁREA TERRITORIAL DISPONÍVEL'] < df_base['ÁREA TERRITORIAL DISPONÍVEL'].quantile(0.50)]
for i in range(destaques.shape[0]):
    plt.text(x = destaques['RENDA MENSAL'].iloc[i] - 1.0,
             y = destaques['PREÇO POR METRO'].iloc[i] - 0.5,
             s = destaques['BAIRRO'].iloc[i],
             fontsize = 10,
             weight = 'bold',
             color = 'black')


plt.title("Análise de Bairros em Estado de Consolidação Exclusiva (A Pós-Gentrificação): ")
plt.xlabel("Renda mensal dos moradores")
plt.ylabel("Preço por metro quadrado")

plt.legend(bbox_to_anchor = (1.05, 1), loc = 2)

plt.show()