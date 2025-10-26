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

            # Eliminar la verificación de tamaño para pruebas
            #if file_size < 1 * 1024 * 1024:  # 1MB como mínimo
            #    return jsonify({"error": "El archivo es demasiado pequeño, probablemente esté incompleto."}), 502

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
