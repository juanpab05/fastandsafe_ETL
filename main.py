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
#Extracciones
print("--- INICIANDO FASE DE EXTRACCIÓN ---")
raw_fecha = extract.extract_fecha()
raw_hora = extract.extract_hora()

dim_sede = extract.extract_sede(oltp_conn)
dim_mensajero = extract.extract_mensajero(oltp_conn)
tabla_usuario = extract.extract_usuario(oltp_conn)
dim_cliente = extract.extract_cliente(oltp_conn)
dim_novedad = extract.extract_novedad(oltp_conn)

# >>> NUEVAS EXTRACCIONES PARA LA TABLA DE HECHOS 
raw_novedad_servicio = extract.extract_novedades_servicio(oltp_conn)
raw_servicio = extract.extract_servicio(oltp_conn)
raw_estado_servicio = extract.extract_estado_servicio(oltp_conn)
raw_usuarioaquitoy = extract.extract_usuarioaquitoy(oltp_conn)

#Transformaciones:
print("\n--- INICIANDO FASE DE TRANSFORMACIÓN ---")
dim_fecha = transform.transform_fecha(raw_fecha)
dim_hora = transform.transform_hora(raw_hora)
dim_sede = transform.transform_sede(dim_sede)
dim_mensajero = transform.transform_mensajero(dim_mensajero, tabla_usuario)
dim_cliente = transform.transform_cliente(dim_cliente)
dim_novedad = transform.transform_novedad(dim_novedad)

# >>> NUEVA TRANSFORMACIÓN PARA LA TABLA DE HECHOS 
fact_novedades = transform.transform_fact_novedades(raw_novedad_servicio, raw_servicio, dim_hora)
fact_entregas = transform.transform_fact_entregas(raw_estado_servicio, raw_servicio, raw_usuarioaquitoy, dim_fecha, dim_hora)

#Cargas: 
print("\n--- INICIANDO FASE DE CARGA A LA BODEGA ---")

# Full refresh: vaciamos las tablas del datamart antes de recargar para garantizar
# idempotencia (correr el ETL N veces deja el mismo resultado, sin duplicados).
# CASCADE resuelve el orden de las FK (hechos -> dimensiones) automáticamente.
tablas_datamart = [
    "fact_novedades", "fact_entregas",
    "dim_fecha", "dim_hora", "dim_sede",
    "dim_mensajero", "dim_cliente", "dim_novedad",
]
# with olap_conn.begin() as conn:
#    conn.execute(text(f"TRUNCATE TABLE {', '.join(tablas_datamart)} RESTART IDENTITY CASCADE"))

load.load(dim_fecha, olap_conn, "dim_fecha")
load.load(dim_hora, olap_conn, "dim_hora")

load.load(dim_sede, olap_conn, "dim_sede")
load.load(dim_mensajero, olap_conn, "dim_mensajero")
load.load(dim_cliente, olap_conn, "dim_cliente")
load.load(dim_novedad, olap_conn, "dim_novedad")

# >>> NUEVA CARGA PARA LA TABLA DE HECHOS 
load.load(fact_novedades, olap_conn, "fact_novedades")
load.load(fact_entregas, olap_conn, "fact_entregas")
