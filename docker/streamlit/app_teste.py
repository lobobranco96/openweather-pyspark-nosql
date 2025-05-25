import streamlit as st

# 1. Importar bibliotecas
try:
    from pymongo import MongoClient
    import pandas as pd
    from dotenv import load_dotenv
    import os
    import datetime
    st.write("✅ Bibliotecas importadas com sucesso")
except Exception as e:
    st.error(f"Erro ao importar bibliotecas: {e}")

# 2. Carregar variáveis do .env
try:
    load_dotenv()
    st.write("✅ Variáveis do .env carregadas")
except Exception as e:
    st.error(f"Erro ao carregar .env: {e}")

# 3. Pegar variável MONGO_URI
try:
    MONGO_URI = os.getenv("MONGO_URI")
    if MONGO_URI:
        st.write(f"✅ MONGO_URI encontrada: {MONGO_URI[:30]}...")  # mostra só parte por segurança
    else:
        st.error("❌ MONGO_URI não encontrada no .env")
except Exception as e:
    st.error(f"Erro ao pegar MONGO_URI: {e}")

# 4. Conectar no MongoDB
try:
    client = MongoClient(MONGO_URI)
    st.write("✅ Conexão MongoClient criada")
except Exception as e:
    st.error(f"Erro na conexão MongoClient: {e}")

# 5. Selecionar banco e coleção
try:
    db = client["clima"]
    collection = db["dados"]
    st.write("✅ Banco e coleção selecionados")
except Exception as e:
    st.error(f"Erro ao selecionar banco/coleção: {e}")

# 6. Buscar dados (exemplo: 5 documentos)
try:
    dados = list(collection.find().limit(5))
    if dados:
        st.write("✅ Dados carregados:")
        st.write(dados)
    else:
        st.warning("⚠️ Nenhum dado retornado da consulta")
except Exception as e:
    st.error(f"Erro ao buscar dados: {e}")

# 7. Converter para DataFrame e exibir
try:
    df = pd.DataFrame(dados)
    if not df.empty:
        df["_id"] = df["_id"].astype(str)
        st.write("✅ Dados convertidos para DataFrame:")
        st.dataframe(df)
    else:
        st.warning("⚠️ DataFrame vazio após conversão")
except Exception as e:
    st.error(f"Erro na conversão para DataFrame: {e}")

# 8. Converter coluna data_hora para datetime
try:
    if "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")
        st.write("✅ Coluna 'data_hora' convertida para datetime:")
        st.dataframe(df[["data_hora"]])
    else:
        st.warning("⚠️ Coluna 'data_hora' não encontrada no DataFrame")
except Exception as e:
    st.error(f"Erro na conversão da coluna data_hora: {e}")
