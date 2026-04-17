import scapy.all as scapy
import requests
import time

# URL de InfluxDB - Usamos el nombre del servicio de docker-compose
URL = "http://localhost:8086/write?db=ports"

def process_packet(packet):
    try:
        if packet.haslayer(scapy.IP):
            ip_src = packet[scapy.IP].src
            port = None
            
            # Extraemos el puerto si es TCP o UDP
            if packet.haslayer(scapy.TCP):
                port = packet[scapy.TCP].dport
            elif packet.haslayer(scapy.UDP):
                port = packet[scapy.UDP].dport

            if port:
                # Formato Line Protocol de InfluxDB
                line = f"port_requests,port={port},ip={ip_src} value=1"
                # Aumentamos ligeramente el timeout para evitar descartes
                requests.post(URL, data=line, timeout=1)
    except Exception as e:
        # Quitamos el 'pass' temporalmente para ver si hay errores de conexión en los logs
        print(f"Error enviando a Influx: {e}")

# Esperar a que InfluxDB levante
print("Esperando 10 segundos a InfluxDB...")
time.sleep(10)
print("Sniffer activado: Capturando tráfico real en todas las interfaces...")

# Forzamos la captura. 
# Si esto no funciona, prueba añadiendo el parámetro iface="eth0" (o como se llame tu red)
scapy.sniff(store=False, prn=process_packet)
