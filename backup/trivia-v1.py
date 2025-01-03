import os
from moviepy.editor import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from moviepy.video.fx.all import fadein, fadeout
import boto3
import time
import uuid
import io
import numpy as np
from PIL import Image, ImageDraw


# Ejemplo de uso de la función principal
uuidcode = str(uuid.uuid4())

voices = [
    {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "text", "Newscaster": ""},
    {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "text", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Ivy", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Joanna", "Gender": "Female", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kendra", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kimberly", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Salli", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Joey", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Justin", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kevin", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Stephen", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "es-US", "VoiceId": "Lupe", "Gender": "Female", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "es-US", "VoiceId": "Pedro", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "es-US", "VoiceId": "Miguel", "Gender": "Male", "TextType": "ssml", "Newscaster": ""}
]

def get_polly_response(engine, voiceid, text, prosodyrate="100%"):
    print("get_polly_response:", engine, voiceid, text, prosodyrate)

    # Coloca tu lista de voces aquí
    voice = next((v for v in voices if v["Engine"] == engine and v["VoiceId"] == voiceid), None)

    print(voice)

    if not voice:
        raise ValueError(f"Voice with Engine '{engine}' and VoiceId '{voiceid}' not found.")

    text_type = voice["TextType"]
    language_code = voice["LanguageCode"]
    newscaster = voice["Newscaster"]

    if text_type == "text":
        polly_text = text
    elif text_type == "ssml":
        if newscaster == "news":
            polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="news">{text}</amazon:domain></prosody></speak>'
        else:
            polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="conversational">{text}</amazon:domain></prosody></speak>'
    else:
        raise ValueError("Invalid TextType")

    polly_client = boto3.Session(profile_name='doccumi', region_name="us-east-1").client("polly")

    print("get_polly_response:", polly_text, text_type, voiceid, language_code)

    response = polly_client.synthesize_speech(
        Engine=engine,
        OutputFormat="mp3",
        Text=polly_text,
        TextType=text_type,
        VoiceId=voiceid,
        LanguageCode=language_code,
    )

    return response

def create_file_path(file_path):
    print("file_path:", file_path)
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Ruta creada: {directory}")
    else:
        print(f"La ruta ya existe: {directory}")

def text_to_speech_polly(text, output_filename, voz, max_retries=7):
    create_file_path(output_filename)

    attempt = 0
    success = False
    while not success and attempt < max_retries:
        try:
            response = get_polly_response("neural", voz, text, "100%")
            audio_data = response["AudioStream"].read()

            with open(output_filename, "wb") as out:
                out.write(audio_data)

            success = True
        except Exception as e:
            attempt += 1
            print(f"Error on attempt {attempt}: {e}")
            time.sleep(3)  # Wait a bit before retrying

    if not success:
        raise Exception(f"Failed to get Polly response after {max_retries} attempts")

    return output_filename

# Generar el audio narrativo con AWS Polly
def generate_narration(text, output_file, voz):
    text_to_speech_polly(text, output_file, voz)

# Crear un clip de video de fondo con opacidad
def create_background_video(background_video_path, duration):
    background_clip = VideoFileClip(background_video_path).subclip(0, duration)
    return background_clip.set_opacity(0.5)


def add_logo(logo_path, video_clip):
    # Abrir el logo como imagen Pillow
    logo_image = Image.open(logo_path)

    # Calcular el nuevo tamaño del logo
    final_width = int(video_clip.w * 0.8)
    aspect_ratio = logo_image.height / logo_image.width
    new_height = int(final_width * aspect_ratio)

    # Redimensionar el logo usando Pillow
    logo_resized = logo_image.resize((final_width, new_height), Image.Resampling.LANCZOS)

    # Convertir la imagen redimensionada a ImageClip
    logo_clip = ImageClip(np.array(logo_resized)).set_duration(video_clip.duration)

    # Posicionar el logo en el video
    logo_clip = logo_clip.set_position(("center", 100))  # Agregar un margen de 100 píxeles desde la parte superior

    return logo_clip

# Añadir texto de la pregunta
def add_question_text(question_text, video_clip, question_font_path, margin=80, top_margin=450):
    # Calcular el ancho máximo permitido para el texto, considerando los márgenes
    max_width = video_clip.w - 2 * margin

    # Crear el TextClip con ajuste de línea
    question_clip = (TextClip(question_text, fontsize=80, color='white', font=question_font_path, method='caption', size=(max_width, None))
                     .set_duration(video_clip.duration)
                     .set_pos(("center", top_margin)))  # Controlar la altura de presentación con top_margin
    return question_clip

# Añadir opciones de respuesta
def add_options(options, video_clip, options_font_path, margin=170, top_margin=1000):
    option_clips = []
    first_option_pos = top_margin
    option_space = 170
    y_positions = [first_option_pos, first_option_pos + option_space, first_option_pos + (option_space * 2)]

    # Configuración de estilo
    circle_radius = int(40 * 1.5)  # Aumentar el radio del círculo en un 30%
    circle_color = '#6A5ACD'  # Color del círculo en formato hexadecimal (Lavender)
    option_bg_color = '#FFFFFF'  # Fondo blanco para las opciones
    option_bg_height = 115  # Altura del fondo de las opciones
    corner_radius = 50  # Radio de las esquinas redondeadas del fondo

    for i, option in enumerate(options):
        # Crear el círculo con Pillow
        circle_image = Image.new("RGBA", (circle_radius * 2, circle_radius * 2), (255, 255, 255, 0))
        draw = ImageDraw.Draw(circle_image)
        draw.ellipse((0, 0, circle_radius * 2, circle_radius * 2), fill=circle_color)

        # Convertir la imagen Pillow a un array numpy
        circle_array = np.array(circle_image)

        # Convertir el array numpy a ImageClip
        circle_clip = ImageClip(circle_array).set_duration(video_clip.duration)
        circle_clip = circle_clip.set_position((margin, y_positions[i]))

        # Crear el texto dentro del círculo
        label_text = chr(65 + i)  # Genera las letras A, B, C
        label_clip = (TextClip(label_text, fontsize=80, color='white', font=options_font_path)
                      .set_duration(video_clip.duration)
                      .set_position((margin + 30, y_positions[i] + 10)))  # Ajustar posición del texto dentro del círculo

        # Crear el fondo redondeado para la opción usando Pillow
        bg_width = video_clip.w - 2 * margin
        bg_image = Image.new("RGBA", (bg_width, option_bg_height), (255, 255, 255, 0))
        rounded_rectangle = Image.new("RGBA", (bg_width, option_bg_height), option_bg_color)
        mask = Image.new("L", (bg_width, option_bg_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (bg_width, option_bg_height)], corner_radius, fill=255)
        bg_image = Image.composite(rounded_rectangle, bg_image, mask)

        # Convertir el fondo redondeado a ImageClip
        bg_array = np.array(bg_image)
        option_bg_clip = ImageClip(bg_array).set_duration(video_clip.duration)
        option_bg_clip = option_bg_clip.set_position((margin + 10, y_positions[i] + 1))

        # Crear el texto de la opción
        option_text_clip = (TextClip(option, fontsize=70, color='black', font=options_font_path)
                            .set_duration(video_clip.duration)
                            .set_position((margin + circle_radius * 2 + 20, y_positions[i] + 15)))

        # Componer la opción final
        composed_clip = CompositeVideoClip([option_bg_clip, circle_clip, label_clip, option_text_clip], size=(video_clip.w, video_clip.h))
        option_clips.append(composed_clip)

    return option_clips

# Revelar la opción correcta
def reveal_correct_option(options_clips, correct_option_index, reveal_time, options_font_path):
    # Crear un nuevo TextClip con el fondo amarillo para la opción correcta
    correct_option_text = options_clips[correct_option_index].txt
    correct_option_clip = TextClip(correct_option_text, fontsize=40, bg_color='yellow', color='black', font=options_font_path)
    correct_option_clip = correct_option_clip.set_duration(reveal_time).set_pos(options_clips[correct_option_index].pos)

    # Cambiar la duración de las otras opciones para que se terminen cuando se revele la correcta
    for i, clip in enumerate(options_clips):
        if i != correct_option_index:
            clip = clip.set_end(reveal_time)
        else:
            options_clips[i] = correct_option_clip

    return options_clips

# Añadir el texto de la cuenta
def add_account_text(account_text, video_clip, account_font_path):
    account_clip = (TextClip(account_text, fontsize=50, color='white', font=account_font_path)
                    .set_duration(video_clip.duration)
                    .set_pos(("center", 1700)))
    return account_clip

# Añadir efectos de sonido
def add_sound_effects(tictac_sound_path, reveal_time):
    tictac_sound = AudioFileClip(tictac_sound_path).subclip(0, reveal_time)
    return tictac_sound

# Componer el video final
def compose_video(background_clip, logo_clip, question_clip, options_clips, account_clip, narration_audio, sound_effects, output_file):
    final_clip = CompositeVideoClip([background_clip, logo_clip, question_clip, *options_clips, account_clip])
    final_audio = CompositeAudioClip([narration_audio.set_start(0), sound_effects.set_start(narration_audio.duration)])
    final_clip = final_clip.set_audio(final_audio)
    # final_clip = final_clip.subclip(0, 0.1)
    final_clip.write_videofile("./videos/output.mp4", codec='libx264', fps=24, preset='ultrafast')
    # final_clip.write_videofile(output_file, codec='libx264', fps=24, preset='ultrafast')

# Función principal para generar el video de trivia
def generate_trivia_video(background_video_path, logo_path, question_text, options, correct_option_index, account_text, narration_text, tictac_sound_path, output_file, question_font_path, options_font_path, account_font_path):
    narration_audio_file = f"./audios/{uuidcode}.mp3"
    generate_narration(narration_text, narration_audio_file, "Lupe")

    background_clip = create_background_video(background_video_path, duration=10)
    logo_clip = add_logo(logo_path, background_clip)
    question_clip = add_question_text(question_text, background_clip, question_font_path)
    options_clips = add_options(options, background_clip, options_font_path)
    # Pasa la fuente de opciones a la función reveal_correct_option
    # options_clips = reveal_correct_option(options_clips, correct_option_index, reveal_time=8, options_font_path=options_font_path)
    account_clip = add_account_text(account_text, background_clip, account_font_path)
    narration_audio = AudioFileClip(narration_audio_file)
    sound_effects = add_sound_effects(tictac_sound_path, reveal_time=8)

    compose_video(background_clip, logo_clip, question_clip, options_clips, account_clip, narration_audio, sound_effects, output_file)

    # Limpieza de archivos temporales
    os.remove(narration_audio_file)

generate_trivia_video(
    background_video_path="./assets/videos/background1.mp4",
    logo_path="./assets/images/logo.png",
    question_text="¿Qué marca es representada por un logo de una manzana mordida?",
    options=["Nike", "Apple", "Microsoft"],
    correct_option_index=1,
    account_text="@elclubdelosgenios",
    narration_text="¿Qué marca es representada por un logo de una manzana mordida?",
    tictac_sound_path="./assets/audios/clock.mp3",
    output_file=f"./videos/{uuidcode}.mp4",
    question_font_path="./assets/fonts/TT-Milks-Casual-Pie-Trial-Base.otf",  # Ruta a la fuente para la pregunta
    options_font_path="./assets/fonts/Sniglet-Regular.ttf",  # Ruta a la fuente para las opciones
    account_font_path="./assets/fonts/Sniglet-Regular.ttf"  # Ruta a la fuente para la cuenta
)
