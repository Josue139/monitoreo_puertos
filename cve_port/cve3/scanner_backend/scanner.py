from drivers_scanner import scan_drivers_summary

import subprocess
import xml.etree.ElementTree as ET
import requests
import json
import os
from datetime import datetime
import csv
import sys

API_NVD = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch="

# 🔥 NUEVO: función para guardar historial
def guardar_historial(total):
    ruta = "output/historial.json"

    # Crear archivo si no existe
    if not os.path.exists(ruta):
        with open(ruta, "w") as f:
            json.dump([], f)

    # Leer historial existente
    with open(ruta, "r") as f:
        historial = json.load(f)

    # Agregar nuevo registro
    historial.append({
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "total": total
    })

    # Guardar historial actualizado
    with open(ruta, "w") as f:
        json.dump(historial, f, indent=2)


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
            ["nmap", "-sV", "-p-", ip, "-oX", "resultado.xml"],
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
        return "LOW"
    elif score <= 6.9:
        return "MEDIUM"
    elif score <= 8.9:
        return "HIGH"
    else:
        return "CRITICAL"

def generar_reporte(resultados, ip, drivers_info):
    os.makedirs("output", exist_ok=True)

    reporte_final = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_escaneada": ip,
        "total_cves": len(resultados),
        "vulnerabilidades": resultados,
        "drivers": drivers_info
    }

    with open("output/reporte.json", "w") as f:
        json.dump(reporte_final, f, indent=4)

    with open("output/reporte.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "CVE", "Librería", "Versión", "Score", "Severidad",
            "Fecha publicación", "Fecha detectado",
            "Vector", "Confidencialidad", "Integridad", "Disponibilidad",
            "Fix", "Sugerencia", "Origen", "Enlace"
        ])
        for r in resultados:
            writer.writerow([
                r["cve"],
                r["libreria"],
                r["version"],
                r["score"],
                r["severidad"],
                r["fecha_publicacion"],
                r["fecha_detectado"],
                r["vector"],
                r["impacto"]["confidencialidad"],
                r["impacto"]["integridad"],
                r["impacto"]["disponibilidad"],
                r["fix"],
                r["sugerencia"],
                r["origen"],
                r["enlace"]
            ])

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
                padding: 8px;
                border: 1px solid #ccc;
                text-align: left;
                font-size: 12px;
            }}
            th {{
                background-color: #333;
                color: white;
            }}
            .LOW {{
                background-color: #b3ffb3;
            }}
            .MEDIUM {{
                background-color: #ffe680;
            }}
            .HIGH {{
                background-color: #ffb366;
            }}
            .CRITICAL {{
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
                <th>Versión</th>
                <th>Score</th>
                <th>Severidad</th>
                <th>Fecha publ.</th>
                <th>Fecha detectado</th>
                <th>Vector</th>
                <th>C</th>
                <th>I</th>
                <th>A</th>
                <th>Fix</th>
                <th>Sugerencia</th>
                <th>Origen</th>
                <th>Enlace</th>
            </tr>
    """

    for r in resultados:
        html += f"""
            <tr class="{r['severidad']}">
                <td>{r['cve']}</td>
                <td>{r['libreria']}</td>
                <td>{r['version']}</td>
                <td>{r['score']}</td>
                <td>{r['severidad']}</td>
                <td>{r['fecha_publicacion']}</td>
                <td>{r['fecha_detectado']}</td>
                <td>{r['vector']}</td>
                <td>{r['impacto']['confidencialidad']}</td>
                <td>{r['impacto']['integridad']}</td>
                <td>{r['impacto']['disponibilidad']}</td>
                <td>{r['fix']}</td>
                <td>{r['sugerencia']}</td>
                <td>{r['origen']}</td>
                <td><a href="{r['enlace']}">Ver CVE</a></td>
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
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = "host.docker.internal"

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
                categoria = item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseSeverity"]
            except:
                score = 0
                categoria = "UNKNOWN"

            if not severidad_valida(score):
                continue

            try:
                fecha_publicacion = item["cve"]["published"].split("T")[0]
            except:
                fecha_publicacion = "desconocida"

            try:
                descripcion = item["cve"]["descriptions"][0]["value"]
            except:
                descripcion = "Descripción no disponible"

            try:
                vector = item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"]
            except:
                vector = "No disponible"

            try:
                impacto_conf = item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["confidentialityImpact"]
                impacto_int = item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["integrityImpact"]
                impacto_disp = item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["availabilityImpact"]
            except:
                impacto_conf = impacto_int = impacto_disp = "UNKNOWN"

            fix = "No disponible"
            try:
                for node in item["cve"]["configurations"]["nodes"]:
                    for match in node.get("cpeMatch", []):
                        if "versionEndExcluding" in match:
                            fix = f"Actualizar a versión {match['versionEndExcluding']}"
            except:
                pass

            if fix != "No disponible":
                sugerencia = f"Aplicar actualización recomendada: {fix}"
            else:
                sugerencia = "Revisar documentación oficial del proveedor para mitigaciones."

            vulnerabilidad = {
                "cve": cve_id,
                "libreria": s["nombre"],
                "version": s["version"],
                "score": score,
                "severidad": categoria,
                "fecha_publicacion": fecha_publicacion,
                "fecha_detectado": datetime.now().isoformat(timespec="seconds"),
                "descripcion": descripcion,
                "vector": vector,
                "impacto": {
                    "confidencialidad": impacto_conf,
                    "integridad": impacto_int,
                    "disponibilidad": impacto_disp
                },
                "fix": fix,
                "sugerencia": sugerencia,
                "driver": None,
                "origen": "servicio",
                "enlace": enlace
            }

            reporte.append(vulnerabilidad)

    print("DEBUG - Contenido de reporte:")
    print(reporte)

    try:
        reporte.sort(key=lambda x: x.get("score", 0), reverse=True)
    except Exception as e:
        print(f"⚠️ No se pudo ordenar el reporte: {e}")

    print("📌 Escaneando información del sistema (drivers/kernel)...")
    drivers_info = scan_drivers_summary()

    generar_reporte(reporte, ip, drivers_info)
    generar_reporte_html(reporte, ip)

    # 🔥 NUEVO: guardar historial de vulnerabilidades detectadas
    guardar_historial(len(reporte))


if __name__ == "__main__":
    main()

