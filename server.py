import os
import re
import tempfile
import you_get
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route("/api/download", methods=["GET"])
def download():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro ?url="}), 400

    # Limpia la URL (en caso de que venga con parámetros adicionales)
    url = url.strip().replace(" ", "")
    url = re.sub(r"&(amp;)?utm_.*", "", url)

    try:
        # Crea un archivo temporal para guardar el video descargado
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            # Usa You-Get para descargar el video
            you_get.download(url, output_dir=os.path.dirname(tmp.name))

            # Verifica si el archivo tiene contenido
            if os.path.getsize(tmp.name) == 0:
                return jsonify({"error": "El archivo descargado está vacío (probablemente bloqueo de origen)."}), 502

            # Devuelve el video descargado
            return send_file(
                tmp.name,
                mimetype="video/mp4",
                as_attachment=True,
                download_name="video.mp4"
            )

    except Exception as e:
        return jsonify({"error": f"No se pudo descargar: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
