import pandas as pd
from sqlalchemy.engine import Engine

#Aqui va el codigo para extraer las tablas de la base de datos
def extract_fecha() -> pd.DatetimeIndex:
    """Genera el rango de tiempo bruto diario para la dimensión fecha."""
    # Genera un índice con todos los días desde el 2020 hasta el 2030
    return pd.date_range(start="2020-01-01", end="2030-12-31", freq="D")


def extract_hora() -> pd.DatetimeIndex:
    """Genera el rango de tiempo bruto para el día completo (por minuto)."""
    # Se extrae/genera la serie de tiempo limpia de 00:00 a 23:59
    rango_tiempo = pd.date_range("00:00:00", "23:59:00", freq="min")
    return rango_tiempo


def extract_sede(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("sede", connection)


def extract_mensajero(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("clientes_mensajeroaquitoy", connection)


def extract_usuario(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("auth_user", connection)


def extract_cliente(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("cliente", connection)


def extract_novedad(connection: Engine) -> pd.DataFrame:
    return pd.read_sql_table("mensajeria_tiponovedad", connection)

# Estas funciones de extracción adicionales se pueden usar para obtener datos más detallados sobre las novedades y servicios, si es necesario para futuras transformaciones o análisis.

def extract_novedades_servicio(connection: Engine) -> pd.DataFrame:
    """Extrae las novedades operacionales registradas en el día a día."""
    return pd.read_sql_table("mensajeria_novedadesservicio", connection)

def extract_servicio(connection: Engine) -> pd.DataFrame:
    """Extrae las planillas o servicios base para cruzar con las novedades."""
    return pd.read_sql_table("mensajeria_servicio", connection)
