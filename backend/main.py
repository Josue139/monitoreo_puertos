from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from influxdb import InfluxDBClient
import nmap
import socket
import os

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Clientes externos
client = InfluxDBClient(host='localhost', port=8086, database='ports')
nm = nmap.PortScanner()

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "N/A"

# --- RUTAS DE API ---

@app.get("/api/timeline")
def get_timeline(range: str = "24h"):
    intervals = {"2h": "1m", "6h": "5m", "24h": "30m", "7d": "1h", "30d": "6h"}
    interval = intervals.get(range, "1h")
    query = f'SELECT SUM(value) FROM port_requests WHERE time > now() - {range} GROUP BY time({interval}), port'
    res = client.query(query)
    output = {}
    for series in res.items():
        port = series[0][1]['port']
        output[port] = [{"time": p['time'], "val": p['sum'] or 0} for p in series[1]]
    return output

@app.get("/api/top-ips")
def get_top_ips(port: str = None):
    where_clause = f"WHERE time > now() - 24h AND port = '{port}'" if port else "WHERE time > now() - 24h"
    query = f'SELECT SUM(value) FROM port_requests {where_clause} GROUP BY ip, port'
    result = client.query(query)
    ips_data = []
    for series in result.items():
        points = list(series[1])
        ip = series[0][1]['ip']
        ips_data.append({
            "ip": ip,
            "hostname": get_hostname(ip),
            "port": series[0][1]['port'],
            "count": int(sum(p['sum'] for p in points if p['sum'])),
            "last_activity": points[-1]['time'] if points else None
        })
    return sorted(ips_data, key=lambda x: x['count'], reverse=True)[:15]

@app.get("/api/scan-target")
def scan_target(ip: str):
    try:
        target_clean = str(ip).strip()
        nm.scan(hosts=target_clean, arguments='-sV -T4')
        results = []
        if target_clean in nm.all_hosts():
            for proto in nm[target_clean].all_protocols():
                for port in nm[target_clean][proto].keys():
                    service = nm[target_clean][proto][port]
                    banner = f"{service.get('name', 'unknown')} {service.get('product', '')}"
                    results.append({"port": int(port), "banner": banner.strip(), "state": service.get('state', 'unknown')})
        return results if results else {"info": f"No services in {target_clean}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/scan-self")
def scan_self():
    try:
        target = "0.0.0.0" 
        nm.scan(hosts=target, arguments='-p 22,80,3000,8000,8086 -sV')
        results = []
        host_key = nm.all_hosts()[0] if nm.all_hosts() else target
        if host_key in nm.all_hosts():
            for proto in nm[host_key].all_protocols():
                for port in nm[host_key][proto].keys():
                    service = nm[host_key][proto][port]
                    banner = f"{service.get('name', '')} {service.get('product', '')}"
                    results.append({"port": port, "banner": banner.strip() or "Servicio Activo", "state": service.get('state', 'open')})
        return results
    except Exception as e:
        return {"error": str(e)}

# --- EL CORRECAMINOS: SERVIDO DE FRONTEND ---

# 1. Montamos la carpeta interna de React. 
# Esto resuelve el error de MIME type (JS/CSS)
if os.path.exists("static/static"):
    app.mount("/static", StaticFiles(directory="static/static"), name="static")

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    # Ignorar llamadas a la API
    if full_path.startswith("api"):
        return {"error": "API route not found"}
    
    # Construir ruta al archivo físico en la carpeta 'static'
    file_path = os.path.join("static", full_path)
    
    # Si el archivo existe (favicon, manifest, etc.), enviarlo
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Para todo lo demás (la ruta base /), enviar el index.html
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "No se encontró el build del frontend en la carpeta static."}
