import pandas as pd
from pathlib import Path
import config


MESES = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE"
}


MESES_NUMERO = {
    nombre: numero
    for numero, nombre in MESES.items()
}


def normalizar_numero_economico(valor):

    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip().upper()

    texto = texto.replace("VEH", "")
    texto = texto.replace(" ", "")
    texto = texto.replace("-", "")

    try:
        return int(float(texto))
    except (ValueError, TypeError):
        return pd.NA


def obtener_mes_numero(valor):

    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip().upper()

    # Si viene como nombre
    if texto in MESES_NUMERO:
        return MESES_NUMERO[texto]

    # Si viene como número
    try:
        numero = int(float(texto))

        if 1 <= numero <= 12:
            return numero

    except (ValueError, TypeError):
        pass

    return pd.NA


def detectar_anio(df_kilometraje, mes_numero):

    anios = (
        df_kilometraje[
            df_kilometraje["mes_numero"] == mes_numero
        ]["año"]
        .dropna()
        .unique()
    )

    if len(anios) == 1:
        return int(anios[0])

    if len(anios) == 0:
        return None

    raise ValueError(
        f"Se encontraron varios años para el mes "
        f"{MESES[mes_numero]}: {anios}."
    )


def clasificar_diferencia(valor):

    if pd.isna(valor):
        return "SIN DATOS KILOMETRAJE"

    if abs(valor) >= 20:
        return "DIFERENCIA SIGNIFICATIVA"

    if abs(valor) >= 10:
        return "DIFERENCIA MODERADA"

    return "COINCIDE"


print("\n")
print("=" * 70)
print("ANALIZADOR DE COMBUSTIBLE Y KILOMETRAJE")
print("=" * 70)


# ============================================================
# 1. LEER HISTÓRICO GPS
# ============================================================

archivo_gps = config.ARCHIVO_HISTORICO

if not archivo_gps.exists():

    raise FileNotFoundError(
        f"\nNo se encontró el histórico GPS:\n"
        f"{archivo_gps}\n\n"
        f"Primero ejecuta kilometraje.py."
    )


print("\nLeyendo histórico de kilometraje GPS...")

df_kilometraje = pd.read_excel(
    archivo_gps
)

print(
    f"Registros históricos GPS encontrados: "
    f"{len(df_kilometraje)}"
)

columnas_gps = [
    "vehiculo",
    "año",
    "mes_numero",
    "mes",
    "kilometros_recorridos"
]


faltantes_gps = [
    columna
    for columna in columnas_gps
    if columna not in df_kilometraje.columns
]


if faltantes_gps:

    raise ValueError(
        "Faltan columnas en el histórico GPS: "
        + ", ".join(faltantes_gps)
    )


# Normalizar número económico del GPS

df_kilometraje["NUMERO_ECONOMICO"] = (
    df_kilometraje["vehiculo"]
    .apply(normalizar_numero_economico)
)


print("\nNÚMEROS ECONÓMICOS DEL GPS:")

print(
    df_kilometraje[
        [
            "vehiculo",
            "NUMERO_ECONOMICO"
        ]
    ]
    .drop_duplicates()
    .sort_values("NUMERO_ECONOMICO")
    .to_string(index=False)
)


# ============================================================
# 2. LEER RESUMEN DE COMBUSTIBLE
# ============================================================

archivo_combustible = (
    Path("resultados")
    / "Resumen_Combustible.xlsx"
)


if not archivo_combustible.exists():

    raise FileNotFoundError(
        "\nNo se encontró el resumen de combustible:\n"
        f"{archivo_combustible}\n\n"
        "Primero ejecuta combustible.py."
    )


print("\n")
print("=" * 70)
print("LEYENDO RESUMEN DE COMBUSTIBLE")
print("=" * 70)


df_combustible = pd.read_excel(
    archivo_combustible
)


print(
    f"\nRegistros de combustible encontrados: "
    f"{len(df_combustible)}"
)


print("\nColumnas:")

print(
    df_combustible.columns.tolist()
)


if "No. Económico" not in df_combustible.columns:

    raise ValueError(
        "No se encontró la columna "
        "'No. Económico' "
        "en el reporte de combustible."
    )


if "Mes" not in df_combustible.columns:

    raise ValueError(
        "No se encontró la columna 'Mes' "
        "en el reporte de combustible."
    )


# Normalizar número económico

df_combustible["NUMERO_ECONOMICO"] = (
    df_combustible["No. Económico"]
    .apply(normalizar_numero_economico)
)


# Detectar número de mes

df_combustible["mes_numero"] = (
    df_combustible["Mes"]
    .apply(obtener_mes_numero)
)


# ============================================================
# 3. DETECTAR MESES DISPONIBLES
# ============================================================

meses_en_archivo = sorted(
    df_combustible["mes_numero"]
    .dropna()
    .unique()
)


print("\n")
print("=" * 70)
print("MESES DETECTADOS EN COMBUSTIBLE")
print("=" * 70)


for mes_numero in meses_en_archivo:

    print(
        f"{int(mes_numero):02d} - "
        f"{MESES[int(mes_numero)]}"
    )


# ============================================================
# 4. PROCESAR CADA MES
# ============================================================

resultados_mensuales = []


for mes_numero in meses_en_archivo:

    mes_numero = int(mes_numero)

    mes = MESES[mes_numero]

    print("\n")
    print("=" * 70)
    print(f"PROCESANDO: {mes}")
    print("=" * 70)


    # --------------------------------------------------------
    # Determinar año mediante GPS
    # --------------------------------------------------------

    anio = detectar_anio(
        df_kilometraje,
        mes_numero
    )


    if anio is None:

        print(
            f"\nADVERTENCIA: "
            f"No existe información GPS para {mes}."
        )

        print(
            "El mes no será incluido en "
            "la comparación."
        )

        continue


    print(
        f"\nPeriodo detectado: "
        f"{mes} {anio}"
    )


    # --------------------------------------------------------
    # Filtrar combustible del mes
    # --------------------------------------------------------

    df_combustible_mes = df_combustible[
        df_combustible["mes_numero"] == mes_numero
    ].copy()


    print(
        f"Registros de combustible: "
        f"{len(df_combustible_mes)}"
    )

    # --------------------------------------------------------
    # Verificar si el mes realmente tiene datos de combustible
    # --------------------------------------------------------

    columnas_datos = [
        "Km. Recorridos en el mes",
        "Litros cargados en el mes",
        "Monto de carga ($) del mes"
    ]

    tiene_datos = False

    for columna in columnas_datos:

        if columna in df_combustible_mes.columns:

            valores = pd.to_numeric(
                df_combustible_mes[columna],
                errors="coerce"
            ).fillna(0)

            if valores.sum() > 0:
                tiene_datos = True
                break

    if not tiene_datos:
        print(
            f"\nADVERTENCIA: {mes} no contiene "
            "datos reales de combustible."
        )

        print(
            "El mes parece ser una plantilla "
            "sin información de cargas."
        )

        print(
            "No se incluirá en la comparación."
        )

        continue

    # --------------------------------------------------------
    # Filtrar GPS del mes
    # --------------------------------------------------------

    df_gps_mes = df_kilometraje[
        (df_kilometraje["año"] == anio)
        &
        (df_kilometraje["mes_numero"] == mes_numero)
    ].copy()


    print(
        f"Registros GPS: "
        f"{len(df_gps_mes)}"
    )


    # --------------------------------------------------------
    # Detectar vehículos GPS duplicados
    # --------------------------------------------------------

    duplicados_gps = df_gps_mes[
        df_gps_mes.duplicated(
            subset=["NUMERO_ECONOMICO"],
            keep=False
        )
    ]


    if not duplicados_gps.empty:

        print(
            "\nADVERTENCIA: "
            "Se encontraron números económicos "
            "duplicados en el GPS."
        )

        print(
            duplicados_gps[
                [
                    "vehiculo",
                    "NUMERO_ECONOMICO",
                    "kilometros_recorridos"
                ]
            ]
            .sort_values("NUMERO_ECONOMICO")
            .to_string(index=False)
        )


        # Se conserva un solo registro por
        # número económico para evitar duplicar
        # los registros de combustible.
        df_gps_mes = (
            df_gps_mes
            .drop_duplicates(
                subset=["NUMERO_ECONOMICO"],
                keep="last"
            )
        )


    # --------------------------------------------------------
    # Preparar GPS para el cruce
    # --------------------------------------------------------

    df_gps_mes = df_gps_mes[
        [
            "NUMERO_ECONOMICO",
            "vehiculo",
            "kilometros_recorridos"
        ]
    ].copy()


    df_gps_mes = df_gps_mes.rename(
        columns={
            "kilometros_recorridos": "Km GPS"
        }
    )


    # --------------------------------------------------------
    # Eliminar registros de combustible
    # sin número económico
    # --------------------------------------------------------

    registros_sin_numero = (
        df_combustible_mes[
            df_combustible_mes[
                "NUMERO_ECONOMICO"
            ].isna()
        ]
    )


    if not registros_sin_numero.empty:

        print(
            "\nADVERTENCIA:"
        )

        print(
            "Se encontraron registros de combustible "
            "sin número económico."
        )

        print(
            registros_sin_numero[
                [
                    "No. Económico",
                    "Resguardante"
                ]
            ]
            .to_string(index=False)
        )


        df_combustible_mes = (
            df_combustible_mes[
                df_combustible_mes[
                    "NUMERO_ECONOMICO"
                ].notna()
            ]
        )


    # --------------------------------------------------------
    # CRUCE COMBUSTIBLE VS GPS
    # --------------------------------------------------------

    df = df_combustible_mes.merge(
        df_gps_mes,
        on="NUMERO_ECONOMICO",
        how="left"
    )


    # --------------------------------------------------------
    # Detectar vehículos sin GPS
    # --------------------------------------------------------

    sin_gps = df[
        df["Km GPS"].isna()
    ]


    if not sin_gps.empty:

        print(
            "\nADVERTENCIA: "
            "Los siguientes vehículos de combustible "
            "no tienen kilometraje GPS:"
        )

        print(
            sin_gps[
                [
                    "No. Económico",
                    "Resguardante"
                ]
            ]
            .drop_duplicates()
            .to_string(index=False)
        )


    # --------------------------------------------------------
    # Calcular diferencia
    # --------------------------------------------------------

    df["Diferencia Km"] = (
        df["Km. Recorridos en el mes"]
        - df["Km GPS"]
    )


    df["% Diferencia"] = (
        df["Diferencia Km"]
        /
        df["Km. Recorridos en el mes"]
    ) * 100


    df.loc[
        df["Km. Recorridos en el mes"] == 0,
        "% Diferencia"
    ] = pd.NA


    # --------------------------------------------------------
    # Clasificación
    # --------------------------------------------------------

    df["Indicador"] = (
        df["% Diferencia"]
        .apply(
            clasificar_diferencia
        )
    )

    # --------------------------------------------------------
    # Agregar año y normalizar mes
    # --------------------------------------------------------

    df["Mes"] = mes

    df.insert(
        0,
        "Año",
        anio
    )

    # --------------------------------------------------------
    # Guardar resultado del mes
    # --------------------------------------------------------

    resultados_mensuales.append(
        df.copy()
    )

    # --------------------------------------------------------
    # Mostrar resumen del mes
    # --------------------------------------------------------

    print("\nCOMPARACIÓN")

    columnas_mostrar = [
        "No. Económico",
        "Resguardante",
        "Km. Recorridos en el mes",
        "Km GPS",
        "Diferencia Km",
        "% Diferencia",
        "Indicador"
    ]


    print(
        df[columnas_mostrar]
        .to_string(index=False)
    )


# ============================================================
# 5. CONSOLIDAR TODOS LOS MESES
# ============================================================

if not resultados_mensuales:

    raise ValueError(
        "\nNo se pudo realizar ninguna comparación."
    )


df_resultado_total = pd.concat(
    resultados_mensuales,
    ignore_index=True
)


# ============================================================
# 6. ORDENAR RESULTADOS
# ============================================================

df_resultado_total["Mes_Numero"] = (
    df_resultado_total["Mes"]
    .map(
        {
            "ENERO": 1,
            "FEBRERO": 2,
            "MARZO": 3,
            "ABRIL": 4,
            "MAYO": 5,
            "JUNIO": 6,
            "JULIO": 7,
            "AGOSTO": 8,
            "SEPTIEMBRE": 9,
            "OCTUBRE": 10,
            "NOVIEMBRE": 11,
            "DICIEMBRE": 12
        }
    )
)


df_resultado_total = (
    df_resultado_total
    .sort_values(
        [
            "Año",
            "Mes_Numero",
            "No. Económico"
        ]
    )
    .reset_index(drop=True)
)


df_resultado_total = (
    df_resultado_total
    .drop(columns=["Mes_Numero"])
)


# ============================================================
# 7. GUARDAR RESUMEN COMPLETO
# ============================================================

carpeta_resultados = Path(
    "resultados"
)

carpeta_resultados.mkdir(
    exist_ok=True
)


salida = (
    carpeta_resultados
    / "Resumen_Combustible_GPS.xlsx"
)


df_resultado_total.to_excel(
    salida,
    index=False
)


print("\n")
print("=" * 70)
print("RESUMEN GENERAL GENERADO")
print("=" * 70)


print(
    f"\nTotal de registros comparados: "
    f"{len(df_resultado_total)}"
)


print("\nRegistros procesados por mes:")

print(
    df_resultado_total
    .groupby(
        ["Año", "Mes"]
    )
    .size()
    .to_string()
)


print(
    f"\nArchivo generado:\n"
    f"{salida}"
)


# ============================================================
# 8. ACTUALIZAR HISTÓRICO
# ============================================================

archivo_historico = (
    carpeta_resultados
    / "Historico_Combustible_GPS.xlsx"
)


columnas_historico = [
    "Año",
    "Mes",
    "No. Económico",
    "Placa",
    "Resguardante",
    "Km. Recorridos en el mes",
    "Km GPS",
    "Diferencia Km",
    "% Diferencia",
    "Indicador"
]


df_historico_mes = (
    df_resultado_total[
        columnas_historico
    ]
    .copy()
)


if archivo_historico.exists():

    print(
        "\nHistórico existente encontrado."
    )

    df_historico = pd.read_excel(
        archivo_historico
    )


    # --------------------------------------------------------
    # Eliminar del histórico los meses que estamos
    # procesando nuevamente
    # --------------------------------------------------------

    periodos_procesados = (
        df_historico_mes[
            [
                "Año",
                "Mes"
            ]
        ]
        .drop_duplicates()
    )


    for _, periodo in periodos_procesados.iterrows():

        df_historico = df_historico[
            ~(
                (df_historico["Año"] == periodo["Año"])
                &
                (df_historico["Mes"] == periodo["Mes"])
            )
        ]


    # Agregar nuevamente los datos actualizados

    df_historico = pd.concat(
        [
            df_historico,
            df_historico_mes
        ],
        ignore_index=True
    )


else:

    print(
        "\nCreando histórico por primera vez."
    )

    df_historico = (
        df_historico_mes.copy()
    )


# ============================================================
# 9. ORDENAR HISTÓRICO
# ============================================================

orden_meses = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12
}


df_historico["Mes_Numero"] = (
    df_historico["Mes"]
    .astype(str)
    .str.upper()
    .map(orden_meses)
)


df_historico = (
    df_historico
    .sort_values(
        [
            "Año",
            "Mes_Numero",
            "No. Económico"
        ]
    )
    .reset_index(drop=True)
)


df_historico = (
    df_historico
    .drop(columns=["Mes_Numero"])
)


# ============================================================
# 10. GUARDAR HISTÓRICO
# ============================================================

df_historico.to_excel(
    archivo_historico,
    index=False
)


print(
    f"\nArchivo histórico actualizado:\n"
    f"{archivo_historico}"
)


print("\n")
print("=" * 70)
print("ANÁLISIS TERMINADO")
print("=" * 70)