from flask import Flask, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
# Esto elimina CUALQUIER bloqueo de CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api/reporte", methods=["GET"])
def get_reporte():
    ruta = "output/reporte.json"
    if not os.path.exists(ruta):
        return jsonify({"error": "No hay datos aún"}), 404
    with open(ruta, "r") as f:
        return jsonify(json.load(f))

# Asegúrate de tener también las rutas /api/drivers y /api/historial aquí igual que la anterior

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
