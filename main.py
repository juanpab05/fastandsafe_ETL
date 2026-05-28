import pandas as pd
import datetime
from datetime import date
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
import yaml
from etl import extract, transform, load, utils_etl
import psycopg2

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

#Lectura de los datos de config.yml para conectarse a la base de datos y bodega de datos
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    config_db = config['OLTP']
    config_etl = config['OLAP']

# Construct the database URL
url_db = (f"{config_db['drivername']}://{config_db['user']}:{config_db['password']}@{config_db['host']}:"
          f"{config_db['port']}/{config_db['dbname']}")
url_etl = (f"{config_etl['drivername']}://{config_etl['user']}:{config_etl['password']}@{config_etl['host']}:"
           f"{config_etl['port']}/{config_etl['dbname']}")
# Create the SQLAlchemy Engine
db_conn = create_engine(url_db)
etl_conn = create_engine(url_etl)

#Aqui va ir el codigo donde se llaman las funciones de extraccion, transformacion y por ultimo carga de las tablas.

