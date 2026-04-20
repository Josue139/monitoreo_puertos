import subprocess
import xml.etree.ElementTree as ET
import requests
import json
import os
from datetime import datetime
import csv
import sys

API_NVD = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch="

def severidad_valida(score, minimo=4.0):
    return score >= minimo

def cve_reciente(cve_id, minimo=2015):
    try:
        año = int(cve_id.split("-")[1])
        return año >= minimo
    except:
        return True

def ejecutar_nmap(ip):
    print(f"Escaneando puertos de {ip}...")

    try:
        resultado = subprocess.run(
            ["nmap", "-sV", "-p0-1024,8000-8999", ip, "-oX", "resultado.xml"],
            capture_output=True,
            text=True,
            timeout=120
        )
    except subprocess.TimeoutExpired:
        print("❌ Error: Nmap tardó demasiado y fue cancelado.")
        return None
    except Exception as e:
        print(f"❌ Error ejecutando Nmap: {e}")
        return None

    if resultado.returncode != 0:
        print("❌ Nmap no pudo completar el escaneo.")
        return None

    return "resultado.xml"

def extraer_servicios(xml_file):
    if xml_file is None:
        return []

    try:
        tree = ET.parse(xml_file)
    except:
        print("❌ Error leyendo el archivo XML de Nmap.")
        return []

    root = tree.getroot()
    servicios = []
    vistos = set()

    for port in root.iter("port"):
        service = port.find("service")
        if service is None:
            continue

        nombre = service.get("name")
        version = service.get("version")

        if not nombre or not version:
            continue

        clave = f"{nombre}-{version}"
        if clave in vistos:
            continue

        vistos.add(clave)

        servicios.append({
            "nombre": nombre,
            "version": version
        })

    return servicios

def consultar_cve(nombre, version):
    if not version:
        return []

    query = f"{nombre} {version}"
    url = API_NVD + query

    print(f"Buscando CVEs para: {query}")

    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        print("❌ Error: No hay conexión a internet.")
        return []
    except requests.exceptions.Timeout:
        print("❌ Error: La API tardó demasiado en responder.")
        return []
    except Exception as e:
        print(f"❌ Error consultando la API: {e}")
        return []

    if r.status_code != 200:
        print(f"❌ Error: La API devolvió código {r.status_code}")
        return []

    try:
        data = r.json()
    except:
        print("❌ Error: La API devolvió datos inválidos.")
        return []

    return data.get("vulnerabilities", [])

def clasificar_cvss(score):
    if score <= 3.9:
        return "leve"
    elif score <= 6.9:
        return "grave"
    elif score <= 8.9:
        return "muy-grave"
    else:
        return "prioridad"

def generar_reporte(resultados, ip):
    os.makedirs("output", exist_ok=True)

    reporte_final = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_escaneada": ip,
        "total_cves": len(resultados),
        "vulnerabilidades": resultados
    }

    with open("output/reporte.json", "w") as f:
        json.dump(reporte_final, f, indent=4)

    with open("output/reporte.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CVE", "Librería", "Enlace", "Peligrosidad"])
        for r in resultados:
            writer.writerow([r["CVE"], r["libreria"], r["enlace"], r["peligrosidad"]])

    print("📄 Reportes generados: JSON y CSV")

def generar_reporte_html(resultados, ip):
    os.makedirs("output", exist_ok=True)

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Vulnerabilidades</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 10px;
                border: 1px solid #ccc;
                text-align: left;
            }}
            th {{
                background-color: #333;
                color: white;
            }}
            .leve {{
                background-color: #b3ffb3;
            }}
            .grave {{
                background-color: #ffe680;
            }}
            .muy-grave {{
                background-color: #ffb366;
            }}
            .prioridad {{
                background-color: #ff6666;
            }}
        </style>
    </head>
    <body>
        <h1>Reporte de Vulnerabilidades</h1>
        <p><strong>IP escaneada:</strong> {ip}</p>
        <p><strong>Total de CVEs:</strong> {len(resultados)}</p>

        <table>
            <tr>
                <th>CVE</th>
                <th>Librería</th>
                <th>Enlace</th>
                <th>Peligrosidad</th>
            </tr>
    """

    for r in resultados:
        html += f"""
            <tr class="{r['peligrosidad']}">
                <td>{r['CVE']}</td>
                <td>{r['libreria']}</td>
                <td><a href="{r['enlace']}">Ver CVE</a></td>
                <td>{r['peligrosidad']}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    with open("output/reporte.html", "w") as f:
        f.write(html)

    print("📄 Reporte HTML generado: output/reporte.html")


def main():
    # Si el usuario pasa una IP por parámetro, la usamos
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        # Si no pasa nada, usamos tu IP actual
        ip = "10.124.163.168"

    print(f"📌 Escaneando la IP: {ip}")

    xml = ejecutar_nmap(ip)
    servicios = extraer_servicios(xml)

    reporte = []

    for s in servicios:
        cves = consultar_cve(s["nombre"], s["version"])
        for item in cves:
            cve_id = item["cve"]["id"]

            if not cve_reciente(cve_id):
                continue

            enlace = f"https://www.cve.org/CVERecord?id={cve_id}"

            try:
                score = item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"]
            except:
                score = 0

            if not severidad_valida(score):
                continue

            categoria = clasificar_cvss(score)

            reporte.append({
                "CVE": cve_id,
                "libreria": s["nombre"],
                "enlace": enlace,
                "peligrosidad": categoria
            })

    print("DEBUG - Contenido de reporte:")
    print(reporte)

    generar_reporte(reporte, ip)
    generar_reporte_html(reporte, ip)



if __name__ == "__main__":
    main()

