import os
from dotenv import load_dotenv
import streamlit as st
import pymongo
import pandas as pd
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Função para conectar ao MongoDB
def connect_mongo():
    client = pymongo.MongoClient(MONGO_URI) 
    db = client["clima"]  
    collection = db["dados"]  
    return collection

# Função para ler dados da coleção MongoDB
def get_data_from_mongo():
    collection = connect_mongo()
    data = collection.find()  # Recupera todos os documentos
    return pd.DataFrame(list(data))  # Converte para DataFrame do pandas

# Título do App
st.title("Visualização de Dados do MongoDB - Clima")

# Exibir uma descrição
st.markdown("""
    Este aplicativo exibe os dados de clima armazenados no MongoDB.
    Você pode visualizar informações como temperatura, umidade, etc.
""")

# Tente carregar e exibir os dados
try:
    # Carregar dados do MongoDB
    df = get_data_from_mongo()
    
    # Mostrar o DataFrame no Streamlit
    if not df.empty:
        st.write("Aqui estão os dados de clima:")
        st.dataframe(df)  # Exibe os dados como uma tabela interativa
    else:
        st.warning("Nenhum dado encontrado no MongoDB.")
except Exception as e:
    st.error(f"Ocorreu um erro ao tentar conectar ao MongoDB: {e}")

if not df.empty:
    st.subheader("Estatísticas")
    st.write(df.describe())  # Exibe estatísticas básicas do DataFrame

    st.subheader("Gráfico de Temperatura")
    st.line_chart(df["temperatura"])  # Gráfico simples de temperatura
