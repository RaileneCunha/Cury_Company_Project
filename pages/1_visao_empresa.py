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

st.set_page_config(page_title="Visão Empresa", page_icon="https://www.iconfinder.com/icons/4263514/ddos_protection_server_shield_icon",layout="wide")

#---------------------------------------------------------------------------------------------
#Funções
#---------------------------------------------------------------------------------------------
def country_maps(df1):
    """ Está função mostra o mapa das cidades por tipo de tráfego """
    # Agrupando os dados para obter o valor mediano
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Criando o mapa base
    map = folium.Map(location=[df_aux['Delivery_location_latitude'].mean(), df_aux['Delivery_location_longitude'].mean()], zoom_start=12)

    # Adicionando marcadores ao mapa
    for index, location_info in df_aux.iterrows():
        popup_text = f"{location_info['City']} - {location_info['Road_traffic_density']}"
        folium.Marker(
            [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
            popup=popup_text
        ).add_to(map)

    # Exibindo o mapa no Streamlit
    folium_static(map, width=1024, height=600)

def order_share_by_week(df1):
    """ Está função mostra a quantidade de pedidos por entregador e por semana """
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig


def order_by_week(df1):
    """ Está função mostra a quantidade de pedidos por semana """
    # Quantidade de pedidos por Semana
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'])
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig
    

def traffic_order_city(df1):
    """ Está função mostra as entregas por cidade e tráfego"""
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size ='ID',color='City',hover_name='City')
    return fig


def traffic_order_share(df1):
    """ Está função mostra os pedidos por tráfego """
    columns = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    
    # gráfico
    fig =px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return fig

def order_metric(df1):  
    """ Está função mostra a quantidade de pedidos por dia """
        # Quantidade de pedidos por dia
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    
        # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    return fig

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

st.header('Marketplace - Visão Cliente')
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', ' Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric(df1)    
        st.markdown('# Pedidos por dia')
        st.plotly_chart(fig, use_container_width=True)


    #Colunas
    with st.container():
        coluna1, coluna2 = st.columns(2)
        
        with coluna1:
            fig = traffic_order_share(df1)
            st.markdown(' Pedidos por tráfego')
            st.plotly_chart(fig, use_container_width=True)
    
        with coluna2:
            fig = traffic_order_city(df1)
            st.markdown(' Pedidos por cidade e tráfego')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.markdown('# Pedidos por semana')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        fig = order_share_by_week(df1)
        st.header('Pedidos por entregador por semana')
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.header('Localização central de cada cidade por tipo de tráfego')
    country_maps(df1)
    

    
            
   















    


