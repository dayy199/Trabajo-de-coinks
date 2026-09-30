import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(
    page_title="Coink - Dashboard de Clasificación de Usuarios",
    page_icon="🐷",
    layout="wide"
)

st.title("🐷 Evaluación del Desempeño de Usuarios en Coink (Oinks)")
st.markdown("""
Esta aplicación evalúa y clasifica el desempeño de los usuarios de **Coink** analizando sus patrones de ahorro en los **Oinks**.
""")

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv("depositos_oinks.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    
    # Conversión de fechas
    df["operation_date"] = pd.to_datetime(df["operation_date"])
    df["user_createddate"] = pd.to_datetime(df["user_createddate"])
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo 'depositos_oinks.csv'. Asegúrate de que esté en el repositorio. Detalle: {e}")
    st.stop()

# --- DEFINICIÓN DE MÉTRICA (SCORE RFM DE AHORRO) ---
# Recency (Reciente): Días transcurridos desde el último depósito registrado en el dataset
max_date = df["operation_date"].max()

user_metrics = df.groupby("user_id").agg(
    total_deposited=("operation_value", "sum"),
    frequency=("operation_value", "count"),
    avg_deposit=("operation_value", "mean"),
    last_operation=("operation_date", "max"),
    user_created=("user_createddate", "min")
).reset_index()

user_metrics["recency_days"] = (max_date - user_metrics["last_operation"]).dt.days

# Cálculo de Score de 1 a 5 mediante quintiles
user_metrics["r_score"] = pd.qcut(user_metrics["recency_days"], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
user_metrics["f_score"] = pd.qcut(user_metrics["frequency"].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
user_metrics["m_score"] = pd.qcut(user_metrics["total_deposited"], 5, labels=[1, 2, 3, 4, 5])

# Coink Score Global (0 a 100)
user_metrics["coink_score"] = (
    user_metrics["r_score"].astype(int) * 0.3 +
    user_metrics["f_score"].astype(int) * 0.35 +
    user_metrics["m_score"].astype(int) * 0.35
) * 20

# Categorización del Usuario
def classify_user(score):
    if score >= 80:
        return "Top Ahorrador ⭐"
    elif score >= 60:
        return "Ahorrador Frecuente 👍"
    elif score >= 40:
        return "Ahorrador Ocasional 😐"
    else:
        return "Usuario Inactivo / En Riesgo 💤"

user_metrics["categoria"] = user_metrics["coink_score"].apply(classify_user)

# --- DASHBOARD EN STREAMLIT ---

# Sidebar: Filtros
st.sidebar.header("Filtros de Búsqueda")
categoria_filtro = st.sidebar.multiselect(
    "Selecciona Categorías de Usuario:",
    options=user_metrics["categoria"].unique(),
    default=user_metrics["categoria"].unique()
)

filtered_metrics = user_metrics[user_metrics["categoria"].isin(categoria_filtro)]

# Indicadores clave (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Usuarios Únicos", len(user_metrics))
col2.metric("Monto Total Depositado", f"${df['operation_value'].sum():,.0f}")
col3.metric("Promedio Depositado / Usuario", f"${user_metrics['total_deposited'].mean():,.0f}")
col4.metric("Coink Score Promedio", f"{user_metrics['coink_score'].mean():.1f} pts")

st.divider()

# Gráficas
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Distribución de Usuarios por Categoría")
    cat_counts = filtered_metrics["categoria"].value_counts()
    
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
    ax.bar(cat_counts.index, cat_counts.values, color=colors[:len(cat_counts)])
    plt.xticks(rotation=30, ha='right')
    ax.set_ylabel("Cantidad de Usuarios")
    ax.set_title("Categorías de Ahorro Coink")
    st.pyplot(fig)

with col_chart2:
    st.subheader("Frecuencia vs. Monto Total Depositado")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(filtered_metrics["frequency"], filtered_metrics["total_deposited"], c='#1f77b4', alpha=0.6)
    ax.set_xlabel("Número de Depósitos (Frecuencia)")
    ax.set_ylabel("Monto Total ($)")
    ax.set_title("Relación Frecuencia vs Monto")
    st.pyplot(fig)

st.divider()

# Tabla de Resultados
st.subheader("Detalle de Calificación por Usuario")
st.dataframe(
    filtered_metrics[[
        "user_id", "coink_score", "categoria", "total_deposited", "frequency", "recency_days"
    ]].sort_values(by="coink_score", ascending=False),
    use_container_width=True
)
