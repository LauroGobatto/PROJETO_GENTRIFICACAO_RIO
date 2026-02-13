import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


df_base = pd.read_csv('data/processed/BAIRROS_RENDA.csv')
df_baixaclasse = df_base[(df_base['RENDA MENSAL'] <= 12500) & (df_base['PREÇO POR METRO'] <= 150)]
df_baixaclasse = df_baixaclasse.sort_values(by='ÁREA TERRITORIAL DISPONÍVEL', ascending = True)


plt.figure(figsize=(10,6))
sns.scatterplot(data = df_baixaclasse,
                x = 'RENDA MENSAL',
                y = 'PREÇO POR METRO',
                size = 'ÁREA TERRITORIAL DISPONÍVEL',
                hue = 'ÁREA TERRITORIAL DISPONÍVEL',
                sizes = (100, 2000),
                alpha = 0.7,
                palette = 'viridis')


media_x = df_base['RENDA MENSAL'].mean()
media_y = df_base['PREÇO POR METRO'].mean()
plt.axhline(y = media_y, color = 'red', linestyle = '--', linewidth= 1.5)
plt.axvline(x = media_x, color = 'blue', linestyle = '--', linewidth= 1.5)
plt.text(media_x * 0.45, media_y * 1.1, 'PRÉ-GENTRIFICAÇÃO', fontsize = 15, weight = 'bold', verticalalignment = 'top')


destaques = df_base[df_base['ÁREA TERRITORIAL DISPONÍVEL'] > df_base['ÁREA TERRITORIAL DISPONÍVEL'].quantile(0.85)]
for i in range(destaques.shape[0]):
    plt.text(x = destaques['RENDA MENSAL'].iloc[i] - 1.0,
             y = destaques['PREÇO POR METRO'].iloc[i] - 0.5,
             s = destaques['BAIRRO'].iloc[i],
             fontsize = 10,
             weight = 'bold',
             color = 'black')




plt.title("Análise de Bairros em Estado de Desinvestimento Planejado (A Pré-Gentrificação): ")
plt.xlabel("Renda mensal dos moradores")
plt.ylabel("Preço por metro quadrado")


plt.legend(bbox_to_anchor = (1.05, 1), loc = 2)


plt.show()
