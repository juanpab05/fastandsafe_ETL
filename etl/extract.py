import pandas as pd
from sqlalchemy.engine import Engine

#Aqui va el codigo para extraer las tablas de la base de datos
def extract_sede(conection: Engine):

    dim_sede = pd.read_sql_table('sede', conection)
    return dim_sede

def extract_ciudad(conection: Engine):

    tabla_ciudad = pd.read_sql_table('ciudad', conection)
    return tabla_ciudad

def extract_mensajero(conection: Engine):

    dim_mensajero = pd.read_sql_table('clientes_mensajeroaquitoy', conection)
    return dim_mensajero

def extract_usuario(conection: Engine):
    
    tabla_usuario = pd.read_sql_table('auth_user', conection)
    return tabla_usuario