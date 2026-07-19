import datetime
from datetime import timedelta, date, datetime
from typing import Tuple, Any

import holidays
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
from pandas import DataFrame

#Aqui va el codigo para transformar las tablas de la base de datos en las dimensiones y hechos que pusimos

def transform_fecha(rango_fecha: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Transforma el rango de fechas en la estructura exacta solicitada para el Data Mart.
    Atributos: cod_Fecha, año, mes, dia, nombre_Dia
    """
    df_fecha = pd.DataFrame()
    
    # 1. Generar la Clave Inteligente AAAAMMDD (Garantiza consistencia absoluta en las cargas)
    df_fecha["cod_Fecha"] = rango_fecha.strftime("%Y%m%d").astype(int)
    
    # 2. Atributos requeridos por tu diseño
    df_fecha["año"] = rango_fecha.year
    df_fecha["mes"] = rango_fecha.month
    df_fecha["dia"] = rango_fecha.day
    
    # 3. Nombre del día en español
    dias_espanol = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    df_fecha["nombre_Dia"] = rango_fecha.day_name().map(dias_espanol)
    
    # 4. Columna de auditoría y ordenamiento estricto
    df_fecha["saved"] = pd.Timestamp.now().date()
    df_fecha = df_fecha[["cod_Fecha", "año", "mes", "dia", "nombre_Dia", "saved"]]
    
    return df_fecha


def transform_hora(rango_tiempo: pd.DatetimeIndex) -> DataFrame:
    """Transforma el rango de tiempo en la estructura exacta solicitada."""
    # Corrección: Inicializamos el DataFrame directamente con un diccionario para evitar warnings
    df_transformado = pd.DataFrame({
        "hora": rango_tiempo.hour,
        "minuto": rango_tiempo.minute
    })
    
    # Generación de la Clave Subrogada consecutiva (1 a 1440)
    df_transformado["cod_Hora"] = range(1, len(df_transformado) + 1)
    
    # Reordenamiento estricto de columnas
    df_transformado = df_transformado[["cod_Hora", "hora", "minuto"]]
    return df_transformado

def transform_sede(dim_sede: DataFrame) -> DataFrame:
    """
    Parametros: dim_sede.
    Se conservan las columnas requeridas para la dimensión (sede_id, nombre, cliente_id) y se renombran.
    """
    dim_sede.drop(columns=dim_sede.columns.difference(["sede_id", "nombre", "cliente_id"]), inplace=True)
    dim_sede.replace({' ': 'No aplica', '':'No_aplica'}, inplace=True)
    dim_sede.rename(columns={"sede_id": "key_dim_sede", "nombre": "nombre_sede", "cliente_id": "cliente_id_sede"}, inplace=True)
    dim_sede.sort_values(by=["key_dim_sede"], inplace=True)
    dim_sede["saved"] = date.today()
    return dim_sede

def transform_mensajero(dim_mensajero: DataFrame, tabla_usuario: DataFrame) -> DataFrame:
    """
    Parametros: dim_mensajero y tabla_usuario. 
    Solo se necesita tabla_usuario para extraer el username al que corresponde la "user_id" de cada mensajero.
    """
    dim_mensajero = dim_mensajero.join(tabla_usuario.set_index("id"), on="user_id")
    dim_mensajero.drop(columns=dim_mensajero.columns.difference(["id", "username"]), inplace=True)
    dim_mensajero.replace({np.nan: 'No aplica', ' ': 'No aplica', '': 'No_aplica'}, inplace=True)
    dim_mensajero.rename(columns={"id": "key_dim_mensajero", "username": "username_mensajero"}, inplace=True)
    dim_mensajero.sort_values(by=["key_dim_mensajero"], inplace=True)
    dim_mensajero["saved"] = date.today()
    return dim_mensajero


def transform_cliente(dim_cliente: DataFrame) -> DataFrame:
    """    
    Parametros: dim_cliente.
    """
    dim_cliente.drop(columns=['nit_cliente', 'email', 'direccion', 'telefono', 'nombre_contacto', 'ciudad_id', 'tipo_cliente_id', 'activo', 'coordinador_id', 'sector'], inplace=True)    
    dim_cliente.rename(columns={"cliente_id": "key_dim_cliente", "nombre": "nombre_cliente"}, inplace=True)
    dim_cliente.sort_values(by=["key_dim_cliente"], inplace=True)
    dim_cliente["saved"] = date.today()
    
    return dim_cliente


def transform_novedad(dim_novedad: DataFrame) -> DataFrame:
    """
    Parametros: dim_novedad.
    """
    dim_novedad.rename(columns={"id": "key_dim_novedad", "nombre": "tipo_novedad"}, inplace=True)
    dim_novedad.sort_values(by=["key_dim_novedad"], inplace=True)
    dim_novedad["saved"] = date.today()

    return dim_novedad


def transform_fact_novedades(df_nov: DataFrame, df_ser: DataFrame, ready_hora: DataFrame) -> DataFrame:
    """
    Transforma la tabla de hechos de novedades conectando el negocio con el tiempo.
    Atributos: cod_Fecha, cod_Hora, cod_Sede, cod_Novedad, cod_Cliente, cod_Mensajero, ID_Entrega, descripcion_adicional
    """

    df_hechos = pd.merge(df_nov, df_ser, left_on="servicio_id", right_on="id", how="inner")
    
    df_hechos["fecha_novedad"] = pd.to_datetime(df_hechos["fecha_novedad"])
    
    df_hechos["cod_Fecha"] = df_hechos["fecha_novedad"].dt.strftime("%Y%m%d").astype(int)
    
    df_hechos["puente_hora"] = df_hechos["fecha_novedad"].dt.hour
    df_hechos["puente_minuto"] = df_hechos["fecha_novedad"].dt.minute
    
    df_hechos = pd.merge(
        df_hechos,
        ready_hora[["cod_Hora", "hora", "minuto"]],
        left_on=["puente_hora", "puente_minuto"],
        right_on=["hora", "minuto"],
        how="left"
    )
    
    # 5. Renombrar las columnas físicas del origen a la estructura formal de nuestro Data Mart
    df_hechos.rename(columns={
        "origen_id": "cod_Sede",             # El origen mapea la ubicación física/sede
        "tipo_novedad_id": "cod_Novedad",
        "cliente_id": "cod_Cliente",
        "mensajero_id_x": "cod_Mensajero",   # Usamos el mensajero específico que reportó la novedad (tabla novedades)
        "servicio_id": "ID_Entrega",
        "descripcion_x": "descripcion_adicional" # La descripción de la novedad en sí
    }, inplace=True)
    
    # 6. Selección y ordenamiento estricto de las columnas exigidas
    columnas_finales = [
        "cod_Fecha", "cod_Hora", "cod_Sede", "cod_Novedad", 
        "cod_Cliente", "cod_Mensajero", "ID_Entrega", "descripcion_adicional"
    ]
    df_hechos = df_hechos[columnas_finales]
    
    # Rellenar textos vacíos para evitar fallos de strings y añadir auditoría
    df_hechos["descripcion_adicional"].fillna("Sin descripción", inplace=True)
    df_hechos["saved"] = date.today()
    
    return df_hechos

# Estados del OLTP -> sufijo del datamart Entregas.
# El estado 3 ("Con novedad") NO va aquí, ese pertenece al hecho de Novedades.
ESTADOS_ENTREGA = {
    1: "Iniciado",
    2: "Asignado",
    4: "Recogido",
    5: "Entregado",
    6: "Cerrado",
}


def _estado_a_columnas(raw_estado_servicio, estado_id, sufijo, dim_fecha, dim_hora):
    """
    Para UN estado, devuelve una fila por servicio con:
        servicio_id | ts_<sufijo> | cod_Fecha_<sufijo> | cod_Hora_<sufijo>
    El ts es el datetime real (para luego restar los tiempos).
    cod_Fecha y cod_Hora salen de cruzar contra las dimensiones.
    """
    sub = raw_estado_servicio[raw_estado_servicio["estado_id"] == estado_id].copy()

    # Unimos fecha (date) + hora (time) en un solo datetime robusto
    sub["ts"] = pd.to_datetime(
        sub["fecha"].astype(str) + " " + sub["hora"].astype(str),
        errors="coerce"
    )

    # Si un servicio tocó el estado más de una vez, nos quedamos con la primera vez
    sub = sub.sort_values("ts").drop_duplicates(subset="servicio_id", keep="first")

    # Descomponemos para poder buscar en las dimensiones
    sub["año"]    = sub["ts"].dt.year
    sub["mes"]    = sub["ts"].dt.month
    sub["dia"]    = sub["ts"].dt.day
    sub["hora"]   = sub["ts"].dt.hour
    sub["minuto"] = sub["ts"].dt.minute

    # cod_Fecha: se busca en dim_fecha por año/mes/dia
    sub = sub.merge(dim_fecha[["cod_Fecha", "año", "mes", "dia"]],
                    on=["año", "mes", "dia"], how="left")
    # cod_Hora: se busca en dim_hora por hora/minuto
    sub = sub.merge(dim_hora[["cod_Hora", "hora", "minuto"]],
                    on=["hora", "minuto"], how="left")

    sub = sub.rename(columns={
        "ts":        f"ts_{sufijo}",
        "cod_Fecha": f"cod_Fecha_{sufijo}",
        "cod_Hora":  f"cod_Hora_{sufijo}",
    })
    return sub[["servicio_id", f"ts_{sufijo}",
                f"cod_Fecha_{sufijo}", f"cod_Hora_{sufijo}"]]

def transform_fact_entregas(raw_estado_servicio, raw_servicio,
                            raw_usuarioaquitoy, dim_fecha, dim_hora):
    """
    Hecho Entregas. Grano: un servicio = una entrega.
    """
    # 1) Grano y FK directos que salen de mensajeria_servicio
    df_entregas = raw_servicio.rename(columns={
        "id": "ID_entrega",
        "cliente_id": "cod_Cliente",
        "mensajero_id": "cod_Mensajero",
    })[["ID_entrega", "cod_Cliente", "cod_Mensajero"]].copy()

    # 2) Sede: se une por el MISMO id. servicio.id == usuarioaquitoy.id
    #    -> la sede del servicio 7 es la sede_id del registro id=7 en usuarioaquitoy.
    df_entregas = df_entregas.merge(
        raw_usuarioaquitoy.rename(columns={"sede_id": "cod_Sede"})[["id", "cod_Sede"]],
        left_on="ID_entrega", right_on="id", how="left"
    ).drop(columns=["id"])

    # 3) Por cada estado, traer fecha/hora (y el ts para los tiempos)
    for estado_id, sufijo in ESTADOS_ENTREGA.items():
        cols = _estado_a_columnas(raw_estado_servicio, estado_id, sufijo,
                                  dim_fecha, dim_hora)
        df_entregas = df_entregas.merge(cols, left_on="ID_entrega", right_on="servicio_id", how="left")
        df_entregas = df_entregas.drop(columns=["servicio_id"])

    # 4) Tiempos por fase (en minutos), restando los ts
    df_entregas["tiempo_Estado_Iniciado"]  = (df_entregas["ts_Asignado"]  - df_entregas["ts_Iniciado"]).dt.total_seconds() / 60
    df_entregas["tiempo_Estado_Asignado"]  = (df_entregas["ts_Recogido"]  - df_entregas["ts_Asignado"]).dt.total_seconds() / 60
    df_entregas["tiempo_Estado_Recogido"]  = (df_entregas["ts_Entregado"] - df_entregas["ts_Recogido"]).dt.total_seconds() / 60
    df_entregas["tiempo_Estado_Entregado"] = (df_entregas["ts_Cerrado"]   - df_entregas["ts_Entregado"]).dt.total_seconds() / 60

    # 5) Selección y orden final (igual a tu diagrama)
    columnas_finales = [
        "ID_entrega",
        "cod_Fecha_Iniciado",  "cod_Hora_Iniciado",
        "cod_Fecha_Asignado",  "cod_Hora_Asignado",
        "cod_Fecha_Recogido",  "cod_Hora_Recogido",
        "cod_Fecha_Entregado", "cod_Hora_Entregado",
        "cod_Fecha_Cerrado",   "cod_Hora_Cerrado",
        "cod_Cliente", "cod_Sede", "cod_Mensajero",
        "tiempo_Estado_Iniciado", "tiempo_Estado_Asignado",
        "tiempo_Estado_Recogido", "tiempo_Estado_Entregado",
    ]
    df_entregas = df_entregas[columnas_finales]
    df_entregas["saved"] = date.today()
    
    print(df_entregas)
    
    return df_entregas