# fastandsafe_ETL
ETL de la base de datos "fast and safe".

##Instalar requisitos
Crear un ambiente de entorno:
```
python3 -m venv my_env

#unix systems
source my_env/bin/activate  

#win
python3 -m venv my_env

#cmd.exe
C:\> <venv>\Scripts\activate.bat

#PowerShell
PS C:\> <venv>\Scripts\Activate.ps1
```
Instalar los paquetes:
```
pip install -r requirements.txt
```
Estructura de config.yml (no se sube por razones de seguridad)
```
OLTP:
  drivername: postgresql  
  user: postgres # su username
  password : valor_privado
  port: 5432 # pordefecto 
  host: localhost # la direccion a la base de datos
  dbname: fastandsafe_oltp #nombre de la base de datos

OLAP:
  drivername: postgresql  
  user: postgres # su username
  password : valor_privado
  port: 5432 # pordefecto 
  host: localhost # la direccion a la bodega de datos
  dbname: fastandsafe_olap #nombre de la bodega de datos
```
