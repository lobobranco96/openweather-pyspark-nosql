import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os
import plotly.express as px

# Carrega as variáveis do arquivo .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

@st.cache_data(ttl=300)
def carregar_dados():
    client = MongoClient(MONGO_URI)
    db = client["clima"]
    collection = db["dados"]
    dados = list(collection.find())
    df = pd.DataFrame(dados)
    if not df.empty:
        df["_id"] = df["_id"].astype(str)
        if "data_hora" in df.columns:
            df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")
        return df
    else:
        return pd.DataFrame()

def dashboard_temperatura_cidade(df, cidade):
    st.subheader(f"Temperatura ao longo do tempo em {cidade}")
    df_cidade = df[df["cidade"] == cidade].sort_values(by="data_hora")
    if df_cidade.empty:
        st.write("Sem dados para mostrar.")
        return
    fig = px.line(df_cidade, x="data_hora", y="temperatura",
                  title=f"Temperatura ao longo do tempo - {cidade}",
                  labels={"data_hora": "Data e Hora", "temperatura": "Temperatura (°C)"})
    st.plotly_chart(fig, use_container_width=True)

def dashboard_temperatura_geral(df):
    st.subheader("Temperatura ao longo do tempo - Todas as Cidades")
    if df.empty or "data_hora" not in df.columns or "temperatura" not in df.columns or "cidade" not in df.columns:
        st.write("Dados insuficientes para mostrar o gráfico geral.")
        return
    df = df.dropna(subset=["data_hora", "temperatura", "cidade"])
    df_sorted = df.sort_values(by="data_hora")
    fig = px.line(df_sorted, x="data_hora", y="temperatura", color="cidade",
                  title="Temperatura ao longo do tempo por cidade",
                  labels={"data_hora": "Data e Hora", "temperatura": "Temperatura (°C)", "cidade": "Cidade"})
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("Dashboard Weather MongoDB")

    df = carregar_dados()

    if df.empty:
        st.error("Nenhum dado encontrado no MongoDB.")
        return

    dashboard_opcoes = ["Temperatura - Cidade", "Temperatura - Todas as Cidades"]
    dashboard = st.selectbox("Escolha o dashboard:", dashboard_opcoes)

    if dashboard == "Temperatura - Cidade":
        cidades = df["cidade"].unique()
        cidade = st.selectbox("Escolha uma cidade:", cidades)

        st.subheader(f"Últimos 10 registros para {cidade}")
        df_cidade = df[df["cidade"] == cidade].sort_values(by="data_hora", ascending=False)
        st.dataframe(df_cidade.head(10))

        dashboard_temperatura_cidade(df, cidade)

    elif dashboard == "Temperatura - Todas as Cidades":
        dashboard_temperatura_geral(df)

    if st.button("Atualizar dados"):
        st.cache_data.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
