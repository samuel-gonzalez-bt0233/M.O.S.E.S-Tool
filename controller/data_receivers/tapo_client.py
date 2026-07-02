import asyncio
from tapo import ApiClient 
from styles.config_logs import LogType

async def measure_consumption(data_queue, credentials, stop_event):

    IP_ENCHUFE = credentials['ip']
    EMAIL = credentials['email']
    PASS = credentials['pass']

    client = ApiClient(EMAIL, PASS)
    
    try:
        device = await client.p115(IP_ENCHUFE)
        data_queue.put(f"[ENGINE] Conectado a {IP_ENCHUFE}")
        while not stop_event.is_set():
            try:
                
                usage = await device.get_current_power()
                vatios = usage.current_power
                data_queue.put(vatios)
                
            except Exception as e:
                data_queue.put(f"[ENGINE] Error de lectura: {e}")
            
            await asyncio.sleep(1)

    except Exception as e:
        data_queue.put(f"[ENGINE] Error crítico de conexión: {e}")

import asyncio
import random
import time

async def produce_mock_voltage(queue: asyncio.Queue):
    """
    Corutina asíncrona que simula el flujo continuo del enchufe Tapo.
    Genera lecturas de voltaje y las inyecta en una cola asíncrona cada segundo.
    """
    
    while True:
        # 1. Generamos el voltaje con fluctuación real en torno a 230V
        voltage = round(random.uniform(30.0, 32.0), 1)
        
        
        # 3. Metemos el objeto en la cola de forma asíncrona (no bloqueante)
        queue.put(voltage)
        
        # 4. Nos dormimos exactamente 1 segundo antes de la próxima lectura
        await asyncio.sleep(1)