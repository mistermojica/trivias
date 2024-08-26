import os
from moviepy.editor import concatenate_videoclips, VideoFileClip, ImageClip, TextClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip, VideoClip
from moviepy.video.fx.all import fadein, fadeout
import boto3
import time
import uuid
import io
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import subprocess
import argparse
from dotenv import load_dotenv, find_dotenv
from proglog import ProgressBarLogger

load_dotenv(find_dotenv())

uuidcode = ""  # Genera un UUID único para archivos temporales

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

openai = OpenAI()

openai.api_key = OPENAI_API_KEY

# sio = None

SCRIPT_DIR = os.path.dirname(__file__)

# {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "text", "Newscaster": ""},
# {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "text", "Newscaster": ""},
# {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "text", "Newscaster": ""},
# {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "text", "Newscaster": ""},

voices = [
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
    {"Engine": "standard", "LanguageCode": "es-US", "VoiceId": "Miguel", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "es-US", "VoiceId": "Penelope", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "es-MX", "VoiceId": "Mia", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "es-MX", "VoiceId": "Andres", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},

    {"Engine": "neural", "LanguageCode": "fr-FR", "VoiceId": "Lea", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "fr-FR", "VoiceId": "Remi", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "fr-FR", "VoiceId": "Celine", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "fr-FR", "VoiceId": "Mathieu", "Gender": "Male", "TextType": "text", "Newscaster": ""},

    {"Engine": "neural", "LanguageCode": "pt-BR", "VoiceId": "Camila", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "pt-BR", "VoiceId": "Vitoria", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "pt-BR", "VoiceId": "Ricardo", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "pt-BR", "VoiceId": "Thiago", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},

    {"Engine": "neural", "LanguageCode": "it-IT", "VoiceId": "Bianca", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "it-IT", "VoiceId": "Adriano", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "it-IT", "VoiceId": "Carla", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "it-IT", "VoiceId": "Giorgio", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},

    {"Engine": "neural", "LanguageCode": "de-DE", "VoiceId": "Vicki", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "de-DE", "VoiceId": "Daniel", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "de-DE", "VoiceId": "Marlene", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "de-DE", "VoiceId": "Hans", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},

    {"Engine": "standard", "LanguageCode": "ru-RU", "VoiceId": "Tatyana", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "ru-RU", "VoiceId": "Maxim", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},

    {"Engine": "standard", "LanguageCode": "zh-CN", "VoiceId": "Zhiyu", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},

    {"Engine": "neural", "LanguageCode": "hi-IN", "VoiceId": "Kajal", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "hi-IN", "VoiceId": "Aditi", "Gender": "Female", "TextType": "ssml", "Newscaster": ""}
]

def find_voice(voiceid, language):
    language_map = {
        "English": "en-US",
        "Spanish": ["es-US", "es-MX"],
        "French": "fr-FR",
        "Portuguese": "pt-BR",
        "Italian": "it-IT",
        "Chinese": "zh-CN",
        "Hindi": "hi-IN",
        "Russian": "ru-RU",
        "Japanese": "ja-JP",
        "German": "de-DE"
    }

    language_code = language_map.get(language)
    if not language_code:
        return None

    if isinstance(language_code, list):
        # Si el código de idioma es una lista (por ejemplo, para Español), buscar en ambos
        for code in language_code:
            for voice in voices:
                if voice["VoiceId"] == voiceid and voice["LanguageCode"] == code:
                    return voice
    else:
        # Para los demás idiomas, buscar en un solo código
        for voice in voices:
            if voice["VoiceId"] == voiceid and voice["LanguageCode"] == language_code:
                return voice
    return None


def get_polly_response(voiceid, language, text, prosodyrate="100%"):
    # print("get_polly_response:", engine, voiceid, text, prosodyrate)

    # Coloca tu lista de voces aquí
    voice = find_voice(voiceid, language)

    # print("=========================================\n", voice, "\n=========================================")

    if not voice:
        raise ValueError(f"Voice with Languaje '{language}' and VoiceId '{voiceid}' not found.")

    engine = voice["Engine"]
    text_type = voice["TextType"]
    language_code = voice["LanguageCode"]
    newscaster = voice["Newscaster"]

    if text_type == "text":
        polly_text = text
    elif text_type == "ssml":
        if newscaster == "news":
            polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="news">{text}</amazon:domain></prosody></speak>'
        else:
            polly_text = f'<speak><prosody rate="{prosodyrate}">{text}</prosody></speak>'
            # polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="conversational">{text}</amazon:domain></prosody></speak>'
    else:
        raise ValueError("Invalid TextType")

    polly_client = boto3.Session(profile_name='doccumi', region_name="us-east-1").client("polly")

    # print("get_polly_response:", polly_text, text_type, voiceid, language_code)

    response = polly_client.synthesize_speech(
        Engine=engine,
        OutputFormat="ogg_vorbis",
        Text=polly_text,
        TextType=text_type,
        VoiceId=voiceid,
        LanguageCode=language_code,
    )

    return response

def create_file_path(file_path):
    # print("file_path:", file_path)
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Ruta creada: {directory}")
    # else:
    #     print(f"La ruta ya existe: {directory}")

def text_to_speech_polly(text, output_filename, voice, language, max_retries=7):
    create_file_path(output_filename)

    attempt = 0
    success = False
    while not success and attempt < max_retries:
        try:
            response = get_polly_response(voice, language, text, "100%")
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
def generate_narration(text, output_file, voice, language):
    text_to_speech_polly(text, output_file, voice, language)


def create_background_video(background_video_path, background_music_path, target_width, target_height, duration):
    # Cargar el video y cortar la duración al tiempo deseado
    # background_clip = VideoFileClip(background_video_path).subclip(0, duration)
    background_clip = VideoFileClip(background_video_path).loop(duration=duration)
    background_music_clip = AudioFileClip(background_music_path).set_duration(duration).volumex(0.10)

    # Eliminar el audio del clip
    background_clip = background_clip.without_audio()

    background_clip = background_clip.set_audio(background_music_clip)

    # Obtener dimensiones originales
    original_width, original_height = background_clip.size

    # Caso 1: Video horizontal (ancho > alto)
    if original_width > original_height:
        # Escalar la altura a 1920
        background_clip = background_clip.resize(height=target_height)
        # Recortar el centro del video para que el ancho sea 1080
        x_center = background_clip.w / 2
        background_clip = background_clip.crop(width=target_width, height=target_height, x_center=x_center, y_center=target_height / 2)

    # Caso 2: Video vertical o cuadrado (ancho <= alto)
    else:
        # Escalar el ancho a 1080
        background_clip = background_clip.resize(width=target_width)
        # Si la altura aún no es suficiente, seguir escalando hasta que la altura sea al menos 1920
        if background_clip.h < target_height:
            scaling_factor = target_height / background_clip.h
            background_clip = background_clip.resize(height=int(background_clip.h * scaling_factor))
        # Recortar el centro del video para que el ancho sea 1080
        x_center = background_clip.w / 2
        y_center = background_clip.h / 2
        background_clip = background_clip.crop(width=target_width, height=target_height, x_center=x_center, y_center=y_center)

    print("create_background_video - background_clip.w, background_clip.h:", background_clip.w, background_clip.h)

    # Establecer opacidad y devolver el clip
    return background_clip.set_opacity(0.7)


def add_logo(logo_path, ctxVideo):
    print(f"[DEBUG] ============= add_logo - ctxVideo: {ctxVideo} =============")

    # Abrir el logo como imagen Pillow
    logo_image = Image.open(logo_path)

    # Calcular el nuevo tamaño del logo
    final_width = int(ctxVideo["video_width"] * 0.5)
    aspect_ratio = logo_image.height / logo_image.width
    new_height = int(final_width * aspect_ratio)

    # Redimensionar el logo usando Pillow
    logo_resized = logo_image.resize((final_width, new_height), Image.Resampling.LANCZOS)

    # Convertir la imagen redimensionada a ImageClip
    logo_clip = ImageClip(np.array(logo_resized)).set_duration(ctxVideo["video_duration"])

    # Posicionar el logo en el video
    logo_clip = logo_clip.set_position(("center", 200))  # Agregar un margen de 100 píxeles desde la parte superior

    return logo_clip


# Añadir texto de la pregunta
def add_question_text(question_text, ctxVideo, question_font_path, margin=80, top_margin=450):
    print(f"[DEBUG] ============= add_question_text - ctxVideo: {ctxVideo} =============")

    # Calcular el ancho máximo permitido para el texto, considerando los márgenes
    max_width = ctxVideo["video_width"] - (2 * margin)

    print(f"[DEBUG] add_question_text - max_width: {max_width}")

    # Calcular la longitud del texto
    text_length = len(question_text)

    print(f"[DEBUG] add_question_text - text_length: {text_length}")

    # Definir límites de fontsize
    min_fontsize = 50
    max_fontsize = 80

    # Definir rango de caracteres
    min_chars = 55
    max_chars = 100

    # Cálculo del fontsize basado en la longitud del texto
    if text_length <= min_chars:
        fontsize = max_fontsize
    elif text_length >= max_chars:
        fontsize = min_fontsize
    else:
        # Ajuste proporcional entre los valores definidos
        fontsize = int(max_fontsize - ((text_length - min_chars) / (max_chars - min_chars)) * (max_fontsize - min_fontsize))

    print(f"[DEBUG] add_question_text - fontsize: {fontsize}")

    # Crear el TextClip con ajuste de línea
    question_clip = (TextClip(question_text, fontsize=fontsize, color='white', font=question_font_path, method='caption', size=(max_width, None))
                     .set_duration(ctxVideo["video_duration"])
                     .set_pos(("center", top_margin)))  # Controlar la altura de presentación con top_margin
    return question_clip


# Añadir opciones de respuesta
def add_options(options, ctxVideo, options_font_path, top_margin, margin=170):
    # print(f"[DEBUG] add_options - video_clip.duration: {video_clip.duration}")

    if not top_margin:
        top_margin=950

    option_clips = []
    first_option_pos = top_margin

    # Condicional para ajustar el espacio entre opciones
    if len(options) == 3:
        option_space = 170
    elif len(options) == 4:
        option_space = 150
    else:
        option_space = 170  # Valor por defecto

    y_positions = []
    for i in range(len(options)):
        y_position = first_option_pos + (option_space * i)
        y_positions.append(y_position)

    # Configuración de estilo
    circle_radius = int(40 * 1.5)  # Aumentar el radio del círculo en un 30%
    circle_color = '#6A5ACD'  # Color del círculo en formato hexadecimal (Lavender)
    option_bg_color = 'white'  # Fondo blanco para las opciones
    option_bg_height = 115  # Altura del fondo de las opciones
    corner_radius = 50  # Radio de las esquinas redondeadas del fondo

    # Definir límites de fontsize para el texto de las opciones
    max_fontsize = 65
    min_fontsize = 40
    max_chars = 15  # Máximo de caracteres para el tamaño de fuente más grande

    for i, option in enumerate(options):
        # Crear el círculo con Pillow
        circle_image = Image.new("RGBA", (circle_radius * 2, circle_radius * 2), (255, 255, 255, 0))
        draw = ImageDraw.Draw(circle_image)
        draw.ellipse((0, 0, circle_radius * 2, circle_radius * 2), fill=circle_color)

        # Convertir la imagen Pillow a un array numpy
        circle_array = np.array(circle_image)

        # Convertir el array numpy a ImageClip
        circle_clip = ImageClip(circle_array).set_duration(ctxVideo["video_duration"])
        circle_clip = circle_clip.set_position((margin, y_positions[i]))

        # Crear el texto dentro del círculo
        label_text = chr(65 + i)  # Genera las letras A, B, C
        label_clip = (TextClip(label_text, fontsize=80, color='white', font=options_font_path)
                      .set_duration(ctxVideo["video_duration"])
                      .set_position((margin + 30, y_positions[i] + 10)))  # Ajustar posición del texto dentro del círculo

        # Crear el fondo redondeado para la opción usando Pillow
        bg_width = ctxVideo["video_width"] - 2 * margin
        bg_image = Image.new("RGBA", (bg_width, option_bg_height), (255, 255, 255, 0))
        rounded_rectangle = Image.new("RGBA", (bg_width, option_bg_height), option_bg_color)
        mask = Image.new("L", (bg_width, option_bg_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (bg_width, option_bg_height)], corner_radius, fill=255)
        bg_image = Image.composite(rounded_rectangle, bg_image, mask)

        # Convertir el fondo redondeado a ImageClip
        bg_array = np.array(bg_image)
        option_bg_clip = ImageClip(bg_array).set_duration(ctxVideo["video_duration"])
        option_bg_clip = option_bg_clip.set_position((margin + 10, y_positions[i] + 1))

        # Calcular el fontsize basado en la longitud del texto de la opción
        text_length = len(option)
        if text_length <= max_chars:
            fontsize = max_fontsize
        else:
            fontsize = max(min_fontsize, int(max_fontsize - (text_length - max_chars) * (max_fontsize - min_fontsize) / max_chars))

        print(f"[DEBUG] add_options - fontsize for option '{option}': {fontsize}")

        # Crear el texto de la opción
        option_text_clip = (TextClip(option, fontsize=fontsize, color='black', font=options_font_path)
                            .set_duration(ctxVideo["video_duration"])
                            .set_position((margin + circle_radius * 2 + 20, y_positions[i] + 15)))

        option_text_clip.text = option

        # Componer la opción final
        composed_clip = CompositeVideoClip([option_bg_clip, circle_clip, label_clip, option_text_clip], size=(ctxVideo["video_width"], ctxVideo["video_height"]))
        option_clips.append(composed_clip)

    return option_clips

# Revelar la opción correcta
def reveal_correct_option(options_clips, bg_clip_width, options, correct_option_index, start_time, reveal_time, options_font_path, margin=80):
    # print(f"[DEBUG] Opciones: {options}")
    # print(f"[DEBUG] Clips de Opciones: {options_clips}")
    # print(f"[DEBUG] Índice de Opción Correcta: {correct_option_index}")
    # print(f"[DEBUG] reveal_correct_option - video_clip.duration: {video_clip.duration}")
    # print(f"[DEBUG] reveal_correct_option - start_time: {start_time}")
    # print(f"[DEBUG] reveal_correct_option - reveal_time: {reveal_time}")

    # Obtener el texto de la opción correcta desde el arreglo
    correct_option_text = options[correct_option_index]
    # print(f"[DEBUG] Texto de Opción Correcta: {correct_option_text}")

    # Obtener el clip de la opción correcta
    composite_clip = options_clips[correct_option_index]

    # Encontrar el TextClip que contiene el texto de la opción correcta
    option_text_clip = None
    bg_model_clip = composite_clip.clips[0]
    for clip in composite_clip.clips:
        if isinstance(clip, TextClip) and hasattr(clip, 'text'):
            if clip.text == correct_option_text:
                option_text_clip = clip
                break

    if not option_text_clip:
        raise ValueError("No se encontró un TextClip con el texto de la opción dentro del CompositeVideoClip")

    correct_option_bg_color = 'yellow'
    option_bg_height = 115
    corner_radius = 50
    bg_width = bg_clip_width - (2 * margin)

    # Crear el fondo amarillo para la opción correcta
    correct_bg_image = Image.new("RGBA", (bg_width, option_bg_height), (255, 255, 255, 0))
    correct_rounded_rectangle = Image.new("RGBA", (bg_width, option_bg_height), correct_option_bg_color)
    correct_mask = Image.new("L", (bg_width, option_bg_height), 0)
    correct_mask_draw = ImageDraw.Draw(correct_mask)
    correct_mask_draw.rounded_rectangle([(0, 0), (bg_width, option_bg_height)], corner_radius, fill=255)
    correct_bg_image = Image.composite(correct_rounded_rectangle, correct_bg_image, correct_mask)

    correct_bg_array = np.array(correct_bg_image)
    # correct_option_bg_clip = ImageClip(correct_bg_array).set_duration(reveal_time).set_position(bg_model_clip.pos).set_start(start_time)

    correct_bg_image_resized = Image.fromarray(correct_bg_array).resize((bg_model_clip.w, bg_model_clip.h), Image.Resampling.LANCZOS)

    # Convertir la imagen redimensionada en un array numpy
    correct_bg_array_resized = np.array(correct_bg_image_resized)

    # Crear el ImageClip con el tamaño ya ajustado
    correct_option_bg_clip = ImageClip(correct_bg_array_resized).set_duration(reveal_time).set_position(bg_model_clip.pos).set_start(start_time)

    # Crear el nuevo CompositeVideoClip que incluye el fondo amarillo y mantiene el fondo blanco hasta el final
    # new_composed_clip = CompositeVideoClip(
    #     composite_clip.clips + [correct_option_bg_clip],
    #     size=(composite_clip.w, composite_clip.h)
    # )

    # Ajustar el clip original para que termine cuando comience correct_option_bg_clip
    new_clips = []
    for clip in composite_clip.clips:
        if isinstance(clip, ImageClip) and clip.size == correct_option_bg_clip.size:
            # Ajustar la duración del clip original para que termine cuando comience el nuevo clip
            original_clip = clip.set_end(start_time)
            new_clips.append(original_clip)
            # Agregar el clip amarillo que comienza en start_time
            new_clips.append(correct_option_bg_clip)
        else:
            new_clips.append(clip)

    # Crear el nuevo CompositeVideoClip con la lista de clips actualizada
    new_composed_clip = CompositeVideoClip(
        new_clips,
        size=(composite_clip.w, composite_clip.h)
    )

    # Actualizar la lista de clips de opciones con el nuevo clip compuesto para la opción correcta
    options_clips[correct_option_index] = new_composed_clip

    return options_clips

# Añadir el texto de la cuenta
def add_account_text(account_text, video_duration, account_font_path):
    account_clip = (TextClip(account_text, fontsize=50, color='white', font=account_font_path)
                    .set_duration(video_duration)
                    .set_pos(("center", 1700)))
    return account_clip

# Añadir efectos de sonido
def add_sound_effects(tictac_sound_path, start_time, reveal_time):
    tictac_sound = AudioFileClip(tictac_sound_path).subclip(start_time, reveal_time)
    return tictac_sound

# Función para crear la imagen del emoji y devolverla como un objeto Image de PIL
def create_emoji_image(unicode_text, font_path, constant_font_size, emoji_size):
    # Cargar la fuente con el tamaño especificado
    font = ImageFont.truetype(font_path, constant_font_size)

    # Calcular el tamaño del texto (emoji) utilizando getbbox
    left, top, right, bottom = font.getbbox(unicode_text)
    text_width = right - left
    text_height = bottom - top

    # Crea una nueva imagen con el tamaño del texto
    im = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # Dibuja el emoji en la imagen
    draw.text((-left, -top), unicode_text, font=font, embedded_color=True)

    # Redimensionar la imagen al tamaño especificado por el parámetro emoji_size
    im_resized = im.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)

    # Devuelve la imagen redimensionada como un objeto PIL
    return im_resized

def create_progress_bar_with_emoji(duration, width=800, height=100, scale_height=0.8, emoji_size=100, bar_height=100, bar_color="green", bg_color="black", emoji="🚀", constant_font_size=137, font_path="", proportion=0.8):
    # Diccionario de colores RGB
    color_dict = {
        "yellow": (255, 255, 0),
        "green": (0, 255, 0),
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "gray": (128, 128, 128),
    }

    # Convertir nombres de colores a valores RGB
    bar_color_rgb = color_dict[bar_color]
    bg_color_rgb = color_dict[bg_color]

    # Crear la imagen del emoji y convertirla en un array numpy
    emoji_image = create_emoji_image(emoji, font_path, constant_font_size, emoji_size)
    emoji_array = np.array(emoji_image)

    # Crear un ImageClip a partir del array numpy
    emoji_clip = ImageClip(emoji_array).set_duration(duration)

    # Reducir la altura total del video según el parámetro scale_height
    total_height = int((bar_height + emoji_clip.h) * scale_height)  # Nueva altura reducida

    # Definir el tamaño ocupado por la barra de progreso y el emoji (80% del ancho total)
    content_width = int(width * proportion)
    margin = (width - content_width) // 2  # Espacio en blanco a los lados

    def make_frame(t):
        # Crear una imagen de fondo con color sólido usando PIL
        img = Image.new("RGBA", (content_width, bar_height), (0, 0, 0, 0))  # Fondo transparente

        draw = ImageDraw.Draw(img)
        radius = bar_height // 2  # El radio es la mitad de la altura para bordes completamente redondeados

        # Dibujar la barra de fondo gris con bordes redondeados
        draw.rounded_rectangle(
            [(0, 0), (content_width, bar_height)],
            radius=radius,
            fill=bg_color_rgb
        )

        # Calcular el ancho de la barra de progreso basada en el tiempo t y la duración total
        bar_width = int((t / duration) * content_width)

        # Dibujar la barra de progreso con bordes redondeados sobre la barra gris
        draw.rounded_rectangle(
            [(0, 0), (bar_width, bar_height)],
            radius=radius,
            fill=bar_color_rgb
        )

        # Convertir la imagen de PIL a RGB para evitar conflictos de canal alfa
        img = img.convert("RGB")

        # Convertir la imagen de PIL a un array NumPy para MoviePy
        return np.array(img)

    # Crear un VideoClip para la barra de progreso
    progress_bar_clip = VideoClip(make_frame, duration=duration).set_position((margin, (total_height - bar_height) // 2))

    # Calcular la posición vertical del emoji y la barra para que ambos estén centrados
    emoji_position_y = (total_height - bar_height) // 2 - emoji_clip.h // 2 + bar_height // 2

    # Alinear el centro del emoji con el borde derecho de la barra de progreso dentro del 80%
    emoji_clip = emoji_clip.set_position(lambda t: (
        margin + int((t / duration) * content_width) - emoji_clip.w // 2,
        emoji_position_y
    ))

    # Componer el clip final con la barra de progreso y el emoji
    final_clip = CompositeVideoClip([
        progress_bar_clip,
        emoji_clip
    ], size=(width, total_height))

    return final_clip


# Componer el video final
def compose_video(ctxVideo, video_total_duration, logo_clip, question_clip, question_image_clip, options_clips, account_clip, narration_audio, narration_audio_winner, clock_sound_effects, ding_sound_effects, progress_bar_with_emoji):
    # final_clip = CompositeVideoClip([background_clip.set_start(0), logo_clip.set_start(0), question_clip.set_start(0), question_image_clip.set_start(0), *options_clips, account_clip.set_start(0), progress_bar_with_emoji.set_start(narration_audio.duration)])

    video_size = (ctxVideo["video_width"], ctxVideo["video_height"])

    final_clip = CompositeVideoClip([logo_clip.set_start(0), question_clip.set_start(0), question_image_clip.set_start(0), *options_clips, account_clip.set_start(0), progress_bar_with_emoji.set_start(narration_audio.duration)], size=video_size)
    final_clip.set_duration(video_total_duration)

    print(f"[DEBUG] video_total_duration 1: {video_total_duration}")

    # for idx, clip in enumerate(options_clips):
    #     print(f"[DEBUG] options_clips[{idx}] - start: {clip.start}, duration: {clip.duration}, end: {clip.end}")

    # final_audio = CompositeAudioClip([narration_audio.set_start(0), sound_effects.set_start(narration_audio.duration)])
    final_audio = CompositeAudioClip([
        narration_audio.set_start(0),
        clock_sound_effects.set_start(narration_audio.duration),
        ding_sound_effects.volumex(0.05).set_start(narration_audio.duration + clock_sound_effects.duration),
        narration_audio_winner.set_start(narration_audio.duration + clock_sound_effects.duration + 1)
    ])

    print(f"[DEBUG] narration_audio.duration: {narration_audio.duration}")
    print(f"[DEBUG] clock_sound_effects.duration: {clock_sound_effects.duration}")
    print(f"[DEBUG] ding_sound_effects.duration: {ding_sound_effects.duration}")
    print(f"[DEBUG] narration_audio_winner.duration: {narration_audio_winner.duration}")
    # print(f"[DEBUG] clock_sound_effects.duration: {clock_sound_effects.duration}")
    # print(f"[DEBUG] narration_audio.duration + clock_sound_effects.duration: {narration_audio.duration + clock_sound_effects.duration}")
    # print(f"[DEBUG] final_audio.duration: {final_audio.duration}")

    final_clip = final_clip.set_audio(final_audio)
    print(f"[DEBUG] final_audio.duration 2: {final_audio.duration}")
    print(f"[DEBUG] final_clip.duration 2: {final_clip.duration}")

    # final_clip = final_clip.subclip(0, 4)
    # final_clip.write_videofile(output_file, codec='libx264', fps=24, preset='ultrafast')
    # final_clip.write_videofile(output_file, codec='libx264', fps=24, preset='ultrafast')
    return final_clip


def get_clip_top_position(clip, t=None):
    """
    Devuelve la coordenada y (top) del clip en el tiempo t.
    Si .pos es una tupla, devuelve y directamente.
    Si .pos es una función, llama a la función con el tiempo t para obtener y.
    """
    if isinstance(clip.pos, tuple):
        # Si es una tupla, desempaquetar directamente
        _, y = clip.pos
    elif callable(clip.pos):
        # Si es una función, llamar a la función con t para obtener la posición y
        if t is None:
            t = 0  # Por defecto, puedes usar t=0 o cualquier otro valor de tiempo
        _, y = clip.pos(t)
    else:
        raise TypeError("El valor de .pos no es ni una tupla ni una función.")
    return y

# Función principal para generar el video de trivia
# def generate_trivia_video(main_question, voice, background_video_path, logo_path, question_text, question_image, options, correct_option_index, account_text, narration_text, narration_text_winner, tictac_sound_path, ding_sound_path, question_font_path, options_font_path, account_font_path, question_image_font_path):
def generate_trivia_video(main_question, voice, language, ctxVideo, logo_path, question_text, question_image, options, correct_option_index, account_text, narration_text, narration_text_winner, tictac_sound_path, ding_sound_path, question_font_path, options_font_path, account_font_path, question_image_font_path):
    narration_audio_file = f"{SCRIPT_DIR}/public/generados/audios/{uuidcode}.ogg"
    generate_narration(narration_text, narration_audio_file, voice, language)
    narration_audio_file_winner = f"{SCRIPT_DIR}/public/generados/audios/{uuidcode}_winner.ogg"
    generate_narration(narration_text_winner, narration_audio_file_winner, voice, language)
    narration_audio = AudioFileClip(narration_audio_file)
    narration_audio_winner = AudioFileClip(narration_audio_file_winner)

    clock_sound_effects = add_sound_effects(tictac_sound_path, start_time=0, reveal_time=3)
    clock_sound_effects = clock_sound_effects.volumex(0.5)
    video_duration_before_winner = narration_audio.duration + clock_sound_effects.duration
    ding_sound_effects = add_sound_effects(ding_sound_path, start_time=0, reveal_time=2)
    ding_sound_effects = ding_sound_effects.volumex(0.5)
    # video_total_duration = narration_audio.duration + clock_sound_effects.duration + narration_audio_winner.duration
    video_winner_duration = max(narration_audio_winner.duration, ding_sound_effects.duration)
    video_total_duration = narration_audio.duration + clock_sound_effects.duration + max(narration_audio_winner.duration, ding_sound_effects.duration)

    ctxVideo["video_duration"] = video_total_duration

    print(f"[DEBUG] generate_trivia_video - ctxVideo: {ctxVideo}")

    # print(f"[DEBUG] generate_trivia_video - narration_audio.duration: {narration_audio.duration}")
    # print(f"[DEBUG] generate_trivia_video - clock_sound_effects.duration: {clock_sound_effects.duration}")
    # print(f"[DEBUG] generate_trivia_video - ding_sound_effects.duration: {ding_sound_effects.duration}")
    # print(f"[DEBUG] generate_trivia_video - total: {narration_audio.duration + clock_sound_effects.duration + ding_sound_effects.duration}")
    # print(f"[DEBUG] generate_trivia_video - narration_audio_winner.duration: {narration_audio_winner.duration}")
    # print(f"[DEBUG] video_duration_before_winner: {video_duration_before_winner}")
    # print(f"[DEBUG] video_winner_duration: {video_winner_duration}")
    print(f"[DEBUG] generate_trivia_video - video_total_duration: {video_total_duration}")

    # background_clip = create_background_video(background_video_path, duration=video_total_duration)

    # print(f"[DEBUG] background_clip.duration: {background_clip.duration}")
    logo_clip = add_logo(logo_path, ctxVideo)

    print("[DEBUG] generate_trivia_video - logo_clip.w, logo_clip.h:", logo_clip.w, logo_clip.h)

    if (question_image):
        question_clip = add_question_text(main_question, ctxVideo, question_font_path)
    else:
        question_clip = add_question_text(question_text, ctxVideo, question_font_path)

    print("[DEBUG] generate_trivia_video - question_clip.w, question_clip.h:", question_clip.w, question_clip.h)

    # Función para guardar la imagen del emoji
    def save_emoji_image(unicode_text, font_path, font_size, output_path):
        # Cargar la fuente con el tamaño especificado
        font = ImageFont.truetype(font_path, font_size)

        # Calcular el tamaño del texto (emoji) utilizando getbbox
        left, top, right, bottom = font.getbbox(unicode_text)
        text_width = right - left
        text_height = bottom - top

        # Asegúrate de que las dimensiones sean positivas
        text_width = max(1, text_width)
        text_height = max(1, text_height)

        # Crea una nueva imagen con el tamaño del texto
        im = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)

        # Dibuja el emoji en la imagen
        draw.text((-left, -top), unicode_text, font=font, embedded_color=True)

        # Guarda la imagen en un archivo
        im.save(output_path)

    # Condicional para generar el question_image_clip
    if question_image.strip():
        # Generar la imagen del emoji y guardarla
        emoji_image_path = f"{SCRIPT_DIR}/public/generados/images/{uuidcode}_emoji.png"
        save_emoji_image(question_image, question_image_font_path, 137, emoji_image_path)

        # Crear el ImageClip a partir de la imagen guardada
        question_image_clip = ImageClip(emoji_image_path)
        question_image_clip = question_image_clip.set_duration(question_clip.duration)
        question_image_clip = question_image_clip.set_position(('center', question_clip.size[1] + 450))  # Posición debajo del question_clip
    else:
        # Crear un clip vacío si question_image está en blanco
        question_image_clip = TextClip(' ', fontsize=150, color='white')
        question_image_clip = question_image_clip.set_duration(question_clip.duration)
        question_image_clip = question_image_clip.set_position(('center', question_clip.size[1] + 500))  # Posición debajo del question_clip

    print("[DEBUG] generate_trivia_video - question_image_clip.w, question_image_clip.h:", question_image_clip.w, question_image_clip.h)

    print(f"[DEBUG] question_image_clip: {question_image_clip.pos}")

    clip_top_position = get_clip_top_position(question_image_clip)  # Clip es un ImageClip, VideoClip o TextClip

    options_top_margin = clip_top_position + 200

    print(f"[DEBUG] options_top_margin: {options_top_margin}")

    options_clips = add_options(options, ctxVideo, options_font_path, top_margin=options_top_margin) #, reveal_time=4
    # Pasa la fuente de opciones a la función reveal_correct_option
    
    # exit()
    

    options_clips = reveal_correct_option(options_clips, ctxVideo["video_width"], options, correct_option_index, start_time=video_duration_before_winner, reveal_time=video_winner_duration, options_font_path=options_font_path)
    account_clip = add_account_text(account_text, ctxVideo["video_duration"], account_font_path)

    print("[DEBUG] generate_trivia_video - account_clip.w, account_clip.h:", account_clip.w, account_clip.h)

    # Ejemplo de uso
    progress_bar_with_emoji = create_progress_bar_with_emoji(
        duration=clock_sound_effects.duration,      # Duración en segundos
        width=int(ctxVideo["video_width"] * 0.8),         # Ancho del video
        height=0,                                   # Altura inicial del video (no se usa directamente ahora)
        scale_height=0.8,                           # Reducir la altura del video al 80%
        emoji_size=70,                              # Tamaño del emoji
        bar_height=40,                              # Altura de la barra de progreso
        bar_color="yellow",
        bg_color="gray",
        emoji="🚀",
        constant_font_size=137,                     # Tamaño del emoji
        font_path=question_image_font_path,         #"{SCRIPT_DIR}/public/assets/fonts/AppleColorEmoji.ttf"
        proportion=0.85                             # Espacio que ocupa la barra dentro del recuadro
    )

    progress_bar_with_emoji = progress_bar_with_emoji.set_pos(("center", 1575))

    # exit()

    video_clip = compose_video(ctxVideo, video_total_duration, logo_clip, question_clip, question_image_clip, options_clips, account_clip, narration_audio, narration_audio_winner, clock_sound_effects, ding_sound_effects, progress_bar_with_emoji)

    # Limpieza de archivos temporales
    # os.remove(narration_audio_file)
    # os.remove(narration_audio_file_winner)

    return video_clip


# Funcióc para generar un video con múltiples preguntas
def generate_combined_trivia_video(main_question, voice, language, questions_json, background_video_path, background_music_path, logo_path, account_text, tictac_sound_path, ding_sound_path, output_file, question_font_path, options_font_path, account_font_path, question_image_font_path, sessionUUID, sio):
    print("[DEBUG 06]: \n====================\n", "generate_combined_trivia_video -> sio", sio, "\n====================")

    start_time = time.time()  # Inicia el temporizador
    
    logger = MyBarLogger(sessionUUID, sio)

    all_clips = []

    # Definir las dimensiones objetivo
    target_width, target_height = 1080, 1920

    # model_clip = create_background_video(background_video_path, duration=3)

    ctxVideo = {
        "video_width": target_width,
        "video_height": target_height
    }

    for question in questions_json:
        question_text = question['question_text']
        question_image = question['question_image']
        options = question['options']
        correct_option_index = question['correct_option_index']

        narration_text = f"¿{question_text}?"
        narration_text_winner = f"{options[correct_option_index]}!!"

        trivia_clip = generate_trivia_video(
            main_question=main_question,
            voice=voice,
            language=language,
            ctxVideo=ctxVideo,
            logo_path=logo_path,
            question_text=question_text,
            question_image=question_image,
            options=options,
            correct_option_index=correct_option_index,
            account_text=account_text,
            narration_text=narration_text,
            narration_text_winner=narration_text_winner,
            tictac_sound_path=tictac_sound_path,
            ding_sound_path=ding_sound_path,
            question_font_path=question_font_path,
            options_font_path=options_font_path,
            account_font_path=account_font_path,
            question_image_font_path=question_image_font_path
        )

        all_clips.append(trivia_clip)

    # Concatenar los clips de trivia en una secuencia
    trivia_sequence = concatenate_videoclips(all_clips, method="compose")

    # Calcular la duración total de la secuencia de trivia
    total_duration = trivia_sequence.duration

    # Cargar el video de fondo y crear un bucle que dure toda la secuencia de trivia
    background_clip = create_background_video(background_video_path, background_music_path, target_width, target_height, total_duration)

    print("trivia_sequence:", trivia_sequence)

    # Superponer la secuencia de trivia sobre el fondo en bucle
    final_video = CompositeVideoClip([background_clip, trivia_sequence])

    # Guardar el video final
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=12, preset='ultrafast', logger=logger)

    end_time = time.time()  # Detiene el temporizador
    processing_time = end_time - start_time  # Calcula el tiempo de procesamiento

    print(f"Tiempo de procesamiento: {processing_time} segundos")


# Funcióc para generar un video con múltiples preguntas
def ok_generate_combined_trivia_video(main_question, voice, questions_json, background_video_path, logo_path, account_text, tictac_sound_path, ding_sound_path, output_file, question_font_path, options_font_path, account_font_path, question_image_font_path):
    start_time = time.time()  # Inicia el temporizador

    all_clips = []

    for question in questions_json:
        question_text = question['question_text']
        question_image = question['question_image']
        options = question['options']
        correct_option_index = question['correct_option_index']

        narration_text = f"¿{question_text}?"
        narration_text_winner = f"{options[correct_option_index]}!!"
        # narration_text_winner = f"Es, {options[correct_option_index]}!"

        trivia_clip = generate_trivia_video(
            main_question=main_question,
            voice=voice,
            background_video_path=background_video_path,
            logo_path=logo_path,
            question_text=question_text,
            question_image=question_image,
            options=options,
            correct_option_index=correct_option_index,
            account_text=account_text,
            narration_text=narration_text,
            narration_text_winner=narration_text_winner,
            tictac_sound_path=tictac_sound_path,
            ding_sound_path=ding_sound_path,
            question_font_path=question_font_path,
            options_font_path=options_font_path,
            account_font_path=account_font_path,
            question_image_font_path=question_image_font_path
        )

        all_clips.append(trivia_clip)

    for idx, clip in enumerate(all_clips):
        print(f"[DEBUG] all_clips[{idx}] - start: {clip.start}, duration: {clip.duration}, end: {clip.end}")

    # Combinar todos los clips en un solo video
    final_video = concatenate_videoclips(all_clips, method="compose")
    print(f"[DEBUG] generate_combined_trivia_video - final_video.duration: {final_video.duration}")

    # Guardar el video final
    # final_video = final_video.subclip(0, 4)
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=12, preset='ultrafast')

    end_time = time.time()  # Detiene el temporizador
    processing_time = end_time - start_time  # Calcula el tiempo de procesamiento

    print(f"Tiempo de procesamiento: {processing_time} segundos")


def generate_trivias(context, options=1, language="Spanish"):
    # Construye el prompt basado en el contexto y el lenguaje
    prompt = (
        f"Genera {options} {'frases nominales básicas' if options > 1 else 'frase nominal básica'} en idioma {language} {'basadas' if options > 1 else 'basada'} en el siguiente contexto: ['{context}'].\n\n"
        f"{'Los conceptos deben ser oraciones cortas y directas' if options > 1 else 'El concepto debe ser una oración corta y directa'} en idioma {language}. En un arreglo simple en formato JSON.\n"
        'Ejemplos del resultado esperado: {"conceptos": ["Creación del mundo según Génesis", "Matemáticas para niños", "Conjugación del verbo ser o estar en Inglés", "Entrenamiento de fuerza", "Dieta equilibrada", "Ejercicios básicos", "Cálculo de límites", "Historia de los Incas"]}.\n'
        f"IMPORTANTE: Genera el contenido en {language}. Estas expresiones deben ser útiles para que a partir de ellas una IA pueda generar varias preguntas de selección única a manera de trivias."
    )

    # Configura los mensajes para la llamada a OpenAI
    messages = [
        {
            "role": "system",
            "content": "Eres un asistente virtual útil que ayuda a generar conceptos y frases educativas para videos en redes sociales."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    print("====================\n", "prompt:", prompt, "\n====================")

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=1.0,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    
    print("====================\n", "result:", result, "\n====================")

    return json.loads(result)


def generate_quiz_questions(main_question, num_questions=2, num_options=4, language="Spanish"):
    # Genera la lista de opciones
    options_list = [f'"Opción {i+1}"' for i in range(num_options)]

    # Determina si se debe incluir "emoji" en la pregunta
    emoji_included = 'emoji' in main_question.lower()

    # Construye el prompt para la IA
    prompt = (
        f"Genera una {'lista de' if num_questions > 1 else ''} {num_questions} {'preguntas cortas' if num_questions > 1 else 'pregunta corta'} en idioma {language} en formato JSON para un quiz / trivia sobre ['{main_question}']. "
        f"El JSON debe incluir una pregunta principal corta en idioma {language} sin emojis en ella, con el estilo MrBeast en la propiedad 'main_question' que aplique para todas las preguntas de la propiedad 'questions', "
        f"seguido de un arreglo 'questions' que contenga objetos con las siguientes propiedades: "
        f"el texto de la pregunta corta en idioma {language} {'sin emojis en ella' if emoji_included else ''} con variantes {'mencionando siempre el tema central en cada pregunta ' if not emoji_included else ''} para hacer la pronunciación más humana y consistente {'SIN INCLUIR EL EMOJI' if emoji_included else ''}, "
        f"{'una imagen representada como un emoji,' if emoji_included else ''} "
        f"opciones de respuesta en idioma {language} con {num_options} opciones donde alternes la opción correcta en las diferentes posiciones del arreglo de opciones entre 0 y {num_options - 1}, (IMPORTANTE: deben tener un tamaño de 17 caracteres máximo por opción), y el índice de la opción correcta (IMPORTANTE: Las opciones correctas deben estár en posiciones aleatorias entre 0 y {num_options - 1} dentro del arreglo de la propiedad 'options').\n\n"
        f"Aquí hay un ejemplo del formato:\n\n"
        "{\n"
        "  \"main_question\": \"Pregunta principal de ejemplo?\",\n"
        "  \"questions\": [\n"
        "    {\n"
        f"        \"question_text\": \"Variantes de la pregunta de ejemplo?\",\n"
        f"        \"question_image\": \"{'🇩🇴' if emoji_included else ''}\",\n"
        f"        \"options\": {options_list},\n"
        f"        \"correct_option_index\": 2\n"
        "    }\n"
        "  ]\n"
        "} \n\n"
        f"Notas Importantes: "
        f"- Genera todo el contenido en idioma {language}.\n"
        # "- En las opciones distribuye de forma equitativa y no secuencial la asignación de las opciones correctas en posiciones entre 0 y {num_options - 1}.\n"
        "- Asigna las opciones correctas de las preguntas en posiciones aleatorias entre 0 y {num_options - 1}.\n"
        "- Crea todos los campos mencionados en el ejemplo aunque estén en blanco.\n"
        "- REALIZA UNA DOBE VERIFICACION DE LAS OPCIONES CORRECTAS. NO PUEDES COMETER ERRORES.\n"
    )

    # print(prompt)

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f"Eres una útil asistente virtual que ayuda a generar trivias y quizes educativas para videos en redes sociales.",
                },
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

    print(prompt)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=1.0,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content

    return json.loads(result)


def create_video(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio):
    print("[DEBUG 05]: \n====================\n", "create_video -> sio", sio, "\n====================")
    
    # Configura el analizador de argumentos de línea de comandos
    # parser = argparse.ArgumentParser(description="Genera un video de trivia basado en las preguntas del quiz.")
    # parser.add_argument("main_question", type=str, help="La pregunta principal del quiz.")
    # parser.add_argument("num_questions", type=int, help="El número de preguntas en el quiz.")
    # parser.add_argument("num_options", type=int, help="El número de opciones por pregunta.")

    # args = parser.parse_args()

    # Genera el código UUID para el archivo de salida
    # uuidcode = str(uuid.uuid4())
    uuidcode = uuid4

    # print("uuidcode:", uuidcode)

    # Genera las preguntas del quiz usando los argumentos proporcionados
    # trivia = generate_quiz_questions(args.main_question, num_questions=args.num_questions, num_options=args.num_options)
    trivia = generate_quiz_questions(main_question, num_questions, num_options, language)

    print(trivia)
    
    final_logo_path = logo_path or f"{SCRIPT_DIR}/public/assets/images/logo.png"
    final_account_text = account_text or "@elclubdelosgenios"
    
    print("final_logo_path:", final_logo_path)
    print("final_account_text:", final_account_text)

    # Genera el video combinado de la trivia
    generate_combined_trivia_video(
        main_question=trivia["main_question"],
        voice=voice,
        language=language,
        questions_json=trivia["questions"],
        background_video_path=f"{SCRIPT_DIR}/public/assets/videos/{background_video}.mp4",
        background_music_path=f"{SCRIPT_DIR}/public/assets/music/{background_music}.mp3",
        logo_path=final_logo_path,
        account_text=final_account_text,
        tictac_sound_path=f"{SCRIPT_DIR}/public/assets/audios/clock.mp3",
        ding_sound_path=f"{SCRIPT_DIR}/public/assets/audios/ding.mp3",
        output_file=f"{SCRIPT_DIR}/public/generados/videos/{uuidcode}.mp4",
        question_font_path=f"{SCRIPT_DIR}/public/assets/fonts/TT-Milks-Casual-Pie-Trial-Base.otf",
        options_font_path=f"{SCRIPT_DIR}/public/assets/fonts/Sniglet-Regular.ttf",
        account_font_path=f"{SCRIPT_DIR}/public/assets/fonts/Sniglet-Regular.ttf",
        question_image_font_path=f"{SCRIPT_DIR}/public/assets/fonts/AppleColorEmoji.ttf",
        sessionUUID=sessionUUID,
        sio=sio
    )

    # Opcional: Imprime el JSON de la trivia
    # print(json.dumps(trivia, indent=4, ensure_ascii=False))

# if __name__ == "__main__":
#     main()

class MyBarLogger(ProgressBarLogger):
    def __init__(self, session_uuid, sio):
        super().__init__()
        self.session_uuid = session_uuid
        self.sio = sio

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percentage = (value / total) * 100
        else:
            percentage = 0
            
        print("[DEBUG 07]: \n====================\n", "MyBarLogger -> bars_callback -> self.sio", self.sio, "self.session_uuid", self.session_uuid, "\n====================")

        # participants = self.sio.server.manager.get_participants('/')
        
        # print("[DEBUG 08]: \n====================\n", "MyBarLogger -> participants:", participants, "\n====================")

        # Asegúrate de que el cliente esté conectado
        # if sid in self.sio.server.manager.get_participants('/'):
            # self.sio.emit('response', {'message': "hola"}, room=sid)
        # else:
            # print(f"Cliente con SID {sid} no está conectado.")

        # Emitir el progreso con el UUID para identificar la sesión
        response = self.sio.emit('video_progress', {'uuid': self.session_uuid, 'progress': percentage})

        print({'uuid': self.session_uuid, 'sio': self.sio, 'progress': percentage, "response": response})

        print(f'{bar} {attr} {percentage:.2f}%')


def create_video_main(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio):
    # data = [{'url': 'https://www.kayak.com/rimg/himg/17/76/2c/booking-3989982-257263533-043832.jpg', 'description': 'A luxurious, well-lit house with arched windows, a grand entrance, and a gated courtyard surrounded by lush greenery and tall trees.'}, {'url': 'https://www.kayak.com/rimg/himg/97/73/c7/booking-3989982-257263588-299448.jpg', 'description': 'A grand staircase with ornate railings and statues leads to an upper level in an elegant, spacious interior with warm-toned walls and decorative elements.'}, {'url': 'https://www.kayak.com/rimg/himg/21/16/65/booking-3989982-257263572-216394.jpg', 'description': 'A spacious, well-lit kitchen with modern appliances, granite countertops, dark cabinetry, and an arched entryway leading to a grand hallway.'}, {'url': 'https://www.kayak.com/rimg/himg/50/e3/c8/booking-3989982-257263543-083612.jpg', 'description': 'A luxurious bedroom features a four-poster bed, a cozy seating area with ornate furniture, a large TV, and eclectic decor including a plush rug and animal figurines.'}, {'url': 'https://www.kayak.com/rimg/himg/f1/0f/8b/booking-3989982-257263555-150000.jpg', 'description': 'A cozy, well-decorated living room features a fireplace, elegant seating, framed artwork, and a floor lamp with multiple globes.'}, {'url': 'https://www.kayak.com/rimg/himg/36/10/ec/booking-3989982-257263552-131976.jpg', 'description': 'The image shows a luxurious bathroom featuring a large glass-enclosed shower and a separate bathtub area with arched windows and elegant tile work.'}, {'url': 'https://www.kayak.com/rimg/himg/14/cd/e2/booking-3989982-257263561-169186.jpg', 'description': 'A luxurious dining room with ornate furniture, a chandelier, medieval shields on the wall, and a classical statue in an alcove.'}, {'url': 'https://www.kayak.com/rimg/himg/8a/ee/e5/booking-3989982-257263570-205725.jpg', 'description': 'A serene pool area with a small waterfall, decorative bridge, and lush greenery under a purple-hued sky.'}, {'url': 'https://www.kayak.com/rimg/himg/ed/f0/4a/booking-3989982-257263582-272624.jpg', 'description': 'A serene outdoor spa area features a small pool with pink lighting, surrounded by tropical plants, a waterfall, and a classical statue under a pergola.'}, {'url': 'https://www.kayak.com/rimg/himg/13/93/3a/booking-3989982-257263567-188337.jpg', 'description': 'The image shows an outdoor patio area with a pergola, equipped with a ceiling fan, string lights, a barbecue grill, and metal patio furniture.'}]
    # create_property_name_audio(download_path, property_name)
    # num_elements, thumb_filename = process_images_and_audios(data, voz, download_path, uuid4)

    sio.emit('greeting', {'uuid': sessionUUID, 'progress': "hola"})

    print("[DEBUG 04]: \n====================\n", "create_video_main -> sio", sio, "\n====================")

    # participants = sio.server.manager.get_participants('/')
        
    # print("[DEBUG 08]: \n====================\n", "MyBarLogger -> participants:", participants, "\n====================")
    # exit()

    print("---------------------------------------------------")
    print("uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video:", uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio)
    print("---------------------------------------------------")

    create_video(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio)

    return True
