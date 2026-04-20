import os
import platform
import subprocess
from datetime import datetime

def leer_archivo(ruta):
    """Lee un archivo si existe, sino devuelve None."""
    try:
        with open(ruta, "r") as f:
            return f.read().strip()
    except:
        return None


def obtener_kernel_version():
    """Versión del kernel del host (compartido con Docker)."""
    version = leer_archivo("/proc/version")
    if version:
        return version
    return platform.release()


def obtener_modulos_kernel():
    """Lista de módulos del kernel cargados (drivers)."""
    contenido = leer_archivo("/proc/modules")
    if not contenido:
        return []

    modulos = []
    for linea in contenido.split("\n"):
        partes = linea.split()
        if len(partes) >= 1:
            modulos.append(partes[0])  # nombre del módulo
    return modulos


def obtener_interfaces_red():
    """Interfaces de red visibles desde Docker."""
    try:
        return os.listdir("/sys/class/net")
    except:
        return []


def obtener_discos():
    """Dispositivos de bloque visibles."""
    try:
        return os.listdir("/sys/block")
    except:
        return []


def obtener_os_contenedor():
    """Información de la distribución base del contenedor."""
    contenido = leer_archivo("/etc/os-release")
    if not contenido:
        return "Desconocido"

    datos = {}
    for linea in contenido.split("\n"):
        if "=" in linea:
            k, v = linea.split("=", 1)
            datos[k] = v.strip('"')

    return f"{datos.get('NAME', 'Linux')} {datos.get('VERSION', '')}"


def obtener_arquitectura():
    """Arquitectura del sistema."""
    return platform.machine()


def scan_drivers_summary():
    """Escaneo completo de drivers accesibles desde Docker sin root."""
    return {
        "fecha_detectado": datetime.now().isoformat(),
        "kernel_version": obtener_kernel_version(),
        "arquitectura": obtener_arquitectura(),
        "os_contenedor": obtener_os_contenedor(),
        "modulos_kernel": obtener_modulos_kernel(),
        "interfaces_red": obtener_interfaces_red(),
        "discos_detectados": obtener_discos()
    }


if __name__ == "__main__":
    import json
    print(json.dumps(scan_drivers_summary(), indent=4))

