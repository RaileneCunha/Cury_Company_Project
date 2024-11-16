#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessarias
import pandas as pd
import numpy as np
import streamlit as st
import datetime
import pathlib
import os
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Visão Restaurante", page_icon="https://www.iconfinder.com/icons/7876099/french_fries_junk_food_potatoes_fast_restaurante_icon",layout="wide")

#---------------------------------------------------------------------------------------------
#Funções
#---------------------------------------------------------------------------------------------

def density_mean_std(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density'] ).agg({'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values = 'avg_time', color='std_time', color_continuous_scale='RdBu',
                     color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def distance_mean_city(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(
data=[go.Pie(
    labels=avg_distance['City'], 
    values=avg_distance['distance'], 
    pull=[0,0.1,0], 
    marker_colors=['#FF0000', '#00FF00', '#0000FF'])])
    
    return fig


def avg_stc_time_graph(df1):
    df_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_aux['City'],
                         y=df_aux['avg_time'],
                         error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig


def avg_std_time_delivery(df1,festival,op):
    """
        Está função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
        Input:
            df: Dataframe com os dados necessários para o cálculo
            op: tipo de operação que precisa ser calculado
                'avg_time': Calcula o tempo médio
                'std_time': Calcula o desvio padrão do tempo
        Output:
            df: Dataframe com 2 colunas e 1 linha
        
    """
    cols = ['Time_taken(min)', 'Festival']
    df_aux = df1.loc [:, cols].groupby('Festival').agg({'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)

    return df_aux



def distance(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = (df1.loc[:, cols].apply(lambda x: haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis = 1 ))
    
    avg_distance = np.round(df1['distance'].mean(),2)
    
    return avg_distance
    

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
st.header('Marketplace - Visão Restaurantes')
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
        st.title('Métricas Gerais')
        
        cl1,cl2,cl3,cl4,cl5,cl6 = st.columns(6)
        with cl1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique() )
            cl1.metric('Entregadores',delivery_unique)
            
        with cl2:
            avg_distance = distance(df1)
            cl2.metric('Distância média',avg_distance)
               
        with cl3:
            df_aux = avg_std_time_delivery(df1,'Yes','avg_time')
            cl3.metric('Tempo médio', df_aux)

        with cl4:
            df_aux = avg_std_time_delivery(df1,'Yes','std_time')
            cl4.metric('STD Entrega', df_aux)
            
        with cl5:
            df_aux = avg_std_time_delivery(df1,'No','avg_time')
            cl5.metric('Tempo médio', df_aux)
            
        with cl6:
            df_aux = avg_std_time_delivery(df1,'No','std_time')
            cl6.metric('STD Entrega', df_aux)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns (2)
        
        with col1:
            fig = avg_stc_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order'])['Time_taken(min)'].agg(['mean', 'std'])
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
                    

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')
        cl1,cl2, = st.columns(2)
        
        with cl1:
            fig = distance_mean_city(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with cl2:
            fig = density_mean_std(df1)
            st.plotly_chart(fig, use_container_width=True)
        
        





























