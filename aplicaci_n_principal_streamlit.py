import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Coink - Evaluación Oink & Usuarios",
    page_icon="🐷",
    layout="wide"
)

st.title("🐷 Coink - Evaluación de Usuarios y Dispositivos Oink")
st.markdown("Plataforma interactiva para el análisis de depósitos, métricas de desempeño y arquitectura de datos.")

# Carga de Datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("depositos_oinks.csv")
        df['operation_date'] = pd.to_datetime(df['operation_date'])
        return df
    except Exception as e:
        st.error(f"Error al cargar 'depositos_oinks.csv': {e}")
        return None

df = load_data()

# NAVEGACIÓN EN PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "📊 a) Métrica & Dashboard de Usuarios", 
    "🗄️ b) Bases de Datos (SQL vs NoSQL)", 
    "🔄 c) Diagrama de Flujo (OINK)"
])

# ==========================================
# PESTAÑA A: MÉTRICA Y DASHBOARD
# ==========================================
with tab1:
    st.header("a) Evaluacion de Usuarios - Score Coink")
    st.markdown("""
    **Métrica Coink (RFM Adaptado):** 
    Evalúa a los usuarios asignando un puntaje de **0 a 100** derivado de tres variables:
    - **Monto Total Depositado (35%)**: Volumen total en COP ingresado a la alcancía.
    - **Frecuencia (35%)**: Número total de depósitos realizados.
    - **Recencia (30%)**: Días transcurridos desde su último depósito.
    """)

    if df is not None:
        # Procesamiento de métricas
        ref_date = df['operation_date'].max() + pd.Timedelta(days=1)

        user_agg = df.groupby('user_id').agg(
            total_amount=('operation_value', 'sum'),
            deposit_count=('operation_value', 'count'),
            last_deposit=('operation_date', 'max')
        ).reset_index()

        user_agg['recency_days'] = (ref_date - user_agg['last_deposit']).dt.days

        # Quintiles de 1 a 5
        user_agg['m_score'] = pd.qcut(user_agg['total_amount'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
        user_agg['f_score'] = pd.qcut(user_agg['deposit_count'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        user_agg['r_score'] = pd.qcut(user_agg['recency_days'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)

        # Cálculo del Score Final
        user_agg['score_coink'] = (user_agg['m_score'] * 7) + (user_agg['f_score'] * 7) + (user_agg['r_score'] * 6)

        def categorizar(score):
            if score >= 80: return "VIP / Champion"
            elif score >= 60: return "Usuario Leal"
            elif score >= 40: return "Usuario Ocasional"
            else: return "En Riesgo / Inactivo"

        user_agg['categoria'] = user_agg['score_coink'].apply(categorizar)

        # KPIs Principales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Usuarios Únicos", f"{len(user_agg):,}")
        col2.metric("Total Depósitos", f"{len(df):,}")
        col3.metric("Monto Total", f"${df['operation_value'].sum():,.0f} COP")
        col4.metric("Promedio Depósito", f"${df['operation_value'].mean():,.2f} COP")

        st.markdown("---")

        # Filtros de visualización
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cats_selected = st.multiselect("Filtrar por Categoría:", user_agg['categoria'].unique(), default=user_agg['categoria'].unique())
        
        filtered_users = user_agg[user_agg['categoria'].isin(cats_selected)]

        # Visualizaciones nativas de Streamlit
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Distribución de Usuarios por Criterio")
            cat_distribution = filtered_users['categoria'].value_counts()
            st.bar_chart(cat_distribution)

        with col_g2:
            st.subheader("Top Ubicaciones con Más Depósitos")
            top_locations = df['maplocation_name'].value_counts().head(5)
            st.bar_chart(top_locations)

        # Tabla Interactiva
        st.subheader("Tabla de Clasificación de Usuarios")
        search = st.text_input("Buscar usuario por ID:")
        
        disp_df = filtered_users[['user_id', 'total_amount', 'deposit_count', 'recency_days', 'score_coink', 'categoria']]
        if search:
            disp_df = disp_df[disp_df['user_id'].astype(str).str.contains(search)]

        st.dataframe(disp_df, use_container_width=True)

# ==========================================
# PESTAÑA B: BASES DE DATOS
# ==========================================
with tab2:
    st.header("b) Comparativa de Bases de Datos")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.subheader("Base de Datos Relacional (SQL)")
        st.markdown("""
        Organiza la información en tablas rígidas vinculadas por llaves (Primary/Foreign Keys). 
        Garantiza las propiedades **ACID** (Atomicidad, Consistencia, Aislamiento, Durabilidad).
        - **Ejemplos**: PostgreSQL, MySQL.
        """)

    with col_b2:
        st.subheader("Base de Datos No Relacional (NoSQL)")
        st.markdown("""
        Almacena datos sin esquema fijo (Documentos JSON, Clave-Valor, Grafos).
        Prioriza la escalabilidad horizontal y la flexibilidad sobre la consistencia estricta.
        - **Ejemplos**: MongoDB, Cassandra, Redis.
        """)

    st.markdown("---")
    st.subheader("💡 ¿Cuál es mejor para Coink y los Oinks?")
    st.info("""
    Para el **núcleo transaccional de Coink**, una **Base de Datos Relacional (SQL)** es la mejor opción.
    
    **Fundamentos:**
    1. **Integridad Financiera (ACID):** Manejar saldo y dinero real exige que las operaciones se completen por entero o se cancelen. No se permiten inconsistencias eventuales en un depósito.
    2. **Estructura Clara:** Las entidades (*Usuario*, *Transacción*, *Cuenta*, *Oink*) tienen atributos bien definidos con relaciones estructuradas ($1:N$).

    *Nota de Arquitectura Avanzada:* Se recomienda un modelo **híbrido** donde SQL maneje el saldo y depósitos, mientras que una NoSQL (Time-Series) registre logs masivos de telemetría e IoT de las máquinas Oink.
    """)

# ==========================================
# PESTAÑA C: DIAGRAMA DE FLUJO
# ==========================================
with tab3:
    st.header("c) Funcionamiento del Sistema OINK")
    
    st.subheader(" Flujo Completo: Desde la Moneda Físicas hasta la App Móvil y Retiros")
    
    st.markdown("### 1. Proceso de Depósito de Dinero")
    st.code("""
[ INICIO ]
   │
   ▼
1. Usuario se autentica en el Oink (vía QR o Nro. Documento)
   │
   ▼
2. Usuario ingresa monedas/billetes por la ranura
   │
   ▼
3. Sensores IoT del Oink leen y verifican la autenticidad
   │
   ▼
4. Pantalla del Oink confirma el monto y genera el recibo
   │
   ▼
5. Oink envía transacción HTTPS/MQTT cifrada al Backend Coink
   │
   ▼
6. Servidor ejecuta transacción SQL (Suma saldo + Registra evento)
   │
   ▼
7. Notificación Push actualiza la Billetera en la App Móvil
   │
[ FIN ]
    """, language="text")

    st.markdown("### 2. Proceso de Retiro de Dinero")
    st.code("""
[ INICIO ]
   │
   ▼
1. Usuario solicita el retiro desde la App Coink
   │
   ▼
2. Backend valida saldo disponible y genera token OTP dinámico
   │
   ▼
3. Usuario ingresa su documento y OTP en el Oink (o punto aliado)
   │
   ▼
4. Backend valida OTP y envía señal al dispensador del Oink
   │
   ▼
5. Oink entrega el dinero en efectivo
   │
   ▼
6. Backend descuenta el valor de la Billetera (Transacción SQL)
   │
[ FIN ]
    """, language="text")