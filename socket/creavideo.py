from moviepy.editor import VideoFileClip
from proglog import ProgressBarLogger

class VideoCreationLogger(ProgressBarLogger):
    def __init__(self, sio):
        super().__init__()
        self.sio = sio

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percentage = (value / total) * 100
        else:
            percentage = 0

        # Emitir el progreso al cliente
        self.sio.emit('video_progress', {'progress': percentage})

def generate_video(input_file, output_file, sio):
    logger = VideoCreationLogger(sio)
    videoclip = VideoFileClip(input_file)

    # Generar el video usando MoviePy y el logger personalizado
    videoclip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=12, preset='ultrafast', logger=logger)

    videoclip.close()
