import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_base = pd.read_csv('data/processed/BAIRROS_RENDA.csv')
df_estado2 = df_base[(df_base['ÍNDICE DE PRESSÃO'] >= 0.5)]
df_estado2 = df_estado2.sort_values(by='ÍNDICE DE ACESSIBILIDADE', ascending = True)

plt.figure(figsize=(10,6))
sns.scatterplot(data = df_estado2,
                x = 'ÍNDICE DE PRESSÃO',
                y = 'SCORE FINAL',
                size = 'ÍNDICE DE ACESSIBILIDADE',
                hue = 'ÍNDICE DE ACESSIBILIDADE',
                sizes = (100, 2000),
                alpha = 0.7,
                palette = 'viridis')
media_x = df_base['ÍNDICE DE PRESSÃO'].median()
media_y = df_base['SCORE FINAL'].median()
plt.axhline(y = media_y, color = 'red', linestyle = '--', linewidth= 1.5)
plt.axvline(x = media_x, color = 'blue', linestyle = '--', linewidth= 1.5)
plt.text(2.5, 3.5, 'GENTRIFICAÇÃO ATIVA', fontsize = 15, weight = 'bold', verticalalignment = 'top')

destaques = df_base[(df_base['ÍNDICE DE ACESSIBILIDADE'] > 0.8) & (df_base['SCORE FINAL'] > media_y)]
for i in range(destaques.shape[0]):
    plt.text(x = destaques['ÍNDICE DE PRESSÃO'].iloc[i] - 0.03,
             y = destaques['SCORE FINAL'].iloc[i] - 0.03,
             s = destaques['BAIRRO'].iloc[i],
             fontsize = 10,
             weight = 'bold',
             color = 'black')


plt.title("Análise de Bairros em Estado de Fronteira Especulativa (Gentrificação Ativa): ")
plt.xlabel("Índice de Pressão")
plt.ylabel("Score final")

plt.legend(bbox_to_anchor = (1.05, 1), loc = 2)

plt.show()