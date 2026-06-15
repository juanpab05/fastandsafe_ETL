import pandas as pd
import datetime
from datetime import date
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
import yaml
from etl import extract, transform, load
import psycopg2


pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

#Lectura de los datos de config.yml para conectarse a la base de datos y bodega de datos
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    config_oltp = config['OLTP']
    config_olap = config['OLAP']

# Construct the database URL
url_oltp = (f"{config_oltp['drivername']}://{config_oltp['user']}:{config_oltp['password']}@{config_oltp['host']}:"
          f"{config_oltp['port']}/{config_oltp['dbname']}")
url_olap = (f"{config_olap['drivername']}://{config_olap['user']}:{config_olap['password']}@{config_olap['host']}:"
           f"{config_olap['port']}/{config_olap['dbname']}")
# Create the SQLAlchemy Engine
oltp_conn = create_engine(url_oltp)
olap_conn = create_engine(url_olap)


#if utils_etl.new_data(olap_conn):

#Aqui va ir el codigo donde se llaman las funciones de extraccion, transformacion y por ultimo carga de las tablas.
dim_sede = extract.extract_sede(oltp_conn)
print(dim_sede.head())


