
# Analizador de diferencias entre reportes de combustible y kilometraje GPS

## 1. Descripción del proyecto

Este proyecto consiste en el desarrollo de una herramienta en Python para comparar la información de kilometraje registrada en reportes mensuales de combustible con los kilómetros calculados a partir de datos de rastreo satelital GPS.

El objetivo es identificar diferencias entre ambas fuentes de información, detectar posibles inconsistencias y generar reportes que faciliten su revisión y seguimiento histórico por vehículo y periodo.

El proyecto surgió de una necesidad práctica de análisis y validación de información vehicular.

## 2. Objetivos

- Procesar archivos Excel con información de rastreo GPS.
- Calcular distancias recorridas a partir de coordenadas geográficas.
- Consolidar el kilometraje GPS por vehículo, mes y año.
- Procesar reportes mensuales de combustible.
- Comparar el kilometraje reportado con el calculado mediante GPS.
- Identificar y clasificar diferencias entre ambas fuentes.
- Generar reportes históricos para facilitar el seguimiento de los resultados.

## 3. Tecnologías utilizadas

- **Python:** desarrollo de la herramienta.
- **Pandas:** lectura, transformación, limpieza y análisis de datos.
- **Geopy:** cálculo de distancias geográficas entre coordenadas GPS.
- **OpenPyXL:** lectura y generación de archivos Excel.
- **Excel:** almacenamiento de información y presentación de resultados.

## 4. Funcionamiento general

### 1. Procesamiento de información GPS

Se leen los archivos de rastreo satelital de cada vehículo.

El programa:
- Identifica las columnas necesarias.
- Convierte las coordenadas, velocidades y fechas a formatos adecuados.
- Ordena los registros cronológicamente.
- Calcula la distancia entre posiciones GPS consecutivas.
- Aplica criterios mínimos de velocidad y distancia.
- Consolida los kilómetros recorridos por vehículo y periodo.
- Actualiza el histórico de kilometraje GPS.

### 2. Procesamiento de reportes de combustible

Se procesan los archivos Excel con los reportes mensuales de combustible.

Se extraen y organizan los datos necesarios para integrar la información de cada vehículo y periodo.

### 3. Comparación y análisis

Se relacionan los registros de combustible con los registros GPS utilizando el número económico del vehículo y el periodo correspondiente.

Se calculan los siguientes indicadores:

**Diferencia de kilómetros:**

Diferencia = Kilómetros reportados en combustible − Kilómetros GPS

**Porcentaje de diferencia:**

Porcentaje = (Diferencia / Kilómetros reportados en combustible) × 100

Las diferencias se clasifican de acuerdo con los siguientes criterios establecidos para el proyecto:

| Clasificación | Criterio |
|---|---|
| Coincide | Diferencia absoluta menor al 10 % |
| Diferencia moderada | Diferencia absoluta igual o mayor al 10 % y menor al 20 % |
| Diferencia significativa | Diferencia absoluta igual o mayor al 20 % |
| Sin datos de kilometraje | No es posible calcular el porcentaje de diferencia |

Estos umbrales son criterios de análisis definidos para este proyecto, no estándares universales.

## 5. Resultados generados

El programa genera archivos Excel que permiten consultar:

- Kilometraje GPS por vehículo y periodo.
- Resumen mensual de combustible.
- Diferencias entre el kilometraje reportado y el calculado mediante GPS.
- Porcentajes de diferencia y clasificación.
- Histórico de resultados para comparar distintos periodos.

