import asyncio
from tapo import ApiClient 
from styles.config_logs import LogType
from gui.gui_components import EcoTerminal

async def measure_consumption(data_queue, credentials, stop_event):

    IP_ENCHUFE = credentials['ip']
    EMAIL = credentials['email']
    PASS = credentials['pass']

    """
    IP_ENCHUFE = "10.171.247.148"
    EMAIL = "samuel.gonzalez.ramos.2004@gmail.com"
    PASS = "TPlink115"
    
    """
    client = ApiClient(EMAIL, PASS)
    
    try:
        device = await client.p115(IP_ENCHUFE)
        EcoTerminal.log(f"[ENGINE] Conectado a {IP_ENCHUFE}", LogType.SUCCESS)
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