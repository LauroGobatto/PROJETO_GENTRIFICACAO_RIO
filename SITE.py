import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import sqlite3
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import plotly.graph_objects as go
import matplotlib.pyplot as plt

## MONTAR O MAPA DE CALOR
coordenadas = [-22.9068, -43.1729]
zoom_inicial = 11

def gerar_mapa_calor(lat, long, zoom, df):
    mapa_rio = folium.Map(
        location= [lat, long], 
        zoom_start= zoom
    )
    dados_calor = df[['LATITUDE', 'LONGITUDE', 'RISCO DE GENTRIFICAÇÃO']].dropna()
    HeatMap(
        data= dados_calor,
        radius= 25,
        blur = 15,
        gradient = {
        0.0: '#0000FF', 
        0.2: '#00FFFF', 
        0.4: '#00FF00', 
        0.6: '#FFFF00', 
        0.8: '#FF8C00', 
        1.0: '#FF0000'
    }
    ).add_to(mapa_rio)
    return mapa_rio

def normalizar_dados(df, colunas):
    df_norm = df.copy()
    for col in colunas:
        max_val = df[col].max()
        min_val = df[col].min()
        if max_val != min_val:
            df_norm[col] = (df[col] - min_val) / (max_val - min_val)
        else:
            df_norm[col] = 0.5 
    return df_norm

def criar_grafico_radar(df, categorias):
    fig = go.Figure()

    categorias_fechadas = categorias + [categorias[0]]

    for i, row in df.iterrows():
        valores = row[categorias].tolist()
        valores_fechados = valores + [valores[0]]
        if 'BAIRRO' not in df:
            fig.add_trace(go.Scatterpolar(
                r=valores_fechados,
                theta=categorias_fechadas,
                fill='toself',
                name=f"{row['ESTADOS']}"
            ))
            
            fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1.0] # Ajuste o range conforme seus dados (ex: 0 a 1 ou 0 a 100)
            )),
        showlegend=True
            )

        else:
            fig.add_trace(go.Scatterpolar(
                r=valores_fechados,
                theta=categorias_fechadas,
                fill='toself',
                name=f"{row['BAIRRO']}"
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1] # Ajuste o range conforme seus dados (ex: 0 a 1 ou 0 a 100)
                    )),
            showlegend=True
    )
    return fig

def mostrar_ranking_visual(bairro_selecionado, df, categoria):
    df = df.sort_values(by=f'{categoria}', ascending=True).reset_index(drop=True)
    posicao = df[df['BAIRRO'] == bairro_selecionado].index[0] + 1
    total = len(df)
    percentual = (posicao / total) * 100
    
    # Lógica de cor dinâmica baseada no ranking
    if percentual <= 40:
        cor = "#2ecc71" # Verde (Baixo no ranking)
    elif percentual <= 80:
        cor = "#f1c40f" # Amarelo (Médio)
    else:
        cor = "#e74c3c" # Vermelho (Alto no ranking)

    st.write(f"**{bairro_selecionado}** está na posição **{posicao} de {total}** no ranking de {categoria}.")
    
    # Barra de Progresso Customizada
    st.markdown(f"""
        <div style="background-color: #eee; border-radius: 10px; width: 100%; height: 15px;">
            <div style="background-color: {cor}; width: {percentual}%; height: 15px; border-radius: 10px; transition: width 0.5s;">
            </div>
        </div>
    """, unsafe_allow_html=True)


if 'bairro' not in st.session_state:
    st.session_state.bairro = None
if 'categoria' not in st.session_state:
    st.session_state.categoria = None

def limpar_categoria():
    st.session_state.categoria = None

# Função para limpar o Bairro quando escolher Categoria
def limpar_bairro():
    st.session_state.bairro = None

@st.cache_data # Para o site ficar rápido
def carregar_dados():
    conexao = sqlite3.connect('data/processed/GENTRIFICACAO_TOTAL.db')
    query = "SELECT * FROM bairros"
    banco_de_dados = pd.read_sql_query(query, conexao)
    conexao.close()
    return banco_de_dados

df = carregar_dados()

df.columns = ['BAIRRO', 'PREÇO POR METRO QUADRADO', 'UNIDADES RESIDENCIAIS', 'ÍNDICE DE PRESSÃO', 'ÁREA TERRITORIAL DISPONÍVEL', 'MAGNITUDE', 'ÍNDICE DE INFORMALIDADE', 'RENDA MENSAL', 'TAXA DE ESFORÇO', 'LATITUDE', 'LONGITUDE', 'VARIAÇÃO DO PREÇO MENSAL', 'RISCO TARGET', 'RISCO DE GENTRIFICAÇÃO']

colunas_radar = ['RENDA MENSAL', 'PREÇO POR METRO QUADRADO', 'TAXA DE ESFORÇO', 'MAGNITUDE', 'ÁREA TERRITORIAL DISPONÍVEL', 'UNIDADES RESIDENCIAIS', 'ÍNDICE DE PRESSÃO', 'ÍNDICE DE INFORMALIDADE']
df_normalizado = normalizar_dados(df, colunas_radar)

media_renda = df['RENDA MENSAL'].mean()
media_preco = df['PREÇO POR METRO QUADRADO'].mean()
area_maior85 = df['ÁREA TERRITORIAL DISPONÍVEL'].quantile(0.85)
mediana_magnitude = df['MAGNITUDE'].median()
mediana_pressao = df['ÍNDICE DE PRESSÃO'].median()
preco_maior80 = df['PREÇO POR METRO QUADRADO'].quantile(0.80)
renda_maior80 = df['RENDA MENSAL'].quantile(0.80)
area_menor50 = df['ÁREA TERRITORIAL DISPONÍVEL'].quantile(0.50)

bairros_2 = (df['RISCO TARGET'] == 2)
df.loc[bairros_2, 'ESTADOS'] = "ESTADO2"

ainda_vazio = df['ESTADOS'].isna()

bairros_1 = (df['RISCO TARGET'] == 1)
df.loc[bairros_1 & ainda_vazio, 'ESTADOS'] = "ESTADO1"

bairros_3 = (df['PREÇO POR METRO QUADRADO'] > preco_maior80) & (df['RENDA MENSAL'] > renda_maior80)
df.loc[bairros_3 & ainda_vazio, 'ESTADOS'] = "ESTADO3"

df['ESTADOS'] = df['ESTADOS'].fillna("ESTADO4")

df_normalizado['ESTADOS'] = df['ESTADOS']

# Configuração da Página
st.set_page_config(page_title="Radar de Gentrificação RJ", layout="wide")

# --- TÍTULO E INTRODUÇÃO ---
st.title("Radar de Risco de Gentrificação - Rio de Janeiro")
st.markdown("""
Esta ferramenta utiliza **Machine Learning (Random Forest)** para identificar áreas com maior pressão imobiliária 
e risco de gentrificação, baseando-se em renda, preço por metro e área territorial disponível. Também, todos as conclusões teóricas desse projeto derivam do geográfo inglês Neil Smith.
""")

if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("Menu de Navegação")



if st.session_state.pagina == 'home':
        if 'mostrar_radar' not in st.session_state:
            st.session_state.mostrar_radar = False
        if st.sidebar.button("Comparar bairros"):
            st.session_state.mostrar_radar = True
            
        if st.sidebar.button("Estágios da Gentrificação"):
            st.session_state == False
            st.session_state.pagina = 'detalhes'
            st.rerun()
if st.session_state.pagina == 'detalhes':
        if st.sidebar.button("⬅ Voltar para Home"):
            st.session_state.pagina = 'home'
            st.session_state.mostrar_radar= False
            st.rerun()


if st.session_state.pagina == 'home':
    if st.session_state.mostrar_radar == False:
        bairro_alvo = st.sidebar.selectbox("Selecione um bairro para análise detalhada", 
                                   options = df['BAIRRO'].unique(),
                                   key='bairro',
                                   index= None,
                                   placeholder= "Selecionar bairro...",
                                   on_change = limpar_categoria)
    
        if (bairro_alvo == None):
    # --- MAPA INTERATIVO (FOLIUM) ---
            st.title("Visualização do Mapa de Calor")

            mapa_rio = gerar_mapa_calor(-22.9068, -43.1729, 11, df)
            st_folium(mapa_rio, width=1200, height=500)
    
            st.subheader("Principais Fatores de Risco")
            with st.expander("Área Territorial Disponível"):
                st.info("Terrenos que não têm construções ou uso, coletados pelo DATA.RIO. De acordo com o machine learning, o modelo de Random Forest identificou o vazio" \
                " urbano como um fator determinante para a classificação de risco de gentrificação, corroborando a hipótese de que a disponibilidade é o principal vetor da pressão imobiliária no Rio de Janeiro.")
            with st.expander("Unidades Residenciais"):
                st.info("São estruturas físicas independentes destinadas exclusivamente à habitação, como apartamentos, casas ou estúdios. Esse número representa a densidade "\
                "habitacional do bairro. Esses dados foram coletados pelo DATA.RIO.")
            with st.expander("Renda Mensal"):
                st.info ("Representa o poder de compra médio de um morador comum. O dado é a mediana da renda mensal de moradores de cada bairro, coletada pelo Censo de 2022 " \
                "e aplicada aos juros de 2026. É o fator de vulnerabilidade social.")
            with st.expander("Preço por Metro Quadrado"):
                st.info("Indica o valor de mercado atual da região. Dado coletado após uma análise de mais de 12 mil anúncios de aluguel na cidade do Rio de Janeiro e fazer uma " \
                "mediana do preço por metro de cada bairro. Esse fator representa o valor simbólico do solo.")
            with st.expander("Pressão Imobiliária"):
                st.info("Cruzamento de dados entre o número de unidades residenciais e o preço por metro quadrado. Quanto menor o número de unidades residenciais em um bairro com " \
                "um preço por metro alto, indica uma pressão imobiliária para construção de novos empreendimentos ou para verticalizar.")
            with st.expander("Magnitude do Impacto Imobiliário"):
                st.info("Cruzamento de dados entre pressão imobiliária e área territorial disponível. A magnitude dos impactos da pressão imobiliária depende da área territorial disponível " \
                "para uso, pois onde o vazio urbano é vasto e o preço começa a subir, o capital imobiliário desloca-se para essas regiões de 'fronteira' para criar novos mercados. Esse fator identifica exatamente onde essa fronteira está se movendo atualmente.")
            with st.expander("Taxa de esforço"):
                st.info("Fator que surgiu do cruzamento da renda mensal do bairro com o seu preço por metro. Ao cruzar a renda mensal do bairro com o preço de um bairro de 50 metros quadrados "
                "(padrão para famílias pequenas no urbanismo), temos quanto o aluguel toma da renda de um morador comum. Identifica quando um bairro está expulsando moradores originais, sendo 1.0 significando que a renda mensal equivale a um apartamento de 50 metros quadrados.")

# --- ANÁLISE DETALHADA ---
        st.divider()
        col1, col2 = st.columns(2)
        if bairro_alvo: 
            with col1:
                st.subheader(f'Análise: {bairro_alvo}')
                dados_bairro = df[df['BAIRRO'] == bairro_alvo].iloc[0]
                st.metric("Probabilidade de Risco Alto", f"{dados_bairro['RISCO DE GENTRIFICAÇÃO']}%")

                st.write(f"#### Preço por Metro (atualmente): R$ {(dados_bairro['PREÇO POR METRO QUADRADO']).round(2)}")
                grafico = mostrar_ranking_visual(bairro_alvo, df_normalizado, 'PREÇO POR METRO QUADRADO')
                st.divider()
                st.write(f"#### Taxa de Esforço: {dados_bairro['TAXA DE ESFORÇO']:.2f}")
                grafico = mostrar_ranking_visual(bairro_alvo, df_normalizado, 'TAXA DE ESFORÇO')
                st.divider()
                st.write(f"#### Pressão Imobiliária: {dados_bairro['ÍNDICE DE PRESSÃO']} / 5.0")
                grafico = mostrar_ranking_visual(bairro_alvo, df_normalizado, 'ÍNDICE DE PRESSÃO')
                st.divider()
                st.write(f"#### Magnitude do Impacto Imobiliário: {dados_bairro['MAGNITUDE']:.2f} / 5.0")
                grafico = mostrar_ranking_visual(bairro_alvo, df_normalizado, 'MAGNITUDE')
                st.divider()
        
            with col2:
                estado_bairro = df.loc[df['BAIRRO'] == bairro_alvo, 'ESTADOS'].values[0]
                if estado_bairro == "ESTADO1":
                    st.warning("PRÉ-GENTRIFICAÇÃO")
                if estado_bairro == "ESTADO2":
                    st.error("GENTRIFICAÇÃO ATIVA")
                if estado_bairro == "ESTADO3":
                    st.info("PÓS-GENTRIFICAÇÃO")
                if estado_bairro == "ESTADO4":
                    st.success("BAIRROS ESTÁVEIS")

                dados_coordenadas = df[df['BAIRRO'] == bairro_alvo].iloc[0]
                latitude = dados_coordenadas['LATITUDE']
                longitude = dados_coordenadas['LONGITUDE']
                mapa_rio = gerar_mapa_calor(latitude, longitude, 14, df)
                st_folium(mapa_rio, width=500, height=500)


    if st.session_state.mostrar_radar == True: 
        st.header("Radar de Atributos por Bairro")
    
        if st.button("Fechar Radar"):
            st.session_state.mostrar_radar = False
            st.rerun()
    
        bairros_escolhidos = st.multiselect("Compare os Bairros:", df['BAIRRO'].unique())

        if bairros_escolhidos:
            df_filtrado = df_normalizado[df_normalizado['BAIRRO'].isin(bairros_escolhidos)]
            grafico = criar_grafico_radar(df_filtrado, colunas_radar)
            st.plotly_chart(grafico)
        else:
            st.warning("Selecione pelo menos um bairro para ver a teia!")




elif st.session_state.pagina == 'detalhes':

        categoria_alvo = st.sidebar.selectbox("Selecione um estado da gentrificação para analisar",
                              options = ['PRÉ-GENTRIFICAÇÃO', 'GENTRIFICAÇÃO ATIVA', 'PÓS-GENTRIFICAÇÃO',
                               'ESTÁVEIS'],
                               key='categoria',
                              index = None,
                              placeholder= "Selecionar estado...",
                              on_change = limpar_bairro)
        
        if (categoria_alvo == None):
            st.header("GRÁFICO DOS ESTADOS DE GENTRIFICAÇÃO")
            dicionario_estados = {
                'ESTADO1': 'PRÉ-GENTRIFICAÇÃO',
                'ESTADO2': 'GENTRIFICAÇÃO ATIVA',
                'ESTADO3': 'PÓS-GENTRIFICAÇÃO',
                'ESTADO4': 'BAIRROS ESTÁVEIS'
            }
            df_estados = df_normalizado.groupby('ESTADOS').median(numeric_only = True).reset_index()
            df_estados['ESTADOS'] = df_estados['ESTADOS'].map(dicionario_estados)

            grafico_estados = criar_grafico_radar(df_estados, colunas_radar)
            st.plotly_chart(grafico_estados)
            st.caption("Mediana de todos os bairros dentro de cada grupo para encontrar o grupo modelo de cada estágio")
            st.write("\t A pós-gentrificação está na liderança do preço por metro, renda mensal e unidades residenciais. O fato mais interessante tirado desse gráfico é a unidade residencial que não está nos fatores diretos que determinam esse estado da gentrificação, porém pode ser considerado um, já que um bairro após passar pela gentrificação vai possuir uma grande quantidade de unidades residenciais por já ter sido um bairro com grande foco imobiliário.\n\n" \
                     "\t Já no estágio da gentrificação ativa, temos a segunda menor renda mensal e preço por metro do gráfico e a maior taxa de esforço, o que indica que aqui o foco está na retirada dos moradores originais desses bairros , que, junto a liderança no fator de pressão imobiliária, mostra que essa pressão está expulsando seus moradores originais.\n\n" \
                     "\t Na pré-gentrificação, nós temos o menor número de unidades residenciais do gráfico, com a maior área territorial do gráfico que, juntamente a liderança na magnitude da pressão imobiliária pode atrair o interesse da indústria imobiliária no futuro." \
                     "\t Já nos bairros estáveis podemos ver todos os fatores são comedidos, com nenhum sendo extremo.")


        st.divider()
        col1, col2 = st.columns(2)
        if categoria_alvo:
            if categoria_alvo == "PRÉ-GENTRIFICAÇÃO":
                with col1:
                    st.subheader("PRÉ-GENTRIFICAÇÃO")
                    st.warning("Para que um bairro seja gentrificado no futuro, ele precisa ser desvalorizado no presente. O movimento geográfico do capital consiste na migração do capital para outras fronteiras, para assim, o lucro seja maximizado em uma área. Segundo Neil Smith, a gentrificação começa, décadas antes, com o desinvestimento. Após esse desinvestimento, o valor de construções e áreas caem drasticamente, enquanto o valor da terra potencial permanece dormente.\n\n" \
                    "O conceito central da gentrificação para Neil Smith é o Rent Gap, que o pesquisador define como a disparidade entre o valor que a terra renda atualmente com seu uso e o valor poderia render se fosse utilizada para seu “melhor e mais alto uso, como por exemplo, construção de condomínios de luxo.  Quando essa lacuna (o 'gap') fica grande o suficiente, a gentrificação torna-se economicamente irresistível para as incorporadoras. O desinvestimento é, portanto, o preparo do terreno para a revalorização futura.\n\n " \
                    "É possível identificar bairros nesse estado quando a renda mensal de seus moradores é baixa ou estagnada, com um preço por metro quadrado baixo em relação com a média da cidade e com uma grande área territorial disponível.")
                with col2:
                    st.subheader("Bairros nesse estado:")
                    bairros1 = df[df['ESTADOS'] == "ESTADO1"]
                    for bairro in bairros1['BAIRRO']:
                        st.write(f"- {bairro}")

            if categoria_alvo == "GENTRIFICAÇÃO ATIVA":
                with col1:
                    st.subheader("GENTRIFICAÇÃO ATIVA")
                    st.error("É o momento em que o capital decide retornar ao bairro. Quando o diferencial entre o valor atual do solo e o seu valor potencial atinge o ápice, o capital volta para dentro dessas áreas. Para Neil Smith, este estado é uma estratégia econômica deliberada. Ocorre então a transição do valor de uso (moradia popular) para o valor de troca (ativo imobiliário).\n\n " \
                    "O fator Pressão imobiliária representa a agressividade do reinvestimento. Quando esse fator é alto, indica que a velocidade com que o mercado está tentando converter o solo é maior do que a capacidade do bairro de manter sua estrutura original.\n\n" \
                    "Já o fator Magnitude da Pressão imobiliária representa o potencial da gentrificação. A gentrificação não é um evento isolado e precisa de escala para ser lucrativa. Bairros com grande magnitude são áreas onde há muita área disponível para lucro com uma grande intenção de compra. Esses bairros terão a paisagem urbana alterada de forma irreversível nos próximos anos.\n\n" \
                    "A taxa e esforço é o rastro social do projeto. Quando a taxa de esforço chega perto dos 1.0, indica que está havendo uma expulsão do morador original pois a habitação está consumindo boa parte de sua renda, tornando a sua permanência matematicamente impossível.")
                with col2:
                    st.subheader("Bairros nesse estado:")
                    bairros2 = df[df['ESTADOS'] == "ESTADO2"]
                    for bairro in bairros2['BAIRRO']:
                        st.write(f"- {bairro}")

            if categoria_alvo == "PÓS-GENTRIFICAÇÃO":
                with col1:
                    st.subheader("PÓS-GENTRIFICAÇÃO")
                    st.info("A pós-gentrificação é o estágio que parece, de fora, um caso de sucesso. São bairros caros no sentido mais completo da palavra: preços entre os mais altos da cidade, e moradores com renda suficiente para sustentá-los. " \
                    "O rent gap foi fechado. Mas a característica mais reveladora desse estágio é o que está ausente. Não há terra disponível. O território está completamente construído e adensado.\n\n " \
                    "Não há assentamentos informais dentro dos limites, ou quase nenhum: a cidade formal fechou sobre eles. Santos (1996) chamou esse tipo de espaço de ilha técnica, um território cuja infraestrutura é calibrada para reproduzir a acumulação de capital, e não para servir ao tecido social da cidade. " \
                    "As altas taxas de condomínio, a segurança privatizada, o comércio de nicho: não são amenidades. São mecanismos de filtragem que garantem que os novos moradores também não sejam deslocados por quem não puder pagar pela versão da cidade que está sendo produzida ali.")
                with col2:
                    st.subheader("Bairros nesse estado:")
                    bairros3 = df[df['ESTADOS'] == "ESTADO3"]
                    for bairro in bairros3['BAIRRO']:
                        st.write(f"- {bairro}")

            if categoria_alvo == "ESTÁVEIS":
                with col1:
                    st.subheader("ESTÁVEIS")
                    st.success("Os bairros estáveis são aqueles que o modelo alcança por eliminação. Não são pobres o suficiente para atrair o interesse especulativo sobre sua terra. " \
                    "Não estão sob pressão suficiente para estar em processo ativo de conversão. Não são caros o suficiente, nem seus moradores ricos o suficiente, para ter completado o ciclo.\n\n " \
                    "Existem em um equilíbrio provisório: moradores gastando uma parcela razoável da renda com moradia, o mercado imobiliário presente mas não agressivo, o tecido urbano misto e sem grandes destaques. " \
                    "Nada aqui está em um ponto de inflexão. Equilíbrio não é uma condição protegida em uma cidade com os níveis de pressão especulativa do Rio. É, mais precisamente, o estágio anterior à chegada dessa pressão.")
                with col2:
                    st.subheader("Bairros nesse estado:")
                    bairros4 = df[df['ESTADOS'] == "ESTADO4"]
                    col1, col2 = st.columns(2)
                    contagem = bairros4['BAIRRO'].count()
                    i = 0
                    for bairro in bairros4['BAIRRO']:
                        if i < (contagem / 2):
                            with col1:
                                st.write(f"- {bairro}")
                                i = i + 1
                        else:
                            with col2:
                                st.write(f"- {bairro}")

    
    
# --- FOOTER ---
st.caption("Desenvolvido como projeto prático do curso DSA - Janeiro/Abril 2026")