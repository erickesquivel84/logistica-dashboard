import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Logística",
    layout="wide"
)

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("logistica.csv")
    df.columns = df.columns.str.strip().str.upper()
    return df

df = load_data()

# -------------------------
# Date Parsing
# -------------------------
date_cols = ["FECHA", "DESPACHO", "CITA ENTREGA"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# -------------------------
# Normalize Status
# -------------------------
def resultado(row):
    if str(row.get("EN TIEMPO")).strip() == "✔️":
        return "EN TIEMPO"
    if str(row.get("DES TIEMPO")).strip() == "✔️":
        return "DES TIEMPO"
    return row.get("STATUS", "SIN STATUS")

df["RESULTADO"] = df.apply(resultado, axis=1)

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filtros")

ejecutivos = st.sidebar.multiselect(
    "Ejecutivo",
    sorted(df["EJECUTIVO"].dropna().unique())
)

clientes = st.sidebar.multiselect(
    "Cliente",
    sorted(df["CLIENTE"].dropna().unique())
)

resultados = st.sidebar.multiselect(
    "Resultado",
    df["RESULTADO"].unique()
)

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    [df["FECHA"].min(), df["FECHA"].max()]
)

# -------------------------
# Apply Filters
# -------------------------
filtered = df.copy()

if ejecutivos:
    filtered = filtered[f]()
