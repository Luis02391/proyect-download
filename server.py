from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import re

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "🎬 API Universal Descargador HD lista 🚀",
        "usage": {
            "json_mode": "/api/download?url=https://...",
            "direct_mode": "/api/direct?url=https://..."
        }
    })

# -------------------------
# 🔹 MODO 1: Devuelve JSON con info y directUrl
# -------------------------
@app.route("/api/download", methods=["GET"])
def api_download():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro ?url="}), 400

    # Limpia la URL
    url = url.strip().replace(" ", "")
    url = re.sub(r"&(amp;)?utm_.*", "", url)

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            title = info.get("title", "Video")
            thumbnail = info.get("thumbnail", "")
            ext = info.get("ext", "mp4")
            direct_url = info.get("url")

            # Si no tiene url directa, busca la mejor
            if not direct_url and "formats" in info:
                best = max(info["formats"], key=lambda f: f.get("height", 0))
                direct_url = best.get("url")

            if not direct_url:
                return jsonify({"error": "No se pudo obtener el enlace directo."}), 500

            return jsonify({
                "status": "success",
                "title": title,
                "extension": ext,
                "thumbnail": thumbnail,
                "directUrl": direct_url
            })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"No se pudo procesar el enlace: {str(e)}"}), 500


# -------------------------
# 🔹 MODO 2: Descarga y entrega el MP4 directamente
# -------------------------
@app.route("/api/direct", methods=["GET"])
def api_direct():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro ?url="}), 400

    # Limpia URL
    url = url.strip().replace(" ", "")
    url = re.sub(r"&(amp;)?utm_.*", "", url)

    try:
        # Archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            ydl_opts = {
                "quiet": True,
                "outtmpl": tmp.name,
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return send_file(
                tmp.name,
                mimetype="video/mp4",
                as_attachment=True,
                download_name="video.mp4"
            )

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"No se pudo descargar: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
