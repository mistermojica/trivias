import asyncio
import websockets
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

async def main():
    # Simulación de creación de video con MoviePy
    video = VideoFileClip("./assets/videos/background1.mp4").subclip(0, 10)  # 10 segundos
    txt_clip = (TextClip("Hola, este es un video de prueba!", fontsize=70, color='white')
                .set_position('center')
                .set_duration(10))

    # Definición de final_clip (corrección aquí)
    final_clip = CompositeVideoClip([video, txt_clip])

    # Procesamiento en memoria con FFmpeg (usando communicate)
    process = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{final_clip.w}x{final_clip.h}",
        "-pix_fmt", "rgb24", "-r", str(final_clip.fps),
        "-i", "-", 
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-f", "matroska", "pipe:1"  # Cambiado a MKV para soporte sin seek
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

    try:
        # Escribir frames al proceso ffmpeg
        for frame in final_clip.iter_frames(dtype='uint8'):
            process.stdin.write(frame.tobytes())

        # Cerrar stdin para señalar que no hay más datos
        process.stdin.close()

        # Capturar la salida del proceso
        video_data, stderr = process.communicate()

        # Verificar si hubo errores en FFmpeg
        if process.returncode != 0:
            print(f"Error en FFmpeg: {stderr.decode()}")
            return  # Salir si hay un error

        # Envío del video al WebSocket
        async with websockets.connect("wss://sturdy-winner-qjx74659qx73x59j-8000.app.github.dev") as websocket:
            await websocket.send(video_data)
            print("Video enviado con éxito!")

    except Exception as e:
        process.kill()
        raise e

asyncio.run(main())
