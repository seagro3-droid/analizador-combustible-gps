from geopy.distance import geodesic
from pathlib import Path

CARPETA_GPS = Path("gps")
CARPETA_RESULTADOS = Path("resultados")
ARCHIVO_HISTORICO = (
    CARPETA_RESULTADOS /"Historico_Kilometraje_GPS.xlsx"
)

VELOCIDAD_MINIMA = 2 #km/h
DISTANCIA_MINIMA = 0.01 #km = 10 metros

# Crear automáticamente la carpeta de resultados
CARPETA_RESULTADOS.mkdir(exist_ok=True)