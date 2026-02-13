import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_base = pd.read_csv('data/processed/BAIRROS_RENDA.csv')
df_estado4 = df_base[(df_base['ÍNDICE DE ACESSIBILIDADE'] <= 0.5) & (df_base['SCORE FINAL'] <= 1.5)]

plt.figure(figsize=(10,6))
sns.scatterplot(data = df_estado4,
                x = 'ÍNDICE DE ACESSIBILIDADE',
                y = 'SCORE FINAL',
                s = 250,
                alpha = 0.7,
                color = 'purple'
                )

plt.axhline(y = df_base['SCORE FINAL'].quantile(0.10), color = 'red', linestyle = '--', linewidth= 1.5)
plt.axvline(x = 0.4, color = 'blue', linestyle = '--', linewidth= 1.5)
plt.text(0.28, 1.00, 'Estabilidade', fontsize = 15, weight = 'bold', verticalalignment = 'top')

destaques = df_base[(df_base['SCORE FINAL'] < 1.07) & (df_base['ÍNDICE DE ACESSIBILIDADE'] <= 0.4) ]
for i in range(destaques.shape[0]):
    plt.text(x = destaques['ÍNDICE DE ACESSIBILIDADE'].iloc[i],
             y = destaques['SCORE FINAL'].iloc[i] - 0.008,
             s = destaques['BAIRRO'].iloc[i],
             fontsize = 10,
             weight = 'bold',
             color = 'black')


plt.title("Análise de Bairros em Estado de Filtragem (Estabilidade Vulnerável): ")
plt.xlabel("'Índice de acessibilidade")
plt.ylabel("Score final")

plt.legend(bbox_to_anchor = (1.05, 1), loc = 2)

plt.show()