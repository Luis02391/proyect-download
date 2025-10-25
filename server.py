from flask import Flask, request, jsonify
import yt_dlp
import re
import os  # ✅ necesario para Render

app = Flask(__name__)

# ✅ habilita CORS por si lo llamas desde el Atajo o navegador
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "API Universal Descargador HD lista 🚀",
        "usage": "/api/download?url=https://..."
    })


@app.route("/api/download", methods=["GET"])
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Falta el parámetro ?url="}), 400

    # 🔹 Limpia el enlace (por si viene con espacios o basura)
    url = url.strip().replace(" ", "")
    url = re.sub(r"&?(amp;)?utm_.*", "", url)

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

            # Extrae datos útiles
            title = info.get("title", "Video")
            thumbnail = info.get("thumbnail", "")
            ext = info.get("ext", "mp4")

            # 🔹 Encuentra la mejor URL directa posible
            direct_url = info.get("url")
            if not direct_url and "formats" in info:
                best = max(info["formats"], key=lambda f: f.get("height", 0) or 0)
                direct_url = best.get("url")

            if not direct_url:
                return jsonify({"error": "No se pudo obtener un enlace directo."}), 500

            return jsonify({
                "status": "success",
                "title": title,
                "extension": ext,
                "thumbnail": thumbnail,
                "directUrl": direct_url
            })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": f"No se pudo procesar el enlace: {str(e)}"}), 500


if __name__ == "__main__":
    # 🔹 Render necesita usar el puerto dinámico asignado
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
