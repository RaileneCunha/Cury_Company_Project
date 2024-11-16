import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="https://www.iconfinder.com/icons/4263514/ddos_protection_server_shield_icon",
    layout="wide"
)
    

#image_path = 'C:/Users/railene.silva/Documents/CURSO_CIENCIAS_DE_DADOS/Repos/ftc_programacao_python/Nuvem.jpg'
image = Image.open('Nuvem.jpg')
st.sidebar.image(image, width=1000)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Cury Company Growth Dashboard")

st.markdown(""" 
Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
### Como utilizar esse Growth Dashboard?
-  Visão Empresa:
    - Visão Gerencial: Métricas gerais de comportamento.
    - Visão Tática: Indicadores semanais de crescimento.
    - Visão Geográfica: Insights de geolocalização.   
- Visão Entregador:
    - Acompanhamento dos indicadores semanais de crescimento  
- Visão Restaurante:
- Indicadores semanais de crescimento dos restaurantes 
""")