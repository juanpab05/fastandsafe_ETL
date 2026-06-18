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
    dim_cliente.drop(columns=['email', 'direccion', 'telefono', 'nombre_contacto', 'tipo_cliente_id', 'activo', 'coordinador_id', 'sector'], inplace=True)    
    dim_cliente.rename(columns={"cliente_id": "key_dim_cliente"}, inplace=True)
    dim_cliente.sort_values(by=["key_dim_cliente"], inplace=True)
    dim_cliente["saved"] = date.today()

    print(dim_cliente)
    
    return dim_cliente


def transform_novedad(dim_novedad: DataFrame) -> DataFrame:
    """
    Parametros: dim_novedad.
    """
    dim_novedad.rename(columns={"id": "key_dim_novedad", "nombre": "tipo_novedad"}, inplace=True)
    dim_novedad.sort_values(by=["key_dim_novedad"], inplace=True)
    dim_novedad["saved"] = date.today()

    return dim_novedad
