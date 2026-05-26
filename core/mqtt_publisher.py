import json
import threading
import paho.mqtt.publish as publish
from PyQt6.QtCore import QObject, pyqtSignal


class MqttPublisher(QObject):
    ack = pyqtSignal(bool)

    def send_early_stopping_signal(self):
        threading.Thread(target=self.publish_signal, daemon=True).start()

    def publish_signal(self):
        try:
            publish.single(
                "training/stopping",
                payload=json.dumps(0),
                hostname="localhost",
                port=1883,
                qos=1
            )
            self.ack.emit(True)
        except Exception:
            self.ack.emit(False)
