import requests

def descargar_video(url, api_key):
    endpoint = "https://fastsaverapi.com/api/v1/download"
    params = {
        "url": url,
        "api_key": api_key
    }
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success":
            video_url = data["data"]["video"]
            video_response = requests.get(video_url)
            if video_response.status_code == 200:
                with open("video_descargado.mp4", "wb") as f:
                    f.write(video_response.content)
                print("¡Descarga completada con éxito!")
            else:
                print("Error al descargar el video.")
        else:
            print(f"Error: {data['message']}")
    else:
        print("Error al contactar la API.")

# Ejemplo de uso
url_video = "https://www.youtube.com/watch?v=ejemplo"
api_key = "tu_api_key_aqui"
descargar_video(url_video, api_key)
