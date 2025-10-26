from fastapi import FastAPI, HTTPException
import requests
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

# Ruta para descargar el video
@app.get("/descargar_video")
async def descargar_video(url: str, api_key: str):
    # Endpoint de la API FastSaver
    endpoint = "https://fastsaverapi.com/api/v1/download"
    params = {
        "url": url,
        "api_key": api_key
    }

    # Hacer la solicitud GET al servicio de FastSaverAPI
    response = requests.get(endpoint, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al contactar la API de descarga.")

    # Procesamos la respuesta JSON para obtener el enlace del video
    data = response.json()
    if data["status"] != "success":
        raise HTTPException(status_code=400, detail=f"Error en la API: {data['message']}")

    video_url = data["data"]["video"]

    # Solicitar el video
    video_response = requests.get(video_url)

    if video_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al descargar el video.")

    # Devolver el video como respuesta en formato binario
    video_bytes = BytesIO(video_response.content)
    return StreamingResponse(video_bytes, media_type="video/mp4")

# Para correr el servidor de FastAPI, usa el siguiente comando:
# uvicorn nombre_del_archivo:app --reload
