import os
import re
import tempfile
import yt_dlp
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route("/api/direct", methods=["GET"])
def api_direct():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro ?url="}), 400

    url = url.strip().replace(" ", "")
    url = re.sub(r"&(amp;)?utm_.*", "", url)

    try:
        # Crea un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            ydl_opts = {
                "quiet": True,
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": tmp.name,
                "noplaylist": True,
                "retries": 3,
                "source_address": "0.0.0.0",
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Referer": "https://www.tiktok.com/",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                # Impersonar como un navegador válido (usar la configuración de 'impersonate')
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferredformat": "mp4",
                }],
                "extractor_args": {
                    "tiktok": ["--impersonate", "chrome"]
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

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
