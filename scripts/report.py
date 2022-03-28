from distutils.command.upload import upload
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import seaborn as sns
import datetime
from PIL import Image

st.title('Reporte Python Analytics')

path_shp = st.file_uploader("Choose a .shp zip:")

DATA_URL = ("https://github.com/"
            "Ashtin18/pythonAnalytics/blob/master/data/data.csv")

@st.cache
def load_data():
    data = pd.read_csv(DATA_URL, delimiter=";")
    return data

data_load_state = st.text("Loading data...")
data = load_data()
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Mostar Datos'):
    st.text('Datos Crudos')
    st.write(data)

st.set_option('deprecation.showPyplotGlobalUse', False)

#####################################################################################################

st.header("\nLimpieza de Datos:")

code='''
    #Búsqueda y eliminación de los datos nulos(NaN) en la columna ID
    df_main['ID'].isna().sum()
    df_main = df_main[df_main['ID'].notna()]
    df_main

# Eliminación de datos duplicados en la columna ID
    filtro_duplicados = df_main['ID'].duplicated(keep=False)
    df_main[filtro_duplicados]['ID'].value_counts().head()    
    '''

st.code(code, language='python')

st.text("Una vez realizada la limpieza de datos se contruyó la \nsiguiente matríz de correlación: ")


matriz_correlacion_var=["Days","NumberOfMeetingswithParents","Tuition","FRP.Take.up.percent.","SPR.Group.Revenue","MDR.High.Grade"]

corr_matrix = data[matriz_correlacion_var].corr()

plt.matshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)

plt.xticks(np.arange(corr_matrix.shape[0]), corr_matrix.columns, rotation=90)
plt.yticks(np.arange(corr_matrix.shape[0]), corr_matrix.columns)

plt.colorbar()

st.pyplot()





st.text("\n")
st.text("\n\nAnalizando la matriz anterior, podemos corroborar ciertas relaciones entre las \nvariables relevantes del presente estudio. A raiz de estas conjeturas se han\nlogrado plantear las siguientes preguntas exploratorias:")

st.text("\n")
st.header("\nPreguntas de Exploración:")


#####################################################################################################

st.subheader("¿Cúales son las regiones con mejor aceptación al servicio de STC?")
st.text("\nTratando los data, se logró calcular la siguiente tabla:\n")

gdf_states = gpd.read_file(path_shp)

conteo_x_state = data['Group.State'].value_counts()
conteo_x_state = conteo_x_state.reset_index()

st.dataframe(conteo_x_state)

st.text("\n")
st.text("\nFinalmente, se calculó un Mapa de Calor con los viajes registrados:")

gdf_conteo_x_state = pd.merge(left=gdf_states, right=conteo_x_state,
                                left_on="STATE_ABBR",right_on="index")

gdf_conteo_x_state.plot("Group.State", cmap='cool',
                       legend=True,figsize=(10, 5))


st.pyplot()


#####################################################################################################

st.subheader("¿Cúal es la relación del código de pobreza de la escuela con la retención para el año 2012?d")

code='''
# Calculamos el porcentaje de ID retenidos y no retenidos
(df_main['Retained.in.2012.'].value_counts(normalize=True)*100).rename({0:"No Retenido (%):",1:"Retenido (%):"})'''
st.code(code, language='python')
a=(data['Retained.in.2012.'].value_counts(normalize=True)*100).rename({0:"No Retenido (%):",1:"Retenido (%):"})
st.dataframe(a)

conteo_poberty_x_retained = (data[["Poverty.Code","Retained.in.2012."]]
                                .groupby(["Poverty.Code","Retained.in.2012."]).size()
                                .reset_index()
                                .rename({0:"conteo"},axis=1)
                            )


g = sns.catplot(
    data=conteo_poberty_x_retained, kind="bar",
    x="Poverty.Code", y="conteo", hue="Retained.in.2012.",
)
g.set_xticklabels()
st.pyplot()

st.text("A continuación comprobaremos, mediante chi cuadrado, la existencia de una\ndependencia entre ambas variables:\n\nEn primer lugar calculamos una tabla de contingencia, donde:")
st.text("0: Escuela No Retenida para el 2012\n1: Escuela Retenida para el 2012")
a= contingency_table = pd.crosstab(data['Poverty.Code'], data['Retained.in.2012.'])
st.dataframe(a)

st.text("Seguidamente, calculamos el valor p:")
code='''
from scipy.stats import chi2_contingency

stat, p, dof, expected = chi2_contingency(contingency_table)
print(f'stat={stat:.3f}, p={p:.7f}')
>>> stat=36.490, p=0.0000008'''
st.code(code, language='python')

st.text("Planteamos y verificamos nuestras varibles:")
code='''
if p > 0.05:
	print('Se acepta la H0. Las dos muestras son independientes.')
else:
	print('Se rechaza la H0. Existe dependencia entre las muestras.')
'''
st.code(code, language='python')
st.markdown("Se rechaza la H0. **Existe dependencia entre las muestras**.")

#####################################################################################################

st.subheader("¿Existe una relación entre el tipo de escuela y la retención para el año 2012?")

st.text("Elaboramos la siguiente tabla a modo de resumen, donde:")
st.text("0: Escuela No Retenida para el 2012\n1: Escuela Retenida para el 2012")
a=contingency_table = pd.crosstab(data['School.Type'], data['Retained.in.2012.'])
st.dataframe(a)

st.markdown("El porcentaje de retorno en escuelas CHD es: **62.65%**")
st.markdown("El porcentaje de retorno en escuelas Católicas es: **65.03%**")
st.markdown("El porcentaje de retorno en escuelas Públicas es: **59.02%**")
st.markdown("El porcentaje de retorno en escuelas Privadas no Cristianas es: **73.51%**")


# Gráfica.....

conteo_type_x_retained = (data[["School.Type","Retained.in.2012."]]
                                .groupby(["School.Type","Retained.in.2012."]).size()
                                .reset_index()
                                .rename({0:"conteo"},axis=1)
                            )

g = sns.catplot(
    data=conteo_type_x_retained, kind="bar",
    x="School.Type", y="conteo", hue="Retained.in.2012.",
)
g.set_xticklabels(rotation=90)

st.pyplot()

# ...

st.text("De igual manera, comprobaremos mediante chi cuadrado, la existencia de una\ndependencia entre ambas variables:")

st.text("Calculamos el valor p:")
code='''
stat, p, dof, expected = chi2_contingency(contingency_table)
print(f'stat={stat:.3f}, p={p:.7f}')
>>> stat=14.228, p=0.0026102
'''
st.code(code, language='python')

st.text("Planteamos y verificamos nuestras varibles:")
code='''
if p > 0.05:
	print('Se acepta la H0. Las dos muestras son independientes.')
else:
	print('Se rechaza la H0. Existe dependencia entre las muestras.')
'''
st.code(code, language='python')
st.markdown("Se rechaza la H0. **Existe dependencia entre las muestras**.")

#####################################################################################################

st.subheader("¿Qué meses del año presentan mayor número de viajes?")

st.text("Fechas con más viajes registrados: ")
st.text("7/06/2011\t131\n6/06/2011\t72\n14/06/201\t72\n14/06/2011\t72\n31/05/2011\t70\n1/06/2011\t70")

data["Departure.Date.Mod"] = pd.to_datetime(data["Departure.Date"], format='%d/%m/%Y').dt.month

data["Departure.Date.Mod"].value_counts().sort_index().plot()

plt.grid(True)

st.pyplot()