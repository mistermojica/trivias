import requests
import time
import os
from dotenv import load_dotenv, find_dotenv

# Cargar variables de entorno
load_dotenv(find_dotenv())

META_FB_PAGE_ID = os.environ.get("META_FB_PAGE_ID", "")
META_FB_API_VERSION = os.environ.get("META_FB_API_VERSION", "")
META_USER_ACCESS_TOKEN = os.environ.get("META_USER_ACCESS_TOKEN", "")

# Definir variables globales
api_version = META_FB_API_VERSION  # Por ejemplo, "v12.0"
page_id = META_FB_PAGE_ID  # ID de la página de Facebook
user_access_token = META_USER_ACCESS_TOKEN

def get_page_info():
    url = f"https://graph.facebook.com/{api_version}/{page_id}"
    params = {
        "fields": "name,access_token,instagram_business_account",
        "access_token": user_access_token
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def upload_video_to_ig(ig_user_id, cover_url, page_access_token, video_url, video_type, caption, share_to_feed):
    url = f"https://graph.facebook.com/{api_version}/{ig_user_id}/media"
    params = {
        "media_type": video_type,
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": share_to_feed,
        "cover_url": cover_url,
        "access_token": page_access_token
    }
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def check_video_status(ig_container_id, page_access_token):
    url = f"https://graph.facebook.com/{api_version}/{ig_container_id}"
    params = {
        "fields": "status_code,status",
        "access_token": page_access_token
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def publish_video(ig_user_id, ig_container_id, page_access_token):
    url = f"https://graph.facebook.com/{api_version}/{ig_user_id}/media_publish"
    params = {
        "creation_id": ig_container_id,
        "access_token": page_access_token
    }
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def upload_and_publish_video(video_url, cover_url, video_type="REELS", caption="Follow @luxuryroamers for more!", share_to_feed=True):
    # Obtener la información de la página
    page_info = get_page_info()
    
    if "error" in page_info:
        return {"error": "Error obteniendo la información de la página: " + str(page_info["error"])}

    # Extraer el token de acceso de la página y el ID de la cuenta de Instagram
    page_access_token = page_info["access_token"]
    ig_user_id = page_info["instagram_business_account"]["id"]
    
    # Subir el video a Instagram Reels
    upload_response = upload_video_to_ig(ig_user_id, cover_url, page_access_token, video_url, video_type, caption, share_to_feed)
    
    if "error" in upload_response:
        return {"error": "Error subiendo el video a Instagram: " + str(upload_response["error"])}
    
    ig_container_id = upload_response.get("id")
    
    # Verificar el estado del video subido cada 10 segundos
    while True:
        status_response = check_video_status(ig_container_id, page_access_token)
        
        if "error" in status_response:
            return {"error": "Error verificando el estado del video: " + str(status_response["error"])}
        
        print("Estado del video:", status_response)

        if status_response.get("status_code") == "FINISHED":
            # Publicar el video en Instagram
            publish_response = publish_video(ig_user_id, ig_container_id, page_access_token)
            
            if "error" in publish_response:
                return {"error": "Error publicando el video en Instagram: " + str(publish_response["error"])}
            return {"success": "Video publicado exitosamente en Instagram: " + str(publish_response)}

        time.sleep(10)  # Esperar 10 segundos antes de la siguiente verificación

# Función para invocar desde un programa multi-hilo
def upload_video_thread(video_url, cover_url, video_type, caption, share_to_feed, callback):
    response = upload_and_publish_video(video_url, cover_url, video_type, caption, share_to_feed)
    callback(response)