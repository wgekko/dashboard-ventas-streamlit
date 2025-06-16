import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import warnings
import io
warnings.simplefilter("ignore", category=FutureWarning)
# Suprimir advertencias ValueWarning
warnings.simplefilter("ignore")

st.set_page_config(page_title="Análisis Ventas Sankey", layout="wide", page_icon=":material/inactive_order:")
def apply_custom_style():
    css_file = "asset/styles.css"
    try:
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de estilo: {css_file}", icon=":material/cancel:")
apply_custom_style()

st.subheader("Análisis de Ventas con Diagramas Sankey")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_excel("datos/db-datos.xlsx", sheet_name="Hoja1")

df = cargar_datos()

st.markdown("### Vista previa de los datos")
st.dataframe(df.head())

# Paletas de colores para nodos
colores_paises = {pais: color for pais, color in zip(df["pais"].unique(), px.colors.qualitative.Pastel)}
colores_categoria = {cat: color for cat, color in zip(df["categoria"].unique(), px.colors.qualitative.Set2)}
colores_producto = {prod: color for prod, color in zip(df["producto"].unique(), px.colors.qualitative.Prism)}

st.divider()

# -----------------------------------------
# ANALISIS 1: País → Categoría
# -----------------------------------------
st.subheader("Análisis 1: País → Categoría")

col1, col2 = st.columns(2)
with col1:
    paises_seleccionados = st.multiselect("Seleccioná uno o más países", df["pais"].unique(), default=df["pais"].unique())
with col2:
    categorias_seleccionadas = st.multiselect("Filtrar por categorías", df["categoria"].unique(), default=df["categoria"].unique())

df1 = df[
    (df["pais"].isin(paises_seleccionados)) & 
    (df["categoria"].isin(categorias_seleccionadas))
]

df1_agg = df1.groupby(["pais", "categoria"])["total"].sum().reset_index()

nodos1 = list(pd.unique(df1_agg["pais"].tolist() + df1_agg["categoria"].tolist()))
mapa_indices1 = {nombre: i for i, nombre in enumerate(nodos1)}

df1_agg["source"] = df1_agg["pais"].map(mapa_indices1)
df1_agg["target"] = df1_agg["categoria"].map(mapa_indices1)
df1_agg["color"] = df1_agg["pais"].map(colores_paises).fillna("rgba(200,200,200,0.5)")

fig1 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos1,
        color="rgba(0,0,0,0.3)"
    ),
    link=dict(
        source=df1_agg["source"],
        target=df1_agg["target"],
        value=df1_agg["total"],
        color=df1_agg["color"],
        hovertemplate="%{source.label} → %{target.label}<br>Ventas: %{value:,.2f}"
    )
)])
fig1.update_layout(title_text="Flujo de Ventas: País → Categoría", height=500)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------------
# ANALISIS 2: Categoría → Producto
# -----------------------------------------
st.subheader("Análisis 2: Categoría → Producto")

col3, col4 = st.columns(2)
with col3:
    categorias2_sel = st.multiselect("Seleccioná una o más categorías", df["categoria"].unique(), default=df["categoria"].unique())
with col4:
    productos_sel = st.multiselect("Filtrar por productos", df["producto"].unique(), default=df["producto"].unique())

df2 = df[
    (df["categoria"].isin(categorias2_sel)) &
    (df["producto"].isin(productos_sel))
]

df2_agg = df2.groupby(["categoria", "producto"])["total"].sum().reset_index()

nodos2 = list(pd.unique(df2_agg["categoria"].tolist() + df2_agg["producto"].tolist()))
mapa_indices2 = {nombre: i for i, nombre in enumerate(nodos2)}

df2_agg["source"] = df2_agg["categoria"].map(mapa_indices2)
df2_agg["target"] = df2_agg["producto"].map(mapa_indices2)
df2_agg["color"] = df2_agg["categoria"].map(colores_categoria).fillna("rgba(150,150,150,0.5)")

fig2 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos2,
        color="rgba(0,0,0,0.3)"
    ),
    link=dict(
        source=df2_agg["source"],
        target=df2_agg["target"],
        value=df2_agg["total"],
        color=df2_agg["color"],
        hovertemplate="%{source.label} → %{target.label}<br>Ventas: %{value:,.2f}"
    )
)])
fig2.update_layout(title_text="Flujo de Ventas: Categoría → Producto", height=500)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------
# ANALISIS 3: Ciudad → Categoría → Ventas
# -----------------------------------------
st.subheader("Análisis 3: Ciudad → Categoría → Ventas")

# Agregación de datos
df3_agg = df.groupby(["ciudad", "categoria"])["total"].sum().reset_index()

# Generar nodos únicos
nodos3 = list(pd.unique(df3_agg["ciudad"].tolist() + df3_agg["categoria"].tolist()))
mapa_indices3 = {nombre: i for i, nombre in enumerate(nodos3)}

# Mapear ciudades y categorías a índices
df3_agg["source"] = df3_agg["ciudad"].map(mapa_indices3)
df3_agg["target"] = df3_agg["categoria"].map(mapa_indices3)
# Crear colores aleatorios para cada ciudad
import random
ciudades = df3_agg["ciudad"].unique()
colores_ciudades = {
    ciudad: f"rgba({random.randint(50,200)},{random.randint(50,200)},{random.randint(50,200)},0.7)"
    for ciudad in ciudades
}

# Mapear colores a cada flujo
df3_agg["color"] = df3_agg["ciudad"].map(colores_ciudades).fillna("rgba(180,180,180,0.5)")

# Crear Sankey
fig3 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos3,
        color="rgba(0,0,0,0.3)"
    ),
    link=dict(
        source=df3_agg["source"],
        target=df3_agg["target"],
        value=df3_agg["total"],
        color=df3_agg["color"]
    )
)])
fig3.update_layout(title_text="Flujo de Ventas: Ciudad → Categoría", height=500)
st.plotly_chart(fig3, use_container_width=True)

#st.subheader("Análisis 3: Ciudad → Categoría → Ventas")

#df3_agg = df.groupby(["ciudad", "categoria"])["total"].sum().reset_index()

#nodos3 = list(pd.unique(df3_agg["ciudad"].tolist() + df3_agg["categoria"].tolist()))
#mapa_indices3 = {nombre: i for i, nombre in enumerate(nodos3)}

#df3_agg["source"] = df3_agg["ciudad"].map(mapa_indices3)
#df3_agg["target"] = df3_agg["categoria"].map(mapa_indices3)
#df3_agg["color"] = df3_agg["ciudad"].map(colores_paises).fillna("rgba(180,180,180,0.5)")

#fig3 = go.Figure(data=[go.Sankey(
#    node=dict(
#        pad=15,
#        thickness=20,
#        line=dict(color="black", width=0.5),
#        label=nodos3,
#        color="rgba(0,0,0,0.3)"
#    ),
#    link=dict(
#        source=df3_agg["source"],
#        target=df3_agg["target"],
#        value=df3_agg["total"],
#        color=df3_agg["color"]
#    )
#)])
#fig3.update_layout(title_text="Flujo de Ventas: Ciudad → Categoría", height=500)
#st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------------
# ANALISIS 4: Mes → Producto → Utilidad
# -----------------------------------------
st.subheader("Análisis 4: Mes → Producto → Utilidad")

df4_agg = df.groupby(["mes", "producto"])["utilidad"].sum().reset_index()

df4_agg["mes"] = df4_agg["mes"].astype(str)  # Convertir a string para etiquetas

nodos4 = list(pd.unique(df4_agg["mes"].tolist() + df4_agg["producto"].tolist()))
mapa_indices4 = {nombre: i for i, nombre in enumerate(nodos4)}

df4_agg["source"] = df4_agg["mes"].map(mapa_indices4)
df4_agg["target"] = df4_agg["producto"].map(mapa_indices4)
df4_agg["color"] = df4_agg["mes"].map(lambda x: "rgba(100,150,255,0.5)")

fig4 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos4,
        color="rgba(0,0,0,0.3)"
    ),
    link=dict(
        source=df4_agg["source"],
        target=df4_agg["target"],
        value=df4_agg["utilidad"],
        color=df4_agg["color"]
    )
)])
fig4.update_layout(title_text="Flujo de Utilidad: Mes → Producto", height=500)
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------
# ANALISIS 5: País → Producto → Utilidad
# -----------------------------------------
st.subheader("Análisis 5: País → Producto → Utilidad")

df5_agg = df.groupby(["pais", "producto"])["utilidad"].sum().reset_index()

nodos5 = list(pd.unique(df5_agg["pais"].tolist() + df5_agg["producto"].tolist()))
mapa_indices5 = {nombre: i for i, nombre in enumerate(nodos5)}

df5_agg["source"] = df5_agg["pais"].map(mapa_indices5)
df5_agg["target"] = df5_agg["producto"].map(mapa_indices5)
df5_agg["color"] = df5_agg["pais"].map(colores_paises).fillna("rgba(180,180,180,0.5)")

fig5 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos5,
        color="rgba(0,0,0,0.3)"
    ),
    link=dict(
        source=df5_agg["source"],
        target=df5_agg["target"],
        value=df5_agg["utilidad"],
        color=df5_agg["color"]
    )
)])
fig5.update_layout(title_text="Flujo de Utilidad: País → Producto", height=500)
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------------
# ANALISIS 6: País → Categoría → Utilidad
# -----------------------------------------
st.subheader("Análisis 6: País → Categoría → Utilidad")

df6_agg = df.groupby(["pais", "categoria"])["utilidad"].sum().reset_index()

nodos6 = list(pd.unique(df6_agg["pais"].tolist() + df6_agg["categoria"].tolist()))
mapa_indices6 = {nombre: i for i, nombre in enumerate(nodos6)}

df6_agg["source"] = df6_agg["pais"].map(mapa_indices6)
df6_agg["target"] = df6_agg["categoria"].map(mapa_indices6)
df6_agg["color"] = df6_agg["pais"].map(colores_paises).fillna("rgba(150,150,150,0.5)")

fig6 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos6,
        color="rgba(0,0,0,0.3)"
    ),
    link=dict(
        source=df6_agg["source"],
        target=df6_agg["target"],
        value=df6_agg["utilidad"],
        color=df6_agg["color"]
    )
)])
fig6.update_layout(title_text="Flujo de Utilidad: País → Categoría", height=500)
st.plotly_chart(fig6, use_container_width=True)

#--------------------descargar los informes ----------------------    

col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=True)
with col1: 
    with st.container(border=True):
        st.markdown("**Descargar datos del análisis 1 (País → Categoría)**")
        excel1 = df1_agg[["pais", "categoria", "total"]]
        buffer1 = io.BytesIO()
        with pd.ExcelWriter(buffer1, engine='openpyxl') as writer:
            excel1.to_excel(writer, index=False, sheet_name="Pais_Categoria")
        buffer1.seek(0)

        st.download_button(
            label="Descargar Excel - País vs Categoría",
            data=buffer1,
            file_name="analisis_pais_categoria.xlsx",
            key="uno",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
with col2:    
    with st.container(border=True):
        st.markdown("**Descargar datos del análisis 2 (Categoría → Producto)**")
        excel2 = df2_agg[["categoria", "producto", "total"]]
        buffer2 = io.BytesIO()
        with pd.ExcelWriter(buffer2, engine='openpyxl') as writer:
            excel2.to_excel(writer, index=False, sheet_name="Categoria_Producto")
        buffer2.seek(0)

        st.download_button(
            label="Descargar Excel - Categoría vs Producto",
            data=buffer2,
            file_name="analisis_categoria_producto.xlsx",
            key="dos",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=True)
with col1:
    with st.container(border=True):
        st.markdown("**Descargar datos del análisis 3 (Ciudad → Categoría → Ventas)**")
        excel3 = df3_agg[["ciudad", "categoria", "total"]]
        buffer3 = io.BytesIO()
        with pd.ExcelWriter(buffer3, engine='openpyxl') as writer:
            excel3.to_excel(writer, index=False, sheet_name="Ciudad_Categoria")
        buffer3.seek(0)

        st.download_button(
            label="Descargar Excel - Ciudad vs Categoría",
            data=buffer3,
            file_name="analisis_ciudad_categoria.xlsx",
            key="tres",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
with col2:    
    with st.container(border=True):
        st.markdown("**Descargar datos del análisis 4 (Mes → Producto → Utilidad)**")
        excel4 = df4_agg[["mes", "producto", "utilidad"]]
        buffer4 = io.BytesIO()
        with pd.ExcelWriter(buffer4, engine='openpyxl') as writer:
            excel4.to_excel(writer, index=False, sheet_name="Mes_Producto")
        buffer4.seek(0)

        st.download_button(
            label="Descargar Excel - Mes vs Producto",
            data=buffer4,
            file_name="analisis_mes_producto_utilidad.xlsx",
            key="cuatro",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=True)
with col1:
    with st.container(border=True):
        st.markdown("**Descargar datos del análisis 5 (País → Producto → Utilidad)**")
        excel5 = df5_agg[["pais", "producto", "utilidad"]]
        buffer5 = io.BytesIO()
        with pd.ExcelWriter(buffer5, engine='openpyxl') as writer:
            excel5.to_excel(writer, index=False, sheet_name="Pais_Producto")
        buffer5.seek(0)

        st.download_button(
            label="Descargar Excel - País vs Producto",
            data=buffer5,
            file_name="analisis_pais_producto_utilidad.xlsx",
            key="cinco",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
with col2:
    with st.container(border=True):
        st.markdown("**Descargar datos del análisis 6 (País → Categoría → Utilidad)**")
        excel6 = df6_agg[["pais", "categoria", "utilidad"]]
        buffer6 = io.BytesIO()
        with pd.ExcelWriter(buffer6, engine='openpyxl') as writer:
            excel6.to_excel(writer, index=False, sheet_name="Pais_Categoria")
        buffer6.seek(0)

        st.download_button(
            label="Descargar Excel - País vs Categoría",
            data=buffer6,
            file_name="analisis_pais_categoria_utilidad.xlsx",
            key="seis",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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
    