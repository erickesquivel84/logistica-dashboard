import streamlit as st
import pandas as pd
import plotly.express as px
# Page configuration
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
# Parse date columns
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
    return str(row.get("STATUS", "SIN STATUS")).strip()

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
    sorted(df["RESULTADO"].dropna().unique())
)

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    [df["FECHA"].min().date(), df["FECHA"].max().date()]
)

# -------------------------
# Apply Filters
# -------------------------
filtered = df.copy()

if ejecutivos:
    filtered = filtered[filtered["EJECUTIVO"].isin(ejecutivos)]

if clientes:
    filtered = filtered[filtered["CLIENTE"].isin(clientes)]

if resultados:
    filtered = filtered[filtered["RESULTADO"].isin(resultados)]

filtered = filtered[
    (filtered["FECHA"] >= pd.to_datetime(fecha_inicio)) &
    (filtered["FECHA"] <= pd.to_datetime(fecha_fin))
]

# -------------------------
# KPIs
# -------------------------
total = len(filtered)
on_time = len(filtered[filtered["RESULTADO"] == "EN TIEMPO"])
late = len(filtered[filtered["RESULTADO"] == "DES TIEMPO"])

k1, k2, k3 = st.columns(3)
k1.metric("Total de Viajes", total)
k2.metric(
    "En Tiempo (%)",
    f"{(on_time / total * 100):.1f}%" if total else "0%"
)
k3.metric("Con Retraso", late)

# -------------------------
# Charts
# -------------------------
st.subheader("Análisis General")

c1, c2 = st.columns(2)

with c1:
    fig = px.pie(
        filtered,
        names="RESULTADO",
        title="En Tiempo vs Des Tiempo"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    viajes_ejecutivo = (
        filtered.groupby("EJECUTIVO")
        .size()
        .reset_index(name="VIAJES")
    )

    fig = px.bar(
        viajes_ejecutivo,
        x="EJECUTIVO",
        y="VIAJES",
        title="Viajes por Ejecutivo"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Retrasos por Cliente
# -------------------------
st.subheader("Retrasos por Cliente")

late_df = filtered[filtered["RESULTADO"] == "DES TIEMPO"]

if not late_df.empty:
    retrasos_cliente = (
        late_df.groupby("CLIENTE")
        .size()
        .reset_index(name="RETRASOS")
    )

    fig = px.bar(
        retrasos_cliente,
        x="CLIENTE",
        y="RETRASOS",
        color="CLIENTE"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay retrasos con los filtros actuales.")

# -------------------------
# Data Table
# -------------------------
st.subheader("Detalle de Viajes")
st.dataframe(filtered, use_container_width=True)

# -------------------------
# Download Button
# -------------------------
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Descargar CSV",
    csv,
    "logistica_filtrada.csv",
    "text/csv"
)
