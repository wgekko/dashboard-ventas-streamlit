import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from xgboost import XGBRegressor
from tabpfn import TabPFNRegressor
from sklearn.metrics import mean_absolute_error
import warnings
warnings.simplefilter("ignore", category=FutureWarning)
# Suprimir advertencias ValueWarning
warnings.simplefilter("ignore")

st.set_page_config(page_title="Predicción Ventas con TabPFN-XGBoost", layout="wide" , page_icon=":material/monitoring:")

def apply_custom_style():
    css_file = "asset/styles.css"
    try:
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de estilo: {css_file}", icon=":material/cancel:")
apply_custom_style()

st.subheader("Predicción con TabPFN y XGBoost")
st.caption("Visualización interactiva de predicciones futuras")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("datos/db-datos.xlsx")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "pais", "categoria", "total"]]

df = cargar_datos()

# Sidebar
modo = st.sidebar.radio("Seleccioná el escenario", ["Por país", "Por categoría"])
horizonte = st.sidebar.selectbox("Horizonte de predicción (meses)", [2, 3, 6])
columna_filtro = "pais" if modo == "Por país" else "categoria"
opciones = df[columna_filtro].dropna().unique()
seleccion = st.sidebar.selectbox(f"Seleccioná un {columna_filtro}:", opciones)

# Comparación múltiple
comparar = st.sidebar.checkbox(f"Comparar múltiples con {columna_filtro}es", value=False)
opciones_comparar = []
if comparar:
    opciones_comparar = st.sidebar.multiselect(
        f"Seleccioná {columna_filtro}es adicionales:", 
        [x for x in opciones if x != seleccion]
    )

# Función de preparación
def preparar_datos(df, filtro, columna):
    df_filtrado = df[df[columna] == filtro]
    df_ag = (
        df_filtrado.groupby(pd.Grouper(key="fecha", freq="MS"))["total"]
        .sum()
        .reset_index()
        .rename(columns={"fecha": "Date", "total": "Value"})
        .set_index("Date")
        .sort_index()
    )
    df_ag["month"] = df_ag.index.month
    df_ag["run_idx"] = np.arange(len(df_ag)) / len(df_ag)
    return df_ag

# Entrenamiento y predicción
def entrenar_y_predecir(df_model, nombre, horiz):
    if len(df_model) < horiz + 4:
        st.warning(f"No hay suficientes datos para: {nombre}")
        return None
    
    train, test = df_model.iloc[:-horiz], df_model.iloc[-horiz:]
    X_tr, y_tr = train.drop(columns="Value"), train["Value"]
    X_te, y_te = test.drop(columns="Value"), test["Value"]

    # Modelos
    xgb = XGBRegressor()
    xgb.fit(X_tr, y_tr)
    y_xgb = xgb.predict(X_te)

    tab = TabPFNRegressor(device="cpu", ignore_pretraining_limits=True)
    tab.fit(X_tr.values, y_tr.values)
    y_tab = tab.predict(X_te.values, output_type="median")
    q10, q90 = tab.predict(X_te.values, output_type="quantiles", quantiles=[0.1, 0.9])

    return {
        "nombre": nombre,
        "index": df_model.index,
        "valores": df_model["Value"],
        "fechas_pred": y_te.index,
        "tab_median": y_tab,
        "tab_q10": q10,
        "tab_q90": q90,
        "xgb": y_xgb,
        "y_te": y_te
    }

# Gráfico con Plotly
def graficar_resultado(resultado):
    if resultado is None:
        return

    st.subheader(f"Predicción: {resultado['nombre']}")
    st.write(f"**MAE XGBoost**: {mean_absolute_error(resultado['y_te'], resultado['xgb']):.2f}")
    st.write(f"**MAE TabPFN**: {mean_absolute_error(resultado['y_te'], resultado['tab_median']):.2f}")

    fig = go.Figure()

    # Historial
    fig.add_trace(go.Scatter(
        x=resultado["index"], y=resultado["valores"], 
        mode="lines+markers", name="Histórico",
        line=dict(color="blue")
    ))

    # TabPFN
    fig.add_trace(go.Scatter(
        x=resultado["fechas_pred"], y=resultado["tab_median"],
        mode="lines+markers", name="TabPFN Mediana", line=dict(color="green")
    ))
    fig.add_trace(go.Scatter(
        x=resultado["fechas_pred"], y=resultado["tab_q10"],
        mode="lines", name="TabPFN Q10", line=dict(dash="dot", color="lightgreen"), showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=resultado["fechas_pred"], y=resultado["tab_q90"],
        mode="lines", name="TabPFN Q90", line=dict(dash="dot", color="lightgreen"),
        fill='tonexty', fillcolor='rgba(0,255,0,0.15)', showlegend=True
    ))

    # XGBoost
    fig.add_trace(go.Scatter(
        x=resultado["fechas_pred"], y=resultado["xgb"],
        mode="lines+markers", name="XGBoost", line=dict(color="orange", dash="dash")
    ))

    fig.update_layout(
        title=f"Predicción {horizonte} meses — {resultado['nombre']}",
        xaxis_title="Fecha",
        yaxis_title="Total",
        hovermode="x unified",
        legend=dict(x=0, y=1),
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

# Ejecutar
df_modelo = preparar_datos(df, seleccion, columna_filtro)
res_principal = entrenar_y_predecir(df_modelo, seleccion, horizonte)
graficar_resultado(res_principal)

# Comparaciones
if comparar and opciones_comparar:
    st.markdown("**Comparaciones adicionales**")
    for adicional in opciones_comparar:
        df_comp = preparar_datos(df, adicional, columna_filtro)
        resultado = entrenar_y_predecir(df_comp, adicional, horizonte)
        graficar_resultado(resultado)

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
    