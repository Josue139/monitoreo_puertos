
import time
import random
import requests
from datetime import datetime, timedelta

URL = "http://influxdb:8086/write?db=ports"

def inject_history():
    print("Inyectando historial de 30 días para pruebas...")
    for i in range(30 * 24): # 30 días, punto por cada hora
        past_time = datetime.utcnow() - timedelta(hours=i)
        timestamp = int(past_time.timestamp()) * 1000000000
        
        for _ in range(3): # 3 puertos por cada hora
            port = random.choice([22, 80, 443, 8002, 8005, 8006, 8080])
            ip = f"192.168.1.{random.randint(1, 254)}"
            val = random.randint(100, 5000)
            line = f"port_requests,port={port},ip={ip} value={val} {timestamp}"
            try:
                requests.post(URL, data=line)
            except:
                pass

def simulate_realtime():
    print("Iniciando simulación en tiempo real...")
    while True:
        port = random.choice([22, 80, 443, 8080] + list(range(8000, 8010)))
        ip = f"192.168.1.{random.randint(1, 254)}"
        val = random.randint(10, 500)
        line = f"port_requests,port={port},ip={ip} value={val}"
        try:
            requests.post(URL, data=line)
        except:
            pass
        time.sleep(1)

if __name__ == "__main__":
    time.sleep(5) # Esperar a que InfluxDB suba
    inject_history()
    simulate_realtime()
