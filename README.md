# dashboard-ventas-streamlit
app con modelo de prediccion y analisis de ventas 
🛍️ Visualización y Predicción de Ventas para Tienda de Tecnología
Nivel básico (ideal para LinkedIn o introducción de README):
Desarrollamos una aplicación interactiva para visualizar y analizar las ventas de una tienda de productos tecnológicos. A través de gráficos claros y dinámicos, es posible observar la evolución de las ventas a lo largo del tiempo, identificar patrones de consumo y descubrir insights clave sobre el rendimiento de diferentes categorías de productos.
Además, incorporamos modelos de predicción que permiten anticipar tendencias futuras, apoyando la toma de decisiones estratégicas con base en datos.
Todo esto se presenta en una interfaz intuitiva, acompañada de herramientas visuales como gráficos Sankey, que ayudan a entender el flujo de productos y categorías dentro del negocio.
Este proyecto integra visualización de datos, modelado predictivo y análisis avanzado sobre un dataset de ventas en una tienda tecnológica. Las principales características son:
📈 Visualización de evolución temporal:
Se emplean gráficos de series temporales interactivos para observar el comportamiento histórico de las ventas por categoría, producto y canal.
🔍 Modelos de predicción multivariados:
Se utilizan distintos enfoques para estimar la evolución futura de las ventas:
TabPFN + XGBoost: un pipeline de clasificación/regresión que aprovecha el poder de TabPFN (un modelo Transformer entrenado para pocos datos tabulares) junto con XGBoost para mejorar la precisión.
N-BEATS: red neuronal orientada a series temporales, sin necesidad de estacionalidad explícita ni datos externos, capaz de capturar patrones complejos.
🔀 Gráficos Sankey:
Representan el flujo de ventas entre categorías, subcategorías y productos. Este tipo de visualización es clave para comprender cómo se distribuyen los ingresos y cómo se comportan los distintos segmentos del catálogo.
🧰 Tecnologías utilizadas:
Python (Pandas, Plotly, Sklearn, PyTorch)
Visualización con Dash / Streamlit (según implementación)
Modelado con TabPFN, XGBoost y N-BEATS (PyTorch Forecasting)
🚀 Objetivo
Proporcionar a equipos comerciales, de marketing y analítica una herramienta que no solo visualice lo que pasó, sino que también anticipe lo que viene, con modelos de última generación en predicción de series temporales.

