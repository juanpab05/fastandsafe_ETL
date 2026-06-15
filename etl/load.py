import pandas as pd
from pandas import DataFrame
from sqlalchemy.engine import Engine
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

#Aqui va el codigo para cargar las tablas transformadas a la bodega de datos
def load(table: DataFrame, olap_conn: Engine, tname):
    table.to_sql(f'{tname}', olap_conn, if_exists='append', index=False)