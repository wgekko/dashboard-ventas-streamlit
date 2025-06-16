import streamlit as st
import pandas as pd
from darts import TimeSeries
from darts.models import NBEATSModel
from darts.metrics import mae
import plotly.express as px
from darts.utils.utils import ModelMode
import plotly.graph_objects as go
from datetime import datetime
import logging
import warnings

logging.getLogger("darts").setLevel(logging.WARNING)
warnings.simplefilter("ignore", category=FutureWarning)
warnings.simplefilter("ignore")

st.set_page_config(page_title="Predicción Ventas N-BEATS", layout="wide" , page_icon=":material/two_pager_store:")

def apply_custom_style():
    css_file = "asset/styles.css"
    try:
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de estilo: {css_file}", icon=":material/cancel:")

apply_custom_style()

st.subheader("Predicción de ventas con modelo N-BEATS (Darts)")

@st.cache_data
def load_data():
    df = pd.read_excel("datos/db-datos.xlsx", parse_dates=["fecha"])
    df = df[['fecha', 'mes', 'pais', 'categoria', 'total']]
    df.dropna(subset=['fecha', 'total'], inplace=True)
    return df

df = load_data()

def crear_timeseries(df, time_col="ds", value_col="y", frecuencia_sugerida="D"):
    try:
        df = df.sort_values(by=time_col).copy()
        freq_inferida = pd.infer_freq(df[time_col])
        ts = TimeSeries.from_dataframe(
            df,
            time_col=time_col,
            value_cols=value_col,
            fill_missing_dates=True,
            freq=freq_inferida or frecuencia_sugerida
        )
        return ts
    except Exception as e:
        raise ValueError(f"Error al crear la TimeSeries: {e}")

st.sidebar.title("Selección de datos")
modo = st.sidebar.radio("Escenario de predicción:", ["Por País", "Por Categoría"])
grupo = st.sidebar.selectbox("Agrupar por:", ["fecha", "mes"])
horizonte = st.sidebar.selectbox("Horizonte de predicción:", [2, 3, 6])

# Crear columna 'periodo'
if grupo == "mes":
    df['periodo'] = pd.to_datetime(
        df['fecha'].dt.year.astype(str) + '-' +
        df['mes'].astype(str).str.zfill(2) + '-01'
    )
else:
    df['periodo'] = pd.to_datetime(df['fecha'])  # diario

col_agrupadora = "pais" if modo == "Por País" else "categoria"

df_grouped = (
    df.groupby([col_agrupadora, 'periodo'], as_index=False)['total']
    .sum()
    .rename(columns={col_agrupadora: 'unique_id', 'periodo': 'ds', 'total': 'y'})
)
df_grouped['y'] = df_grouped['y'].astype('float32')

if st.checkbox("Mostrar datos procesados"):
    st.dataframe(df_grouped.head())

entidad_sel = st.selectbox(f"Seleccionar {modo.lower()} para predecir", df_grouped["unique_id"].unique())
df_entidad = df_grouped[df_grouped["unique_id"] == entidad_sel].sort_values("ds")

st.subheader(f"Evolución histórica de total - {entidad_sel}")
fig_hist = px.line(df_entidad, x="ds", y="y", title="Histórico de Total", markers=True)
fig_hist.update_layout(xaxis_title="Fecha", yaxis_title="Total")
st.plotly_chart(fig_hist, use_container_width=True)

# Entrenar modelo
if st.button("Entrenar modelo y predecir", icon=":material/sync_arrow_up:", key="entrenar"):
    frecuencia = "MS" if grupo == "mes" else "D"
    try:
        ts = crear_timeseries(df_entidad, time_col="ds", value_col="y", frecuencia_sugerida=frecuencia)
    except Exception as e:
        st.error(f"Error creando la serie temporal: {e}")
        st.stop()

    modelo = NBEATSModel(
        input_chunk_length=30 if grupo == "fecha" else 12,
        output_chunk_length=horizonte,
        n_epochs=300,
        random_state=42,
    )
    with st.spinner("Entrenando modelo..."):
        modelo.fit(ts)

    pred = modelo.predict(horizonte)

    st.subheader("Predicción para próximos períodos")
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=ts.time_index, y=ts.values().flatten(), mode='lines+markers', name='Histórico'))
    fig_pred.add_trace(go.Scatter(x=pred.time_index, y=pred.values().flatten(), mode='lines+markers', name='Predicción'))
    fig_pred.update_layout(title="Predicción de Total", xaxis_title="Fecha", yaxis_title="Total")
    st.plotly_chart(fig_pred, use_container_width=True)

    df_pred = pd.DataFrame({
        "ds": pred.time_index,
        "predicción": pred.values().flatten()
    })
    st.download_button(
        label="Descargar predicción CSV",
        data=df_pred.to_csv(index=False).encode(),
        file_name=f"prediccion_{entidad_sel}.csv",
        mime="text/csv",
        key="download",
        icon=":material/download:"
    )

# Comparación múltiple
st.markdown("---")
st.subheader("Comparar múltiples entidades (opcional)")
comparar = st.checkbox("Activar comparación múltiple")

if comparar:
    entidades = st.multiselect(
        f"Seleccioná múltiples {modo.lower()}s para comparar",
        df_grouped["unique_id"].unique(),
        default=[entidad_sel],
    )

    if st.button("Generar comparación", key="analizar"):
        fig_comp = go.Figure()

        for entidad in entidades:
            df_e = df_grouped[df_grouped["unique_id"] == entidad].sort_values("ds")
            frecuencia = "MS" if grupo == "mes" else "D"

            try:
                ts_e = crear_timeseries(df_e, time_col="ds", value_col="y", frecuencia_sugerida=frecuencia)
            except Exception as e:
                st.error(f"Error con entidad {entidad}: {e}")
                continue

            modelo_e = NBEATSModel(
                input_chunk_length=30 if grupo == "fecha" else 12,
                output_chunk_length=horizonte,
                n_epochs=300,
                random_state=42,
            )
            with st.spinner(f"Entrenando modelo para {entidad}..."):
                modelo_e.fit(ts_e)
            pred_e = modelo_e.predict(horizonte)

            fig_comp.add_trace(go.Scatter(x=ts_e.time_index, y=ts_e.values().flatten(), mode="lines", name=f"{entidad} - Histórico"))
            fig_comp.add_trace(go.Scatter(x=pred_e.time_index, y=pred_e.values().flatten(), mode="lines+markers", name=f"{entidad} - Predicción"))

        fig_comp.update_layout(
            title="Comparación de predicción entre entidades",
            xaxis_title="Fecha",
            yaxis_title="Total"
        )
        st.plotly_chart(fig_comp, use_container_width=True)


# --------------- footer -----------------------------
st.write("---")
with st.container():
    #st.write("---")
    st.write("&copy; - derechos reservados -  2025 -  Walter Gómez - FullStack Developer - Data Science - Business Intelligence")
    #st.write("##")
    left, right = st.columns(2, gap='medium', vertical_alignment="bottom")
    with left:
        #st.write('##')
        st.link_button("Mi LinkedIn", "https://www.linkedin.com/in/walter-gomez-fullstack-developer-datascience-businessintelligence-finanzas-python/")  #,use_container_width=False
    with right: 
        #st.write('##') 
        st.link_button("Mi Porfolio", "https://walter-portfolio-animado.netlify.app/") # , use_container_width=False
    