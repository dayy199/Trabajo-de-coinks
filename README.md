# 🐷 Evaluación de Desempeño de Usuarios en Coink (Oinks)

Este repositorio contiene la solución desarrollada por el equipo de ciencia de datos e IoT para la definición y evaluación de la métrica de desempeño de los usuarios de **Coink** a partir de la base de depósitos en Oinks (`depositos_oink.csv`).

## 📊 Definición de la Métrica: Coink Score (RFM)

Para calificar a los usuarios de manera objetiva, construimos un puntaje denominado **Coink Score** adaptado del modelo tradicional de valor de cliente **RFM (Recency, Frequency, Monetary)**:

1. **Recency (Reciente - 30% peso):** Días transcurridos desde el último depósito realizado en un Oink. Premia la interacción constante.
2. **Frequency (Frecuencia - 35% peso):** Número total de transacciones de depósito realizadas. Premia la fidelidad.
3. **Monetary (Monto - 35% peso):** Suma total acumulada en pesos depositados. Premia la capacidad de ahorro.

El puntaje final se escala en un rango de **0 a 100 puntos** clasificando a los usuarios en 4 niveles:
- **Top Ahorrador ⭐** (Score ≥ 80)
- **Ahorrador Frecuente 👍** (60 ≤ Score < 80)
- **Ahorrador Ocasional 😐** (40 ≤ Score < 60)
- **Usuario Inactivo / En Riesgo 💤** (Score < 40)

## 📁 Estructura del Repositorio

```text
├── app.py               # Aplicación interactiva de Streamlit
├── depositos_oinks.csv   # Dataset con las operaciones de depósito
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Documentación general