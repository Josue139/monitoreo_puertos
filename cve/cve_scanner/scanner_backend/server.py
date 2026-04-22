from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import subprocess
from drivers_scanner import get_system_summary

app = Flask(__name__)
CORS(app)

# -----------------------------
#  GET /reporte
# -----------------------------
@app.get("/reporte")
def get_reporte():
    ruta = "output/reporte.json"
    if not os.path.exists(ruta):
        return jsonify({"error": "reporte.json no encontrado"}), 404

    with open(ruta, "r") as f:
        data = json.load(f)

    return jsonify(data)

# -----------------------------
#  GET /api/reporte
# -----------------------------
@app.get("/api/reporte")
def api_reporte():
    ruta = "output/reporte.json"
    if not os.path.exists(ruta):
        return jsonify({"error": "reporte.json no encontrado"}), 404

    with open(ruta, "r") as f:
        data = json.load(f)

    return jsonify(data)

# -----------------------------
#  GET /api/drivers
# -----------------------------
@app.get("/api/drivers")
def api_drivers():
    info = get_system_summary()
    return jsonify(info)

# -----------------------------
#  GET /api/historial
# -----------------------------
@app.get("/api/historial")
def api_historial():
    ruta = "output/historial.json"
    if not os.path.exists(ruta):
        return jsonify([])

    with open(ruta, "r") as f:
        data = json.load(f)

    return jsonify(data)

# -----------------------------
#  POST /api/reset
# -----------------------------
@app.post("/api/reset")
def api_reset():
    try:
        if os.path.exists("output/reporte.json"):
            os.remove("output/reporte.json")
        if os.path.exists("output/historial.json"):
            os.remove("output/historial.json")

        return jsonify({"status": "ok", "message": "Archivos eliminados"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------
#  POST /api/scan
# -----------------------------
@app.post("/api/scan")
def api_scan():
    try:
        # Ejecutar scanner.py desde la ruta correcta
        script_path = os.path.join(os.getcwd(), "scanner.py")

        if not os.path.exists(script_path):
            return jsonify({"status": "error", "message": "scanner.py no encontrado"}), 500

        subprocess.run(["python3", script_path], check=True)

        return jsonify({"status": "ok", "message": "Escaneo completado"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"Error ejecutando scanner.py: {e}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------
#  MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)

