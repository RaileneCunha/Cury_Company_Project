#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessarias
import pandas as pd
import streamlit as st
import datetime
import pathlib
import os
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Visão Entregadores", page_icon="https://www.iconfinder.com/icons/1321653/black_man_entregador_job_motoboy_motorcycle_courier_profession_professional_icon",layout="wide")

#---------------------------------------------------------------------------------------------
#Funções
#---------------------------------------------------------------------------------------------
def top_delivers(df1,top_asc):
    df2 = df1[['Delivery_person_ID','City','Time_taken(min)']].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=top_asc).reset_index()
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian' , :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban' , :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban' , :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3


def clean_code(df1):
    """ Está função faz a limpeza do dataframe
    
        Tipos de limpeza:
        1.Remoção dos dados NaN
        2.Mudança do tipo da coluna de dados
        3.Remoção dos espaços das variáveis de texto
        4.Formatação da colunada de datas
        5.Limpeza da coluna de tempo (Remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
        
        """
    # 1. Removendo os NaNs
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City']  != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #2. convertando a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #3. convertando a coluna Order date de texto paa đata
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')
                                  
    #4. convertendo multiple deliveries de texto para nunero inteiro (int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 6. Removendo os espacos dentro de strings/texto/object
    df1.loc[ :, 'ID' ] = df1.loc[: , 'ID' ].str.strip()
    df1.loc[ :, 'Road_traffic_density' ] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[ :, 'Type_of_order' ] = df1.loc[ : , 'Type_of_order'].str.strip()
    df1.loc[ :, 'Type_of_vehicle' ] = df1.loc[ :, 'Type_of_vehicle' ].str.strip()
    df1.loc[ :, 'City' ] = df1.loc [ :, 'City'].str.strip() 
    df1.loc[ :, 'Festival' ] = df1.loc [:, 'Festival' ].str.strip( )

    # 7. Limpando a coluna de time taken 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#-----------------------------Início da estrutura lógica do código------------------------------
#Import dataset
df = pd.read_csv('dataset/train.csv')
#---------------------------------------------------------------------------------------------
#Limpando os dados
df1 = clean_code (df)
#---------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------
# Barra lateral
#---------------------------------------------------------------------------------------------
st.header('Marketplace - Visão Entregadores')
image = Image.open('Nuvem.jpg')
st.sidebar.image(image, width=2000)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data?',
    value = datetime.datetime(2022, 11, 9),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.header(date_slider)
st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Power by Comunidade DS')


# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]


# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]



#---------------------------------------------------------------------------------------------
# LAYOUT NO STREAMLIT
#---------------------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_','_'])

with tab1:
    with st.container():
        st.title('Métricas gerais')
        coluna1, coluna2, coluna3, coluna4 = st.columns(4, gap='large')
        with coluna1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            coluna1.metric('Maior idade',maior_idade)
        with coluna2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            coluna2.metric('Menor idade ',menor_idade)
        with coluna3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            coluna3.metric('Melhor condição',melhor_condicao)
        with coluna4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            coluna4.metric('Pior condição',pior_condicao)

    with st.container():
        st.markdown("""----""")
        st.title('Avaliações')
        coluna1, coluna2 = st.columns(2, gap='large')
        
        with coluna1:
            st.markdown('##### Avaliação média por entregador')
            avaliacao_media = (df1[['Delivery_person_Ratings','Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index())
            st.dataframe(avaliacao_media)
        with coluna2:
            st.markdown('##### Avaliação media por trânsito')
            avaliacao_media_transito = (df1[['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density')['Delivery_person_Ratings'].agg(['mean', 'std']))
            avaliacao_media_transito.columns = ['delivery_mean', 'delivery_str']
            avaliacao_media_transito = avaliacao_media_transito.reset_index()
            st.dataframe(avaliacao_media_transito)
            
            st.markdown('##### Avaliação media por clima')
            avaliacao_media_clima = (df1[['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions')['Delivery_person_Ratings'].agg(['mean', 'std']))
            avaliacao_media_clima.columns = ['delivery_mean', 'delivery_str']
            avaliacao_media_clima = avaliacao_media_clima.reset_index()
            st.dataframe(avaliacao_media_clima)
            
    with st.container():
        st.markdown("""----""")
        st.title('Velocidade de entrega')
        
        coluna1, coluna2 = st.columns(2, gap='large')
        
        with coluna1:
            df3 = top_delivers(df1, top_asc=True)
            st.markdown('##### Entregadores mais rápidos')
            st.dataframe(df3)

        with coluna2:
            df3 = top_delivers(df1, top_asc=False)
            st.markdown('##### Entregadores mais lentos')
            st.dataframe(df3)
