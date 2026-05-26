import sys
import threading
import asyncio
from queue import Queue
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog
from styles.config_logs import LogType

# Imports de tu proyecto
from gui.gui_main import AppEco
from gui.windows.gui_configuration_window import ConfigWindow
from core.engine import measure_consumption
from core.mqtt_listener import init_mqtt_listener

# --- GLOBAL PARA CONTROL DE HILOS ---
# avisar al hilo del Tapo que debe cerrarse
tapo_stop_event = threading.Event()

def manage_plug_threads(nuevos_datos, q):
    """Detiene el hilo actual y lanza uno nuevo con las credenciales actualizadas."""
    global tapo_stop_event
    
    # 1. Indicamos al hilo actual que debe terminar su bucle
    tapo_stop_event.set() 
    
    # 2. Creamos un nuevo evento de parada (limpio) para el siguiente hilo
    tapo_stop_event = threading.Event()
    
    # 3. Función interna que ejecutará el bucle de asyncio
    def run_engine():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Pasamos el tapo_stop_event al engine para que consulte .is_set()
            loop.run_until_complete(measure_consumption(q, nuevos_datos, tapo_stop_event))
        finally:
            loop.close()
            main_win.terminal.log("[MAIN] Bucle de motor Tapo cerrado.", LogType.ERROR)
    
    # 4. Lanzamos el hilo como daemon para que muera si cerramos la App
    hilo = threading.Thread(target=run_engine, daemon=True)
    hilo.start()
    main_win.terminal.log(f"[MAIN] Hilo Tapo reiniciado para IP: {nuevos_datos.get('ip')}",LogType.WARNING)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_queue = Queue()

    # 1. Configuración Inicial
    config = ConfigWindow()
    if config.exec() == QDialog.DialogCode.Accepted:
        start_data = config.config_data
        
        # 2. Iniciar Ventana Principal
        main_win = AppEco(data_queue)
        
        # --- CONEXIÓN DE RECONEXIÓN ---
        # Conectamos la señal de la ventana al gestor de hilos del main
        main_win.reconnection_request.connect(lambda nuevos_dt: manage_plug_threads(nuevos_dt, data_queue))
        
        # 3. Lanzar el Broker Mosquitto con CONFIGURACIÓN DE RED
        base_directory = os.path.dirname(os.path.abspath(__file__))
        broker_path = os.path.join(base_directory, "Mosquitto", "mosquitto.exe")
        config_path = os.path.join(base_directory, "Mosquitto", "mosquitto.conf")
        try:
            broker_process = subprocess.Popen([broker_path, "-c", config_path])
            main_win.terminal.log("BROKER: Mosquitto iniciado correctamente.", LogType.SUCCESS)
        except Exception as e:
            main_win.terminal.log(f"BROKER: Error al iniciar: {e}", LogType.ERROR)

        # 4. Iniciar el motor Tapo por primera vez
        manage_plug_threads(start_data, data_queue)

        # 5. Iniciar el Listener MQTT (para recibir métricas)
        mqtt_thread = threading.Thread(target=init_mqtt_listener, args=(main_win,), daemon=True)
        mqtt_thread.start()
        
        # 6. Mostrar Interfaz y ejecutar App
        main_win.show()
        
        # Al salir, intentamos matar el proceso del broker para no dejar procesos zombis
        result = app.exec()
        try:
            broker_process.terminate()
        except:
            pass
        
        sys.exit(result)