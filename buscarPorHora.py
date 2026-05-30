from datetime import datetime
import os
import pandas as pd


def buscar_todo_por_hora(path_metrics, path_consumption, hora_buscada_str):
    # 1. Validación de seguridad: Comprobar si los archivos existen de verdad en sus rutas
    if not os.path.exists(path_metrics):
        return f"❌ El archivo de métricas no existe en la ruta especificada:\n{path_metrics}"
    if not os.path.exists(path_consumption):
        return f"❌ El archivo de consumo no existe en la ruta especificada:\n{path_consumption}"

    # 2. Cargar los archivos desde sus ubicaciones independientes
    df_m = pd.read_csv(path_metrics)
    df_c = pd.read_csv(path_consumption)

    df_m["timestamp"] = pd.to_datetime(df_m["timestamp"])
    df_c["timestamp"] = pd.to_datetime(df_c["timestamp"])

    fecha_base = df_m["timestamp"].dt.date.iloc[0]
    hora_objetivo = datetime.strptime(
        f"{fecha_base} {hora_buscada_str}", "%Y-%m-%d %H:%M:%S"
    )

    # 3. Buscar fila más cercana en Métricas (Época)
    df_m["diff"] = (df_m["timestamp"] - hora_objetivo).abs()
    fila_m = df_m.loc[df_m["diff"].idxmin()]

    # 4. Buscar fila más cercana en Consumo (Vatios)
    df_c["diff"] = (df_c["timestamp"] - hora_objetivo).abs()
    fila_c = df_c.loc[df_c["diff"].idxmin()]

    return (
        f"--- AUDITORÍA TEMPORAL PARA TFG ---\n"
        f"⏱️ Hora consultada: {hora_buscada_str}\n"
        f"------------------------------------\n"
        f"🔄 Época / Paso del modelo: {fila_m['step']}\n"
        f"📉 Inercia en ese instante: {fila_m['value']:.4f}\n"
        f"⚡ Consumo del hardware: {fila_c['watts']} W\n"
        f"🔋 Energía acumulada: {fila_c['accum']} W·s\n"
    )


# =====================================================================
# CONFIGURACIÓN DE RUTAS INDEPENDIENTES
# =====================================================================
# 🔴 Modifica estas rutas poniendo la dirección exacta de dónde está cada CSV
ruta_archivo_metricas = r"C:\Users\samue\Desktop\TFG\new_repo\greenEarlyStopping\Training Metrics (2)\Training Metrics\ADR\28-05-2026_17-32-33.csv"
ruta_archivo_consumo = r"C:\Users\samue\Desktop\TFG\new_repo\greenEarlyStopping\Training Metrics (2)\Training Metrics\ADR\consumption_28-05-2026_17-32-12.csv"
# Hora en formato HH:MM:SS que quieres auditar
hora_a_consultar = "17:33:40"

# Ejecución
print(
    buscar_todo_por_hora(
        ruta_archivo_metricas, ruta_archivo_consumo, hora_a_consultar
    )
)