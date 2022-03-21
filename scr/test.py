from calendar import month
import pandas as pd
import numpy as np
import math
import datetime
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas_profiling as ppr
# from scipy import stats
# from fitter import Fitter

# Función para redondear números
def round_up(n, decimals = 0):  
    multiplier = 10 ** decimals  
    return math.ceil(n * multiplier) / multiplier 


# Importacion de data
data=pd.read_csv("data/data.csv",delimiter=";")

df=pd.DataFrame(data,columns=["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"])

#Creación de las series "Quantity" y "UnitPrice" para trabajar
serie1 = pd.Series(df.iloc[:,3])
serie2 = pd.Series(df.iloc[:,5])

#Multiplicación de ambas series para hallar el ingreso total
acumulado= serie1 * serie2

#Inserción de la nueva columna en el DataFrame
new_df=df.assign(Acumulado=acumulado)

#Eliminación de las columnas "Quantity" y UnitPrice
new_df=new_df.drop(['Quantity','UnitPrice'], axis=1)

#Convertimos la columna InvoiceDate en formato date
new_df['InvoiceDate_dt'] = pd.to_datetime(new_df['InvoiceDate'], format='%m/%d/%Y %H:%M').dt.date

###################################################
# LIMPIEZA DE DATOS
# ELIMINACIÓN DE OUTLIERS:

# Primero encontramos los quartiles, el valor máximo y el valor minimo
Q1 = new_df["Acumulado"].quantile(0.25)
print("Primer Quartil: ",Q1)
Q3 = new_df["Acumulado"].quantile(0.75)
print("Tercer Quartil: ",Q3)
IQR= Q3-Q1
print("Rango Intercuartil: ",IQR)
Mediana= new_df["Acumulado"].median()
print("Mediana", Mediana)
Valor_Minimo = new_df["Acumulado"].min()
print("Valor Mínimo: ",Valor_Minimo)
Valor_Maximo = new_df["Acumulado"].max()
print("Valor Maximo: ",Valor_Maximo)

# Calculamos el bigote inferior y superior
BI_calculado = 0
print("BI_calculado \n"+"0")

BS_calculado = (Q3 + 1.5 * IQR)
print("BS_calculado \n",BS_calculado)

# Ubicamos los outliers
ubicacion_outliers = (new_df["Acumulado"] < BI_calculado) | (new_df["Acumulado"] > BS_calculado)
print("\nUbicación de Outliers \n",ubicacion_outliers)

# Listamos los outliers
outliers = new_df[ubicacion_outliers]
print("\nLista de Outliers \n",outliers)

# Ordenamos los Outliers
Outliers_Ordenados = outliers.sort_values("Acumulado")
print(Outliers_Ordenados)

# Ubicamos los datos que cumplen la condición
ubicacion_no_outliers = (new_df["Acumulado"] >= BI_calculado ) & ( new_df["Acumulado"] <= BS_calculado )
df_main = new_df[ubicacion_no_outliers]
print(df_main)

###################################################

#Creación de Cuadro Resumen de Fecha x IngresoTotal
matriz_resumen =  df_main.groupby(by="InvoiceDate_dt")["Acumulado"].sum()
print(matriz_resumen)

###################################################
# Resumen de países con mas compras
filtro_duplicados = df_main["Country"].duplicated(keep=False)
paises=df_main[filtro_duplicados]['Country'].value_counts().head()
paises.plot(kind='bar')
plt.show()

###################################################
# Creación de la Matriz de Correlación
matriz_correlacion_var=["Acumulado","InvoiceDate_dt","CustomerID",]

corr_matrix = df_main[matriz_correlacion_var].corr(method="pearson")
print(corr_matrix)

plt.rcParams['axes.grid'] = False
plt.matshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
plt.xticks(np.arange(corr_matrix.shape[0]), corr_matrix.columns, rotation=90)
plt.yticks(np.arange(corr_matrix.shape[0]), corr_matrix.columns)

# Creación del reporte
# profile = ppr.ProfileReport(df_main, title='Pandas Profiling Report', minimal=True)
# profile.to_file('data/Reporte.html')

###################################################################
# Preguntas de Exploración: 
# ¿Cual es el promedio de compra por ticket?
# ¿Que pais compra mas?
# ¿Dia con mas ventas?
# ¿Producto mas vendido?

print("\nDATAFRAME: \n")
print(df_main)

ticket_mean=(df_main["Acumulado"].sum())/len(df_main["InvoiceNo"])
print(round_up(ticket_mean,2))
ticket_mean = round_up(ticket_mean,2)

print(f"El gasto de compra promedio por ticket es de €/{ticket_mean}")
