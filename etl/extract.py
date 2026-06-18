import pandas as pd
from sqlalchemy.engine import Engine

#Aqui va el codigo para extraer las tablas de la base de datos
def extract_sede(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("sede", connection)


def extract_ciudad(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("ciudad", connection)


def extract_mensajero(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("clientes_mensajeroaquitoy", connection)


def extract_usuario(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("auth_user", connection)


def extract_cliente(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("cliente", connection)


def extract_novedad(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("mensajeria_tiponovedad", connection)
