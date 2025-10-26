import os
import re
import tempfile
import requests
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

def repackage_video(input_file, output_file):
    """Reempaquetar el video utilizando FFmpeg para asegurar que sea compatible"""
    command = [
        "ffmpeg",
        "-i", input_file,  # Archivo de entrada
        "-c", "copy",      # Copiar sin reencodear
        output_file        # Archivo de salida
    ]
    
    # Capturar los logs de FFmpeg para depuración
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Mostrar el error de FFmpeg si existe
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
    
    # Devolver el estado de FFmpeg
    return result.returncode == 0

@app.route("/api/download", methods=["GET"])
def download():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro ?url="}), 400

    # Limpiar la URL
    url = url.strip().replace(" ", "")
    url = re.sub(r"&(amp;)?utm_.*", "", url)

    try:
        # Realizar la solicitud GET al enlace del video
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            # Crear un archivo temporal para guardar el video
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)

            # Verificar si el archivo tiene contenido
            file_size = os.path.getsize(tmp.name)
            if file_size == 0:
                return jsonify({"error": "El archivo descargado está vacío (probablemente bloqueo de origen)."}), 502

            # Verificar que el archivo tiene un tamaño adecuado
            if file_size < 1 * 1024 * 1024:  # 1MB como mínimo
                return jsonify({"error": "El archivo es demasiado pequeño, probablemente esté incompleto."}), 502

            # Reempaquetar el archivo para asegurarnos de que sea un video válido
            repackage_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            if not repackage_video(tmp.name, repackage_file.name):
                return jsonify({"error": "No se pudo reempaquetar el video correctamente."}), 500

            # Eliminar el archivo temporal original después del reempaquetado
            os.remove(tmp.name)

            # Devolver el archivo MP4 reempaquetado como respuesta al cliente
            return send_file(
                repackage_file.name,
                mimetype="video/mp4",
                as_attachment=True,
                download_name="video.mp4"
            )
        else:
            return jsonify({"error": "No se pudo descargar el video."}), 500
    except Exception as e:
        return jsonify({"error": f"No se pudo descargar: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
