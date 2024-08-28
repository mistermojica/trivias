import os
import asyncio
import random
import time
import uuid
from datetime import datetime
from openai import OpenAI
from loguru import logger
from flask_socketio import SocketIO
from flask import Flask, jsonify, render_template
from t import create_video_main, generate_trivias
from tinydb import TinyDB, Query
from threading import Lock
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

PUBLIC_FOLDER = 'public'
PORT = int(os.environ.get("PORT", "5000"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
openai = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__, static_folder=PUBLIC_FOLDER)
socketio = SocketIO(app, async_mode='eventlet')

db = TinyDB('luxuryroamers.json')
procesos_table = db.table('procesos')
process_lock = Lock()

async def create_video_local(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID):
    start_time = time.time()
    # clear_directory(f'./{PUBLIC_FOLDER}/{uuid4}')
    await create_video_main(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, socketio)
    end_time = time.time()
    return {"execution_time": end_time - start_time}

async def process_pending_tasks():
    async with process_lock:
        while True:
            pending_processes = get_pending_processes()
            if not pending_processes:
                break
            for process in sorted(pending_processes, key=lambda x: x['fecha_creacion']):
                process_id = process['uuid']
                try:
                    await socketio.emit('greeting', {'uuid': process['sessionUUID'], 'progress': "hola 2"})
                    await create_video_local(
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
                        process['sessionUUID']
                    )
                    update_process_status(process_id, 'completado')
                except Exception as e:
                    update_process_status(process_id, f'error: {e}')
            await asyncio.sleep(5)

async def start_process_monitor():
    while True:
        await process_pending_tasks()
        await asyncio.sleep(60)

if __name__ == '__main__':
    socketio.start_background_task(start_process_monitor)
    socketio.run(app, host='0.0.0.0', port=PORT)