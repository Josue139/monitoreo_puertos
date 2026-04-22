from drivers_scanner import scan_drivers_summary   # ← IMPORT CORRECTO

import subprocess
import xml.etree.ElementTree as ET
import requests
import json
import os
from datetime import datetime
import sys

API_NVD = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch="

# ============================================================
#  NUEVAS FUNCIONES (NO ROMPEN NADA)
# ============================================================

def get_installed_libraries():
    libs = []
    try:
        for root, dirs, files in os.walk("/usr/lib"):
            for f in files:
                if f.endswith(".so") or ".so." in f:
                    libs.append(f)
    except:
        pass
    return sorted(list(set(libs)))


def get_network_interfaces():
    try:
        return os.listdir("/sys/class/net")
    except:
        return []


def get_disks():
    try:
        return os.listdir("/sys/block")
    except:
        return []


def get_kernel_modules():
    try:
        return os.listdir("/sys/module")
    except:
        return []


# ============================================================
#  FILTROS CVE
# ============================================================
def severidad_valida(score, minimo=4.0):
    return score >= minimo

def cve_reciente(cve_id, minimo=2015):
    try:
        año = int(cve_id.split("-")[1])
        return año >= minimo
    except:
        return True


# ============================================================
#  APT
# ============================================================
def scan_apt_vulnerabilities():
    vulnerables = []

    try:
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True,
            text=True
        )
        lineas = result.stdout.splitlines()

        for linea in lineas:
            if "security" in linea.lower():
                vulnerables.append(linea.strip())

    except Exception as e:
        vulnerables.append(f"Error al ejecutar APT: {e}")

    return vulnerables


# ============================================================
#  NMAP
# ============================================================
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


# ============================================================
#  CONSULTA CVE
# ============================================================
def consultar_cve(nombre, version):
    if not version:
        return []

    query = f"{nombre} {version}"
    url = API_NVD + query

    print(f"Buscando CVEs para: {query}")

    try:
        r = requests.get(url, timeout=10)
    except:
        return []

    if r.status_code != 200:
        return []

    try:
        data = r.json()
    except:
        return []

    return data.get("vulnerabilities", [])


def consultar_cve_keyword(query):
    url = API_NVD + query
    print(f"Buscando CVEs por keyword: {query}")

    try:
        r = requests.get(url, timeout=10)
    except:
        return []

    if r.status_code != 200:
        return []

    try:
        data = r.json()
    except:
        return []

    return data.get("vulnerabilities", [])


# ============================================================
#  PROCESAR CVE
# ============================================================
def procesar_items_cve_en_reporte(items, libreria, version, origen, reporte):
    for item in items:
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

        sugerencia = (
            f"Aplicar actualización recomendada: {fix}"
            if fix != "No disponible"
            else "Revisar documentación oficial del proveedor."
        )

        reporte.append({
            "cve": cve_id,
            "libreria": libreria,
            "version": version,
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
            "origen": origen,
            "enlace": enlace
        })


# ============================================================
#  REPORTES
# ============================================================
def generar_reporte(resultados, ip, drivers_info, apt_vulnerables,
                    interfaces, discos, modulos, librerias):

    os.makedirs("output", exist_ok=True)

    reporte_final = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_escaneada": ip,
        "total_cves": len(resultados),
        "vulnerabilidades": resultados,
        "drivers": drivers_info,
        "paquetes_vulnerables": apt_vulnerables,

        # NUEVOS CAMPOS
        "interfaces_red": interfaces,
        "discos_detectados": discos,
        "modulos_kernel": modulos,
        "librerias_detectadas": librerias
    }

    with open("output/reporte.json", "w") as f:
        json.dump(reporte_final, f, indent=4)

    print("📄 Reporte JSON generado")


# ============================================================
#  MAIN
# ============================================================
def main():
    ip = sys.argv[1] if len(sys.argv) > 1 else "host.docker.internal"

    print(f"📌 Escaneando la IP: {ip}")

    # -------------------------------
    # NMAP
    # -------------------------------
    xml = ejecutar_nmap(ip)
    servicios = extraer_servicios(xml)

    reporte = []

    for s in servicios:
        cves = consultar_cve(s["nombre"], s["version"])
        procesar_items_cve_en_reporte(
            cves, s["nombre"], s["version"], "servicio", reporte
        )

    # -------------------------------
    # DRIVERS + KERNEL
    # -------------------------------
    drivers_info = scan_drivers_summary()
    kernel_version = drivers_info["kernel_version"]

    if kernel_version:
        base_version = kernel_version.split("-")[0]
        query_kernel = f"linux kernel {base_version}"
        cves_kernel = consultar_cve_keyword(query_kernel)
        procesar_items_cve_en_reporte(
            cves_kernel, "kernel", kernel_version, "kernel", reporte
        )

    # -------------------------------
    # MÓDULOS REALES
    # -------------------------------
    modulos_reales = drivers_info["modulos_kernel"]

    for modulo in modulos_reales:
        cves_mod = consultar_cve_keyword(modulo)
        procesar_items_cve_en_reporte(
            cves_mod, modulo, "N/A", "modulo", reporte
        )

    # -------------------------------
    # CPU / BIOS / UEFI (básico)
    # -------------------------------
    procesar_items_cve_en_reporte(
        consultar_cve_keyword("intel cpu"),
        "intel_cpu", "N/A", "cpu", reporte
    )

    procesar_items_cve_en_reporte(
        consultar_cve_keyword("amd cpu"),
        "amd_cpu", "N/A", "cpu", reporte
    )

    procesar_items_cve_en_reporte(
        consultar_cve_keyword("uefi"),
        "uefi", "N/A", "firmware", reporte
    )

    procesar_items_cve_en_reporte(
        consultar_cve_keyword("bios"),
        "bios", "N/A", "bios", reporte
    )

    # -------------------------------
    # APT
    # -------------------------------
    apt_vulnerables = scan_apt_vulnerabilities()

    for pkg in apt_vulnerables:
        partes = pkg.split()
        nombre = partes[0].split("/")[0] if len(partes) > 0 else "desconocido"
        version_nueva = partes[1] if len(partes) > 1 else "desconocida"

        reporte.append({
            "cve": "APT-SECURITY",
            "libreria": nombre,
            "version": version_nueva,
            "score": 5.0,
            "severidad": "MEDIUM",
            "fecha_publicacion": "desconocida",
            "fecha_detectado": datetime.now().isoformat(timespec="seconds"),
            "descripcion": "Actualización de seguridad disponible para este paquete.",
            "vector": "LOCAL",
            "impacto": {
                "confidencialidad": "LOW",
                "integridad": "LOW",
                "disponibilidad": "LOW"
            },
            "fix": f"Actualizar paquete: {nombre}",
            "sugerencia": "Ejecutar apt upgrade para aplicar parches de seguridad.",
            "driver": None,
            "origen": "apt",
            "enlace": f"https://packages.debian.org/search?keywords={nombre}"
        })

    # -------------------------------
    # ORDENAR
    # -------------------------------
    reporte.sort(
        key=lambda x: (
            0 if x["origen"] == "apt" else 1,
            -x.get("score", 0)
        )
    )

    # -------------------------------
    # NUEVOS DATOS DEL HOST
    # -------------------------------
    interfaces = get_network_interfaces()
    discos = get_disks()
    modulos = get_kernel_modules()
    librerias = get_installed_libraries()

    # -------------------------------
    # GUARDAR REPORTE
    # -------------------------------
    generar_reporte(
        reporte, ip, drivers_info, apt_vulnerables,
        interfaces, discos, modulos, librerias
    )

    # -------------------------------
    # HISTORIAL
    # -------------------------------
    historial_path = "output/historial.json"

    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "total": len(reporte)
    }

    if os.path.exists(historial_path):
        try:
            with open(historial_path, "r") as f:
                historial = json.load(f)
        except:
            historial = []
    else:
        historial = []

    historial.append(entrada)

    with open(historial_path, "w") as f:
        json.dump(historial, f, indent=4)

    print("📄 Historial actualizado")


if __name__ == "__main__":
    main()

