from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import threading
from creavideo import generate_video

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)
    
PORT = os.environ.get("PORT", "")

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-video', methods=['POST'])
def start_video():
    video_file = request.json.get('video_file', './trivia/public/generados/videos/fd17b9a7-0587-4edb-a22f-69ad06986881.mp4')
    output_file = request.json.get('output_file', 'output_video.mp4')

    # Inicia la creación del video en un hilo separado
    threading.Thread(target=generate_video, args=(video_file, output_file, socketio)).start()

    return jsonify({"status": "Video generation started"})

if __name__ == '__main__':
    # socketio.run(app, host='0.0.0.0', port=5000)
    print(f"--------------------------------------------")
    print(f"Servidor Flask corriendo en el puerto {PORT}")
    print(f"--------------------------------------------")

    socketio.run(app, host='0.0.0.0', port=PORT)
