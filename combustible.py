import pandas as pd
from pathlib import Path
import unicodedata


CARPETA_COMBUSTIBLE = Path("combustible")
CARPETA_RESULTADOS = Path("resultados")


MESES = {
    "ENERO": "Enero",
    "FEBRERO": "Febrero",
    "MARZO": "Marzo",
    "ABRIL": "Abril",
    "MAYO": "Mayo",
    "JUNIO": "Junio",
    "JULIO": "Julio",
    "AGOSTO": "Agosto",
    "SEPTIEMBRE": "Septiembre",
    "OCTUBRE": "Octubre",
    "NOVIEMBRE": "Noviembre",
    "DICIEMBRE": "Diciembre"
}


def normalizar_nombre(nombre):
    if pd.isna(nombre):
        return ""

    texto = str(nombre).strip().upper()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


def obtener_mes_de_hoja(nombre_hoja):

    if not nombre_hoja.upper().startswith("C-"):
        return None

    nombre_mes = (
        nombre_hoja[2:]
        .strip()
        .upper()
    )

    return MESES.get(nombre_mes)


def leer_reporte_combustible():

    archivos = [
        archivo
        for archivo in CARPETA_COMBUSTIBLE.glob("*.xlsx")
        if not archivo.name.startswith("~$")
    ]

    if not archivos:
        print("No se encontró ningún archivo de combustible.")
        return None

    archivo = archivos[0]

    print("\n========================================")
    print("REPORTE DE COMBUSTIBLE")
    print("========================================")
    print(f"Archivo: {archivo.name}")

    excel = pd.ExcelFile(archivo)

    hojas = [
        hoja
        for hoja in excel.sheet_names
        if hoja.upper().startswith("C-")
    ]

    if not hojas:
        print("\nNo se encontraron hojas con formato C-Mes.")
        return None

    print("\nHojas encontradas:")

    for hoja in hojas:
        print(f"  - {hoja}")

    resultados = []

    for hoja in hojas:

        mes = obtener_mes_de_hoja(hoja)

        if mes is None:
            print(
                f"\nADVERTENCIA: "
                f"No se pudo identificar el mes de la hoja '{hoja}'."
            )
            continue

        print("\n----------------------------------------")
        print(f"Procesando hoja: {hoja}")
        print(f"Mes: {mes}")
        print("----------------------------------------")

        df = pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=3
        )

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        print(f"Registros encontrados: {len(df)}")

        columnas_requeridas = [
            "No.",
            "No. Económico",
            "Placa",
            "Resguardante",
            "Km. Inicial",
            "Km. Final",
            "Km. Recorridos en el mes",
            "Litros cargados en el mes",
            "Monto de carga ($) del mes",
            "Rendimiento del mes"
        ]

        faltantes = [
            columna
            for columna in columnas_requeridas
            if columna not in df.columns
        ]

        if faltantes:
            print(
                f"\nERROR en la hoja {hoja}."
            )
            print(
                "Faltan las siguientes columnas:"
            )
            print(faltantes)
            continue

        df["RESGUARDANTE_NORMALIZADO"] = (
            df["Resguardante"]
            .apply(normalizar_nombre)
        )

        columnas = [
            "No.",
            "No. Económico",
            "Placa",
            "Resguardante",
            "RESGUARDANTE_NORMALIZADO",
            "Km. Inicial",
            "Km. Final",
            "Km. Recorridos en el mes",
            "Litros cargados en el mes",
            "Monto de carga ($) del mes",
            "Rendimiento del mes"
        ]

        df_resumen = df[columnas].copy()

        # Agregamos el mes correspondiente a la hoja
        df_resumen["Mes"] = mes

        resultados.append(df_resumen)

    if not resultados:
        print("\nNo se pudo procesar ninguna hoja.")
        return None

    df_resumen_total = pd.concat(
        resultados,
        ignore_index=True
    )

    # Orden cronológico de los meses
    orden_meses = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12
    }

    df_resumen_total["Mes_Numero"] = (
        df_resumen_total["Mes"]
        .map(orden_meses)
    )

    df_resumen_total = (
        df_resumen_total
        .sort_values(
            ["Mes_Numero", "No. Económico"]
        )
        .reset_index(drop=True)
    )

    # Mes_Numero solamente se utiliza para ordenar
    df_resumen_total = df_resumen_total.drop(
        columns=["Mes_Numero"]
    )

    CARPETA_RESULTADOS.mkdir(exist_ok=True)

    ruta_salida = (
        CARPETA_RESULTADOS
        / "Resumen_Combustible.xlsx"
    )

    df_resumen_total.to_excel(
        ruta_salida,
        index=False
    )

    print("\n========================================")
    print("RESUMEN DE COMBUSTIBLE GENERADO")
    print("========================================")

    print(
        f"\nTotal de registros: "
        f"{len(df_resumen_total)}"
    )

    print("\nRegistros por mes:")

    print(
        df_resumen_total["Mes"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(
        f"\nArchivo generado:\n"
        f"{ruta_salida}"
    )

    return df_resumen_total


if __name__ == "__main__":
    leer_reporte_combustible()