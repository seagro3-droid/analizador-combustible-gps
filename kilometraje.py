from tarfile import data_filter

import pandas as pd
from geopy.distance import geodesic
from pathlib import Path
import config

def obtener_nombre_vehiculo(archivo):
    return archivo.stem.strip()

def cargar_datos(archivo):
    df = pd.read_excel(archivo, header=1)

    print(f'Registros encontrados: {len(df)}')
    return df

def preparar_datos(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
    )

    columnas_necesarias = [
        "latitud",
        "longitud",
        "speed",
        "position time"
    ]

    faltantes = [
        columna for columna in columnas_necesarias
        if columna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas: "
            + ", ".join(faltantes)
        )

    df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
    df["speed"] = pd.to_numeric(df["speed"], errors="coerce")
    df["position time"] = pd.to_datetime(df["position time"], errors="coerce")
    df = df.dropna(subset=["latitud", "longitud", "position time"])
    df = (df.sort_values("position time").reset_index(drop=True))

    return df

def calcular_distancia( lat1, lon1, lat2, lon2 ):
    punto_anterior = (lat1, lon1)
    punto_actual = (lat2, lon2)
    return geodesic( punto_anterior, punto_actual ).kilometers

def calcular_kilometraje(df):
    kilometros = []

    for i in range(len(df)):
        if i == 0:
            kilometros.append(0)
            continue

        anterior = df.iloc[i - 1]
        actual = df.iloc[i]
        velocidad = actual["speed"]

        if (
                pd.notna(velocidad)
                and velocidad < config.VELOCIDAD_MINIMA
        ):
            kilometros.append(0)
            continue

        distancia = calcular_distancia(
            anterior["latitud"],
            anterior["longitud"],
            actual["latitud"],
            actual["longitud"]
        )

        if distancia < config.DISTANCIA_MINIMA:
            distancia = 0

        kilometros.append(distancia)

    df["kilometros_recorridos"] = kilometros

    return df


def agregar_periodo(df, vehiculo):
    meses_espanol = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                     9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    df["vehiculo"] = vehiculo
    df["fecha"] = (df["position time"].dt.date)
    df["año"] = (df["position time"].dt.year)
    df["mes_numero"] = (df["position time"].dt.month)
    df["mes"] = ( df["mes_numero"] .map(meses_espanol) )
    return df

def generar_resumen_mensual(df):

    resumen = (df.groupby(["vehiculo", "año", "mes_numero", "mes"])
               .agg(kilometros_recorridos=("kilometros_recorridos", "sum"),
                dias_con_recorrido=("fecha", lambda x: x[df.loc[x.index, "kilometros_recorridos"] > 0].nunique()
                ), registros_gps=("position time", "count")).reset_index())

    resumen["kilometros_recorridos"] = resumen["kilometros_recorridos"].round(2)

    return resumen
def guardar_resultado_mensual( df, resumen_mensual, vehiculo, año, mes_numero ):
    nombre_archivo = (f"{vehiculo}_" f"{año}-" f"{mes_numero:02d}.xlsx")
    archivo_salida = (config.CARPETA_RESULTADOS / nombre_archivo)
    with pd.ExcelWriter(archivo_salida, engine="openpyxl") as writer:
        resumen_mensual.to_excel(writer, sheet_name="Resumen mensual", index=False)
        df.to_excel(writer, sheet_name="Datos GPS", index=False)
        print(f"Resultado mensual guardado: " f"{archivo_salida}")

def actualizar_historico( resumen_mensual):

    if config.ARCHIVO_HISTORICO.exists():
        historico = pd.read_excel( config.ARCHIVO_HISTORICO )
        historico = pd.concat( [ historico, resumen_mensual ], ignore_index=True )

    else:
        historico = resumen_mensual.copy()

    historico = (historico.drop_duplicates(subset=["vehiculo", "año", "mes_numero"],keep="last" ) )
    historico = (historico.sort_values(["vehiculo", "año", "mes_numero"]).reset_index(drop=True))
    historico.to_excel(config.ARCHIVO_HISTORICO, index=False)
    print(f"Histórico actualizado: " f"{config.ARCHIVO_HISTORICO}")

def procesar_archivo( archivo ):
    print("\n========================================")
    print(f"Procesando: {archivo.name}")
    print("========================================")

    vehiculo = obtener_nombre_vehiculo(archivo)
    df = cargar_datos(archivo)
    df = preparar_datos(df)
    df = calcular_kilometraje(df)
    df = agregar_periodo(df, vehiculo)
    resumen_mensual = (generar_resumen_mensual(df))
    año = int(resumen_mensual["año"].iloc[0])
    mes_numero = int(resumen_mensual["mes_numero"].iloc[0])
    guardar_resultado_mensual(df, resumen_mensual, vehiculo, año, mes_numero)
    actualizar_historico(resumen_mensual)
    kilometraje = (resumen_mensual["kilometros_recorridos"].iloc[0])
    print(f"\nKilometraje de {vehiculo}: " f"{kilometraje:.2f} km")

def main():
    print("========================================")
    print("ANÁLISIS HISTÓRICO DE KILOMETRAJE GPS")
    print("========================================")
    archivos = list(config.CARPETA_GPS.glob("*.xls"))
    archivos += list(config.CARPETA_GPS.glob("*.xlsx"))

    if not archivos:
        print("\nNo se encontraron archivos GPS " "en la carpeta:")
        print(config.CARPETA_GPS)
        return
    print(f"\nArchivos encontrados: " f"{len(archivos)}")

    for archivo in archivos:
        try:
            procesar_archivo(archivo)

        except Exception as error:
            print(f"\nERROR procesando " f"{archivo.name}:")
            print(error)

if __name__ == "__main__":
    main()
