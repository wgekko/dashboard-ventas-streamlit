import streamlit as st
import pandas as pd
import plotly.express as px
import io
from fpdf import FPDF
import plotly.io as pio
from PIL import Image


st.set_page_config(
    page_title="Dashboard Analsis Ventas", 
    page_icon=":material/finance_mode:", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

def apply_custom_style():
    css_file = "asset/styles.css"
    try:
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de estilo: {css_file}", icon=":material/cancel:")
apply_custom_style()


dfDatos = pd.read_excel("datos/db-datos.xlsx")

with st.sidebar:
    parAno=st.selectbox('Año',options=dfDatos['anio'].unique(),index=0)    

    parMes = st.selectbox('Mes',options=dfDatos['mes'].unique(),index=0)    

    parPais = st.multiselect('País',options=dfDatos['pais'].unique())

if parAno:   
    dfDatos=dfDatos[dfDatos['anio']==parAno]

if parMes:    
    dfDatos=dfDatos[dfDatos['mes']<=parMes]

if len(parPais)>0:
    dfDatos=dfDatos[dfDatos['pais'].isin(parPais)]


dfMesActual = dfDatos[dfDatos['mes']==parMes]

if parMes: 
    if parMes>1:         
        dfMesAnterior = dfDatos[dfDatos['mes']==parMes-1]
    else: 
        dfMesAnterior = dfDatos[dfDatos['mes']==parMes]

st.header('Tienda de Productos Tecnológicos')
st.subheader('Dashboard de Análisis de ventas')

if not parPais:
    st.subheader('País seleccionado : Todos')
else:
    paises_str = ', '.join(parPais)
    st.subheader(f'País seleccionado : {paises_str}')

#if parPais == []:    
#    st.subheader(f'País seleccionado : Todos ')
#else:
#    st.subheader(f'País seleccionado : {parPais} ')    

c1,c2,c3,c4,c5 = st.columns(5)

with c1:    
    productosAct= dfMesActual['cantidad'].sum()    
    productosAnt= dfMesAnterior['cantidad'].sum()    
    variacion=productosAnt-productosAct 
    st.metric(f"Productos vendidos",f'{productosAct:,.0f} unidades', f'{variacion:,.0f}')

with c2:    
    ordenesAct= dfMesActual['orden'].count()    
    ordenesAnt= dfMesAnterior['orden'].count()    
    variacion=ordenesAct-ordenesAnt
    st.metric(f"Ventas realizadas",f'{ordenesAct:.0f}', f'{variacion:.1f}')

with c3:    
    ventasAct= dfMesActual['total'].sum()    
    ventasAnt= dfMesAnterior['total'].sum()   
    variacion=ventasAct-ventasAnt
    st.metric(f"Ventas totales",f'$ {ventasAct:,.0f}', f'{variacion:,.0f}')

with c4:    
    utilidadAct= dfMesActual['utilidad'].sum()    
    utilidadAnt= dfMesAnterior['utilidad'].sum()    
    variacion=utilidadAct-utilidadAnt
    st.metric(f"Utilidades",f'$ {utilidadAct:,.0f}', f'{variacion:,.0f}')

with c5:    
    utilPercentAct= (utilidadAct/ventasAct)*100 if ventasAct != 0 else 0     
    utilPercentAnt= (utilidadAnt/ventasAnt)*100 if ventasAnt != 0 else 0 
    variacion=utilPercentAnt-utilPercentAct 
    st.metric(f"Utilidad porcentual",f'{utilPercentAct:,.2f} %.', f'{variacion:,.0f} %')

c1,c2 = st.columns([0.6,0.4]) 

with c1:
    dfVentasMes = dfDatos.groupby('mes').agg({'total':'sum'}).reset_index()
    fig1 = px.line(dfVentasMes,x='mes',y='total', title='Ventas por mes',color_discrete_sequence=px.colors.qualitative.Plotly)    
    st.plotly_chart(fig1,use_container_width=True)

with c2:
    dfVentasPais = dfMesActual.groupby('pais').agg({'total':'sum'}).reset_index().sort_values(by='total',ascending=False)
    fig2 = px.bar(dfVentasPais,x='pais',y='total', title=f'Ventas por País Mes: {parMes}', color='pais',text_auto=',.0f', color_discrete_sequence=px.colors.qualitative.Plotly)
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2,use_container_width=True)

c1,c2 = st.columns([0.6,0.4])

with c1:
    dfVentasCategoria = dfDatos.groupby(['mes','categoria']).agg({'total':'sum'}).reset_index()
    fig3 = px.line(dfVentasCategoria,x='mes',y='total', title='Ventas por mes y categoría',color='categoria',color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig3,use_container_width=True)

with c2:
    dfVentasCategoria = dfMesActual.groupby('categoria').agg({'total':'sum'}).reset_index().sort_values(by='total',ascending=False)
    fig4 = px.bar(dfVentasCategoria,x='categoria',y='total', title=f'Ventas por categoría Mes: {parMes}', color='categoria',text_auto=',.0f',color_discrete_sequence=px.colors.qualitative.Plotly)
    fig4.update_layout(showlegend=False) 
    st.plotly_chart(fig4,use_container_width=True)

#------------------ generar los archivos para descargar el informe en pdf ----------------
# Función auxiliar para guardar figuras Plotly como imágenes en memoria
def fig_to_image(fig):
    img_bytes = fig.to_image(format="png")
    return Image.open(io.BytesIO(img_bytes))

# Función para generar PDF
def generar_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte de Ventas", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Año: {parAno}  -  Mes: {parMes}", ln=True)
    pdf.cell(0, 10, f"Países: {'Todos' if not parPais else ', '.join(parPais)}", ln=True)
    pdf.ln(10)

    # Agregar los gráficos como imágenes
    figs = [fig1, fig2, fig3, fig4]
    for fig in figs:
        img = fig_to_image(fig)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()

        # Guardar temporalmente imagen
        img_path = "temp_chart.png"
        with open(img_path, "wb") as f:
            f.write(img_bytes)

        pdf.image(img_path, w=180)
        pdf.ln(10)

    # Agregar tabla con datos resumidos (mes actual)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resumen de ventas del mes actual", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.ln(5)

    resumen = dfMesActual.groupby(['pais', 'categoria']).agg({
        'cantidad': 'sum',
        'total': 'sum',
        'utilidad': 'sum'
    }).reset_index()

    for _, row in resumen.iterrows():
        texto = f"{row['pais']} - {row['categoria']} | Cantidad: {row['cantidad']} | Total: ${row['total']:.2f} | Utilidad: ${row['utilidad']:.2f}"
        pdf.cell(0, 8, texto, ln=True)

    # Retornar archivo PDF como bytes
    output = io.BytesIO()
    pdf.output(output)
    return output
# Botón de descarga
st.write("---")
with st.container(border=True):
    if st.button("Descargar reporte en PDF" ,icon=":material/picture_as_pdf:", key="download"):
        pdf_file = generar_pdf()
        st.download_button(
            label="Descargar PDF",
            data=pdf_file.getvalue(),
            file_name="reporte_ventas.pdf",               
            mime="application/pdf"
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
    