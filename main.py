import sys
import threading
import asyncio
from queue import Queue
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog
from styles.config_logs import LogType

# Imports de tu proyecto
from gui.main_window import AppEco
from gui.windows.configuration_window import ConfigWindow
from controller.data_receivers.tapo_client import measure_consumption, produce_mock_voltage
from controller.data_receivers.mqtt_listener import init_mqtt_listener

# --- GLOBAL PARA CONTROL DE HILOS ---
# avisar al hilo del Tapo que debe cerrarse
tapo_stop_event = threading.Event()

def manage_plug_threads(new_data, q):
    global tapo_stop_event
    
    tapo_stop_event.set() 
    
    tapo_stop_event = threading.Event()
    
    def run_engine():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(measure_consumption(q, new_data, tapo_stop_event))
        finally:
            loop.close()
            main_win.terminal.log("[MAIN] Bucle de motor Tapo cerrado.", LogType.ERROR)
    
    thread_tapo = threading.Thread(target=run_engine, daemon=True)
    thread_tapo.start()
    main_win.terminal.log(f"[MAIN] Hilo Tapo reiniciado para IP: {new_data.get('ip')}",LogType.WARNING)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_queue = Queue()

    # 1. Configuración Inicial
    config = ConfigWindow()
    if config.exec() == QDialog.DialogCode.Accepted:
        start_data = config.config_data
        
        # MAIN WINDOW THREAD
        main_win = AppEco(data_queue)
        
        # CONNECTING RECONFIGUTARION SIGNAL TO THREAD MANAGER
        main_win.reconnection_request.connect(lambda nuevos_dt: manage_plug_threads(nuevos_dt, data_queue))
        
        # BROKER CONFIGURATION
        base_directory = os.path.dirname(os.path.abspath(__file__))
        broker_path = os.path.join(base_directory, "Mosquitto", "mosquitto.exe")
        config_path = os.path.join(base_directory, "Mosquitto", "mosquitto.conf")
        try:
            broker_process = subprocess.Popen([broker_path, "-c", config_path])
            main_win.terminal.log("BROKER: Mosquitto iniciado correctamente.", LogType.SUCCESS)
        except Exception as e:
            main_win.terminal.log(f"BROKER: Error al iniciar: {e}", LogType.ERROR)

        #INITIALIZE TAPO THREAD
        manage_plug_threads(start_data, data_queue)

        # NEW THREAD FOR MQTT BROKER
        mqtt_thread = threading.Thread(target=init_mqtt_listener, args=(main_win,), daemon=True)
        mqtt_thread.start()
        
        main_win.show()
        
        result = app.exec()
        try:
            broker_process.terminate()
        except:
            pass
        
        sys.exit(result)