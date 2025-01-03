import asyncio
import os
import requests
import json
import webbrowser
import time
import random
from openai import OpenAI
from trivia import create_video_main, generate_trivias
from ig_uploader import upload_video_thread
import uuid
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory, render_template_string
from flask_socketio import SocketIO
from loguru import logger
from PIL import Image
from datetime import datetime, timezone
from tinydb import TinyDB, Query

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)

import builtins

original_print = print
def omprint(*args, **kwargs):
    logger.info(" ".join(map(str, args)))
    original_print(*args, **kwargs)

# builtins.print = omprint #OM

PUBLIC_FOLDER = 'public'

PORT = os.environ.get("PORT", "")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

openai = OpenAI()

openai.api_key = OPENAI_API_KEY

# Definir script_dir como una variable global
SCRIPT_DIR = os.path.dirname(__file__)

async def download_image(url, download_path, filename):
    img_name = os.path.join(download_path, str(filename) + os.path.splitext(os.path.basename(url))[1])

    with open(img_name, 'wb') as f:
        f.write(requests.get(url).content)

    print(f'Descargada: {img_name}')
    return url  # Retornar la URL de la imagen descargada

def clear_directory(directory_path):
    # Elimina todos los archivos en la carpeta especificada.
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f'Eliminada: {file_path}')
            except Exception as e:
                print(f'Error al eliminar {file_path}: {e}')



async def download_images(selected_images, download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    filename = 0
    for image in selected_images:
        filename = filename + 1
        img_downloaded = await download_image(image["url"], download_path, filename)
        print("Imagen descargada:", img_downloaded)


def send_vehicle_data_to_instagram(ctx):
    # Extraer los valores del objeto ctx
    vehDueno = ctx.get("vehDueno", "Unknown Owner")
    arrFotosVehiculos = ctx.get("arrFotosVehiculos", [])
    vehMarca = ctx.get("vehMarca", "Unknown Brand")
    vehModelo = ctx.get("vehModelo", "Unknown Model")
    vehAnoFabricacion = ctx.get("vehAnoFabricacion", 0)
    vehTipoVehiculo = ctx.get("vehTipoVehiculo", "Unknown Type")
    vehColor = ctx.get("vehColor", "Unknown Color")
    vehTipoEmision = ctx.get("vehTipoEmision", "Unknown Fuel")
    vehLocation = ctx.get("vehLocation", "Unknown Location")

    # Construir el cuerpo de la solicitud
    data = {
        "dueno": vehDueno,
        "to": "instagram",
        "images": arrFotosVehiculos,
        "caption": f"{vehMarca} {vehModelo} {vehAnoFabricacion}\r\nTipo: {vehTipoVehiculo}\r\nColor: {vehColor}\r\nCombustible: {vehTipoEmision}\r\nPrecio: ${random.randint(10000, 40000)}",
        "location": vehLocation,
        "year": vehAnoFabricacion,
        "brand": vehMarca,
        "model": vehModelo,
        "show": True
    }

    print(data)

    # Realizar la solicitud POST
    response = requests.post("http://localhost:3002/publish", json=data)

    # Comprobar el estado de la respuesta
    if response.status_code == 200:
        print("Solicitud enviada con éxito.")
    else:
        print(f"Error al enviar la solicitud: {response.status_code}")
        print(response.text)


def upload_video(video_url, cover_url, property_name):
    # video_url = "https://videos.pexels.com/video-files/10780729/10780729-hd_1080_1920_30fps.mp4"
    video_type = "REELS"
    caption = f"{property_name}\n\nFollow @luxuryroamers for more!!!\n\n#luxuryroamers #luxuryhomes #luxuryproperties #luxurytravelers"
    share_to_feed = True

    def callback(response):
        print(response)

    # Crear y empezar el hilo
    thread = threading.Thread(target=upload_video_thread, args=(video_url, cover_url, video_type, caption, share_to_feed, callback))
    thread.start()


def run_http_server(port, directory):
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    os.chdir(directory)
    httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
    httpd.serve_forever()

async def create_video_local(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, socketio):
    # Registrar el tiempo de inicio
    start_time = time.time()
    
    print("[DEBUG 03]: ====================\n", "create_video_local -> socketio", socketio, "\====================")

    # Iniciar el servidor HTTP en un hilo separado
    directory = f'./{PUBLIC_FOLDER}'

    # url = 'https://www.trulia.com/home/282-s-95th-pl-chandler-az-85224-8207993?mid=0#lil-mediaTab'
    # url = 'https://www.trulia.com/builder-community-plan/Prestwick-Place-Huxley-2059141968?mid=0#lil-mediaTab'
    # url = 'https://www.kayak.com/hotels/The-Ritz-Carlton,San-Francisco,San-Francisco-p61403-h61201-details/2024-07-12/2024-07-19/2adults?psid=lBCEPnMis_&pm=daytaxes'
    # url = 'https://www.es.kayak.com/hotels/Villa-Gordal,Enormous-Villa-in-Las-Vegas-with-39-Sleeps,Las-Vegas-p61746-h3989982-details/2024-07-26/2024-07-31/2adults?psid=mRCEN4ta-l&pm=daybase'

    download_path = f'{directory}/{uuid4}'

    # Llamar a la función para borrar el contenido de la carpeta
    clear_directory(download_path)

    create_video_main(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, socketio)

    # send_vehicle_data_to_instagram(ctx)

    server_url = f"https://trivias.luxuryroamers.com"
    video_to_upload = f'{server_url}/generados/videos/{uuid4}.mp4'
    cover_url = f'{server_url}/{uuid4}/thumbnail/{uuid4}.jpg'

    print("video_to_upload:", video_to_upload)

    # upload_video(video_to_upload, cover_url, property_name)

    # Registrar el tiempo de finalización
    end_time = time.time()

    # Calcular el tiempo de ejecución
    execution_time = end_time - start_time

    print(f"El script tomó {execution_time:.2f} segundos en ejecutarse.")

    return {"execution_time": execution_time}


app = Flask(__name__, static_folder=PUBLIC_FOLDER)
socketio = SocketIO(app)

# Initialize TinyDB
db = TinyDB('luxuryroamers.json')
procesos_table = db.table('procesos')

process_lock = threading.Lock()


def save_to_db(process_id, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID):
    timestamp = datetime.now(timezone.utc).isoformat()
    proceso = {
        "uuid": process_id,
        "language": language,
        "voice": voice,
        "main_question": main_question,
        "num_questions": num_questions,
        "num_options": num_options,
        "background_music": background_music,
        "background_video": background_video,
        "logo_path": logo_path,
        "account_text": account_text,
        "sessionUUID": sessionUUID,
        "fecha_creacion": timestamp,
        "fecha_modificacion": timestamp,
        "estado": "pendiente"
    }
    procesos_table.insert(proceso)
    return process_id


def update_process_status(process_id, status):
    url_video = f'https://trivias.luxuryroamers.com/generados/videos/{process_id}.mp4'
    Process = Query()
    procesos_table.update(
        {
            "estado": status, 
            "fecha_modificacion": datetime.now(timezone.utc).isoformat(),
            "url_video": url_video
        }, Process.uuid == process_id)


def delete_process(process_id):
    Process = Query()
    procesos_table.remove(Process.uuid == process_id)


def get_pending_processes():
    return procesos_table.search(Query().estado == 'pendiente')


def process_pending_tasks():
    print("[DEBUG 02]: ====================\n", "process_pending_tasks -> socketio", socketio, "\====================")
    
    if not process_lock.acquire(blocking=False):
        print("Ya hay un proceso en ejecución.")
        return

    try:
        while True:
            pending_processes = get_pending_processes()
            print("pending_processes:", pending_processes)
            if not pending_processes:
                print("No hay más procesos pendientes.")
                break

            for process in sorted(pending_processes, key=lambda x: x['fecha_creacion']):
                process_id = process['uuid']
                print(f"Ejecutando el proceso ID: {process_id}")
                try:
                    asyncio.run(create_video_local(
                        process['uuid'],
                        process['language'],
                        process['voice'],
                        process['main_question'],
                        process['num_questions'],
                        process['num_options'],
                        process['background_music'],
                        process['background_video'],
                        process['logo_path'],
                        process['account_text'],
                        process['sessionUUID'],
                        socketio
                    ))
                    update_process_status(process_id, 'completado')
                except Exception as e:
                    update_process_status(process_id, f'error: {e}')
                    print(f"Error al procesar el proceso ID: {process_id}, error: {e}")

            time.sleep(5)  # Espera antes de verificar nuevamente
    finally:
        process_lock.release()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    # Capturar los datos enviados en el POST
    context = request.form.get('context', '')
    language = request.form.get('language', 'Spanish')
    options = int(request.form.get('options', 5))
    
    # Generar las trivias usando la función generate_trivias
    generated_trivias = generate_trivias(context, options=options, language=language)
    
    # Retornar las trivias generadas en formato JSON
    return jsonify(generated_trivias)


@app.route('/process', methods=['POST'])
def process_request():
    
    print("[DEBUG B]: ====================\n", "process_request -> socketio:", socketio, "\====================")

    # Captura el archivo logo
    if 'logo' in request.files:
        logo = request.files['logo']
        extension = os.path.splitext(logo.filename)[1]  # Obtener la extensión del archivo
        # Nombre del archivo del logo permanece constante para todas las líneas
        logo_filename = f"{uuid.uuid4()}{extension}"
        logo_path = os.path.join(SCRIPT_DIR, './public/cargados/logos', logo_filename)
        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
        logo.save(logo_path)
    else:
        logo_path = ""

    # Captura datos del formulario
    data = request.form
    print(data)

    language = data.get('language', 'Spanish')
    voice = data.get('voice', 'Pedro')
    main_question = data.get('main_question')
    num_questions = int(data.get('num_questions'))
    num_options = int(data.get('num_options'))
    background_music = data.get('background_music')
    background_video = data.get('background_video')
    account_text = data.get('account', '@clubdelosgenios')
    sessionUUID = data.get('sessionUUID')

    # Procesar cada línea de main_question individualmente
    for line in main_question.splitlines():
        if line.strip():  # Verifica que la línea no esté vacía
            # Genera un process_id único para cada línea
            process_id = str(uuid.uuid4())

            # Registrar en el logger un archivo por cada línea procesada
            logger.add(f"./logs/file_{process_id}.log", rotation="1 day")

            # Guardar en la base de datos o realizar otra acción sensible a process_id
            save_to_db(process_id, language, voice, line, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID)

        # Inicia el proceso en segundo plano, usando process_id único por cada línea
        threading.Thread(target=process_pending_tasks).start()


    return jsonify({"message": "Procesos registrados exitosamente."}), 200


@app.route('/process_una_linea', methods=['POST'])
def process_request_una_linea():
    # Genera el process_id al inicio
    process_id = str(uuid.uuid4())

    # Captura el archivo logo
    if 'logo' in request.files:
        logo = request.files['logo']
        # Obtén la extensión del archivo (por ejemplo, '.jpg' o '.png')
        extension = os.path.splitext(logo.filename)[1]
        # Crea la ruta de almacenamiento usando process_id como nombre del archivo
        logo_path = os.path.join(SCRIPT_DIR, './public/cargados/logos', f"{process_id}{extension}")
        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
        # Guarda el archivo
        logo.save(logo_path)
    else:
        logo_path = ""
        # return jsonify({"error": "No se subió el logo"}), 400

    # data = request.form.to_dict()  # Captura datos del formulario
    data = request.form

    print(data)

    language = data.get('language', 'Spanish')
    voice = data.get('voice', 'Pedro')
    main_question = data.get('main_question')
    num_questions = int(data.get('num_questions'))
    num_options = int(data.get('num_options'))
    background_music = data.get('background_music')
    background_video = data.get('background_video')
    account_text = data.get('account', '@clubdelosgenios')

    logger.add(f"./logs/file_{process_id}.log", rotation="1 day")

    save_to_db(process_id, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text)

    # Inicia el proceso en segundo plano
    threading.Thread(target=process_pending_tasks).start()

    return jsonify({"message": "Proceso registrado exitosamente.", "process_id": process_id}), 200


@app.route('/<path:path>', methods=['GET'])
def serve_file_or_directory(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isdir(full_path):
        files = os.listdir(full_path)
        file_list_html = "<h1>Directory listing for {}</h1><ul>".format(path)
        for file in files:
            file_url = os.path.join(request.path, file)
            file_list_html += f"<li><a href='{file_url}'>{file}</a></li>"
        file_list_html += "</ul>"
        return render_template_string(file_list_html)
    else:
        return send_from_directory(app.static_folder, path)


@app.route('/videos', methods=['GET'])
def list_videos():
    video_files = []

    # Obtener todos los registros de la base de datos
    all_processes = procesos_table.all()

    # Filtrar solo los registros que tienen un url_video y estado 'completado'
    for process in all_processes:
        if 'url_video' in process and (process['estado'] == 'completado' or process['estado'] == 'pendiente'):
            video_files.append({
                "process_id": process['uuid'],
                "filename": process['url_video'],
                "main_question": process['main_question'],
                "num_questions": process['num_questions'],
                "num_options": process['num_options'],
                "language": process['language'],
                "sessionUUID": process['sessionUUID'],
                "modified": process['fecha_modificacion'],
                "status": process['estado']
            })

    # Ordenar los archivos por tiempo de modificación en orden descendente
    video_files.sort(key=lambda x: x["modified"], reverse=True)

    return jsonify(video_files)


@app.route('/videos/<process_id>', methods=['DELETE'])
def delete_process_endpoint(process_id):
    try:
        delete_process(process_id)
        return jsonify({"message": "Process deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/backgroundvideo/<videoid>', methods=['GET'])
def get_background_video(videoid):
    try:
        # Ruta del video en la carpeta pública
        videofile = videoid + ".mp4"
        video_path = os.path.join('public', 'assets', 'videos', videofile)

        # Verificar si el video existe en la ruta pública
        if not os.path.exists(video_path):
            return jsonify({"error": "Video not found"}), 404

        # Generar la URL pública completa para acceder al video
        video_url = f"https://trivias.luxuryroamers.com/assets/videos/{videofile}"

        return jsonify({"video_url": video_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/backgroundmusic/<musicid>', methods=['GET'])
def get_background_music(musicid):
    try:
        # Ruta de la música en la carpeta pública
        musicfile = musicid + ".mp3"
        music_path = os.path.join('public', 'assets', 'music', musicfile)

        # Verificar si la música existe en la ruta pública
        if not os.path.exists(music_path):
            return jsonify({"error": "Music not found"}), 404

        # Generar la URL pública completa para acceder a la música
        music_url = f"https://trivias.luxuryroamers.com/assets/music/{musicfile}"

        return jsonify({"music_url": music_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def start_process_monitor():
    while True:
        print("[DEBUG 01]: ====================\n", "start_process_monitor -> socketio", socketio, "\====================")
        process_pending_tasks()
        time.sleep(60)  # Esperar 1 minuto antes de verificar nuevamente


if __name__ == '__main__':
    
    print("[DEBUG A]: ====================\n", "__main__ -> socketio", socketio, "\====================")

    print(f"--------------------------------------------")
    print(f"Servidor Flask corriendo en el puerto {PORT}")
    print(f"--------------------------------------------")

    threading.Thread(target=start_process_monitor).start()  # Iniciar el monitor de procesos en segundo plano

    socketio.run(app, host='0.0.0.0', port=PORT)

    # app.run(host='0.0.0.0', port=PORT)
    # Corrección para iniciar la aplicación con soporte tanto para HTTP como para WebSocket
    