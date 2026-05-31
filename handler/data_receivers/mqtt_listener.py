import json

import paho.mqtt.client as mqtt
from styles.config_logs import LogType
from core.metrics_dto import MetricsDto
from gui.gui_components import EcoTerminal


def on_connect(client, window, flags, rc):
    if rc == 0:
        window.terminal.log(f"RECEPTOR: Conectado al broker local.", LogType.SUCCESS)
        client.subscribe("training/metrics")
        window.terminal.log(f"RECEPTOR: Suscrito al topic.", LogType.SUCCESS)
    else:
        window.terminal.log(f"RECEPTOR: Error en la conexión. Código {rc}.", LogType.ERROR)


def on_message(client, window, msg):
    try:
        payload = msg.payload.decode()
        print(payload)
        dto = MetricsDto(**json.loads(payload))

        window.new_training_metrics.emit(dto)

    except Exception as e:
        window.terminal.log(f"RECEPTOR: Error al procesar mensaje: {e}", LogType.ERROR)


def init_mqtt_listener(window):
    client = mqtt.Client(userdata=window)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        window.terminal.log(f"RECEPTOR: Conectando al broker local.", LogType.DEBUG)
        client.connect("localhost", 1883, 60)

        client.loop_forever()
    except Exception as e:
        window.terminal.log(f"RECEPTOR: No se pudo conectar al broker: {e}", LogType.WARNING)
