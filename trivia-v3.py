import os
from moviepy.editor import concatenate_videoclips, VideoFileClip, ImageClip, TextClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from moviepy.video.fx.all import fadein, fadeout
import boto3
import time
import uuid
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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
    print(f"[DEBUG] add_options - video_clip.duration: {video_clip.duration}")
    
    option_clips = []
    first_option_pos = top_margin
    option_space = 170

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

        option_text_clip.text = option

        # Componer la opción final
        composed_clip = CompositeVideoClip([option_bg_clip, circle_clip, label_clip, option_text_clip], size=(video_clip.w, video_clip.h))
        option_clips.append(composed_clip)

    return option_clips

# Revelar la opción correcta
def reveal_correct_option(options_clips, video_clip, options, correct_option_index, start_time, reveal_time, options_font_path, margin=80):
    print(f"[DEBUG] Opciones: {options}")
    print(f"[DEBUG] Clips de Opciones: {options_clips}")
    print(f"[DEBUG] Índice de Opción Correcta: {correct_option_index}")
    print(f"[DEBUG] reveal_correct_option - video_clip.duration: {video_clip.duration}")
    print(f"[DEBUG] reveal_correct_option - start_time: {start_time}")
    print(f"[DEBUG] reveal_correct_option - reveal_time: {reveal_time}")

    # Obtener el texto de la opción correcta desde el arreglo
    correct_option_text = options[correct_option_index]
    print(f"[DEBUG] Texto de Opción Correcta: {correct_option_text}")

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
    bg_width = video_clip.w - 2 * margin

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

    
    print(f"[DEBUG] correct_option_bg_clip.w: {correct_option_bg_clip.w}")
    print(f"[DEBUG] correct_option_bg_clip.h: {correct_option_bg_clip.h}")
    print(f"[DEBUG] composite_clip.w: {composite_clip.w}")
    print(f"[DEBUG] composite_clip.h: {composite_clip.h}")
    # if callable(correct_option_bg_clip.pos):
    #     # Si es una función, obtén la posición para el primer frame (por ejemplo)
    #     first_frame_pos = correct_option_bg_clip.pos(0)  # Aquí el "0" representa el primer frame
    #     print(f"[DEBUG] correct_option_bg_clip first_frame_pos: {first_frame_pos}")
        
    #     # Si quieres desglosar los valores x e y
    #     x_pos, y_pos = first_frame_pos
    #     print(f"[DEBUG] correct_option_bg_clip x_pos: {x_pos}, y_pos: {y_pos}")
    # else:
    #     # Si es una tupla, simplemente la desglosas como antes
    #     x_pos, y_pos = correct_option_bg_clip.pos
    #     print(f"[DEBUG] correct_option_bg_clip x_pos: {x_pos}, y_pos: {y_pos}")
    # x_pos, y_pos = composite_clip.pos
    # print(f"[DEBUG] composite_clip x_pos: {x_pos}, y_pos: {y_pos}")
    
    # Actualizar la lista de clips de opciones con el nuevo clip compuesto para la opción correcta
    options_clips[correct_option_index] = new_composed_clip

    return options_clips

# Añadir el texto de la cuenta
def add_account_text(account_text, video_clip, account_font_path):
    account_clip = (TextClip(account_text, fontsize=50, color='white', font=account_font_path)
                    .set_duration(video_clip.duration)
                    .set_pos(("center", 1700)))
    return account_clip

# Añadir efectos de sonido
def add_sound_effects(tictac_sound_path, start_time, reveal_time):
    tictac_sound = AudioFileClip(tictac_sound_path).subclip(start_time, reveal_time)
    return tictac_sound

# Componer el video final
def compose_video(video_total_duration, background_clip, logo_clip, question_clip, question_image_clip, options_clips, account_clip, narration_audio, narration_audio_winner, sound_effects):
    final_clip = CompositeVideoClip([background_clip.set_start(0), logo_clip.set_start(0), question_clip.set_start(0), question_image_clip.set_start(0), *options_clips, account_clip.set_start(0)])
    final_clip.set_duration(video_total_duration)
    print(f"[DEBUG] final_clip.duration 1: {final_clip.duration}")
    for idx, clip in enumerate(options_clips):
        print(f"[DEBUG] options_clips[{idx}] - start: {clip.start}, duration: {clip.duration}, end: {clip.end}")
    
    # final_audio = CompositeAudioClip([narration_audio.set_start(0), sound_effects.set_start(narration_audio.duration)])
    final_audio = CompositeAudioClip([
        narration_audio.set_start(0), 
        sound_effects.set_start(narration_audio.duration),
        narration_audio_winner.set_start(narration_audio.duration + sound_effects.duration)
    ])
    
    print(f"[DEBUG] narration_audio.duration: {narration_audio.duration}")
    print(f"[DEBUG] sound_effects.duration: {sound_effects.duration}")
    print(f"[DEBUG] narration_audio.duration + sound_effects.duration: {narration_audio.duration + sound_effects.duration}")
    print(f"[DEBUG] final_audio.duration: {final_audio.duration}")
    
    final_clip = final_clip.set_audio(final_audio)
    print(f"[DEBUG] final_clip.duration 2: {final_clip.duration}")
    
    # final_clip = final_clip.subclip(0, 4)
    # final_clip.write_videofile(output_file, codec='libx264', fps=24, preset='ultrafast')
    # final_clip.write_videofile(output_file, codec='libx264', fps=24, preset='ultrafast')
    return final_clip

# Función principal para generar el video de trivia
def generate_trivia_video(background_video_path, logo_path, question_text, question_image, options, correct_option_index, account_text, narration_text, narration_text_winner, tictac_sound_path, question_font_path, options_font_path, account_font_path, question_image_font_path):
    uuidcode = str(uuid.uuid4())  # Genera un UUID único para archivos temporales
    narration_audio_file = f"./audios/{uuidcode}.mp3"
    generate_narration(narration_text, narration_audio_file, "Lupe")
    narration_audio_file_winner = f"./audios/{uuidcode}_winner.mp3"
    generate_narration(narration_text_winner, narration_audio_file_winner, "Lupe")
    narration_audio = AudioFileClip(narration_audio_file)
    narration_audio_winner = AudioFileClip(narration_audio_file_winner)
    
    sound_effects = add_sound_effects(tictac_sound_path, start_time=0, reveal_time=3)
    video_duration_before_winner = narration_audio.duration + sound_effects.duration
    video_total_duration = narration_audio.duration + sound_effects.duration + narration_audio_winner.duration
    video_winner_duration = narration_audio_winner.duration
    print(f"[DEBUG] video_duration_before_winner: {video_duration_before_winner}")
    print(f"[DEBUG] video_winner_duration: {video_winner_duration}")
    print(f"[DEBUG] total_duration: {video_total_duration}")
    background_clip = create_background_video(background_video_path, duration=video_total_duration)
    print(f"[DEBUG] background_clip.duration: {background_clip.duration}")
    logo_clip = add_logo(logo_path, background_clip)
    question_clip = add_question_text(question_text, background_clip, question_font_path)
    
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
        emoji_image_path = f"./images/{uuidcode}_emoji.png"
        save_emoji_image(question_image, question_image_font_path, 137, emoji_image_path)
        
        # Crear el ImageClip a partir de la imagen guardada
        question_image_clip = ImageClip(emoji_image_path)
        question_image_clip = question_image_clip.set_duration(question_clip.duration)
        question_image_clip = question_image_clip.set_position(('center', question_clip.size[1] + 500))  # Posición debajo del question_clip
    else:
        # Crear un clip vacío si question_image está en blanco
        question_image_clip = TextClip(' ', fontsize=150, color='white')
        question_image_clip = question_image_clip.set_duration(question_clip.duration)
        question_image_clip = question_image_clip.set_position(('center', question_clip.size[1] + 500))  # Posición debajo del question_clip
    
    options_clips = add_options(options, background_clip, options_font_path) #, reveal_time=4
    # Pasa la fuente de opciones a la función reveal_correct_option
    options_clips = reveal_correct_option(options_clips, background_clip, options, correct_option_index, start_time=video_duration_before_winner, reveal_time=video_winner_duration, options_font_path=options_font_path)
    account_clip = add_account_text(account_text, background_clip, account_font_path)

    # exit()

    video_clip = compose_video(video_total_duration, background_clip, logo_clip, question_clip, question_image_clip, options_clips, account_clip, narration_audio, narration_audio_winner, sound_effects)

    # Limpieza de archivos temporales
    # os.remove(narration_audio_file)
    # os.remove(narration_audio_file_winner)
    
    return video_clip


def generate_trivia_video2(background_video_path, logo_path, question_text, question_image, options, correct_option_index, account_text, narration_text, narration_text_winner, tictac_sound_path, question_font_path, options_font_path, account_font_path):
    narration_audio_file = f"./audios/{uuidcode}.mp3"
    generate_narration(narration_text, narration_audio_file, "Lupe")
    narration_audio_file_winner = f"./audios/{uuidcode}_winner.mp3"
    generate_narration(narration_text_winner, narration_audio_file_winner, "Lupe")
    narration_audio = AudioFileClip(narration_audio_file)
    narration_audio_winner = AudioFileClip(narration_audio_file_winner)
    
    sound_effects = add_sound_effects(tictac_sound_path, start_time=0, reveal_time=3)
    video_duration_before_winner = narration_audio.duration + sound_effects.duration
    video_total_duration = narration_audio.duration + sound_effects.duration + narration_audio_winner.duration
    video_winner_duration = narration_audio_winner.duration
    print(f"[DEBUG] video_duration_before_winner: {video_duration_before_winner}")
    print(f"[DEBUG] video_winner_duration: {video_winner_duration}")
    print(f"[DEBUG] total_duration: {video_total_duration}")
    background_clip = create_background_video(background_video_path, duration=video_total_duration)
    print(f"[DEBUG] background_clip.duration: {background_clip.duration}")
    logo_clip = add_logo(logo_path, background_clip)
    question_clip = add_question_text(question_text, background_clip, question_font_path)
    options_clips = add_options(options, background_clip, options_font_path) #, reveal_time=4
    # Pasa la fuente de opciones a la función reveal_correct_option
    options_clips = reveal_correct_option(options_clips, background_clip, options, correct_option_index, start_time=video_duration_before_winner, reveal_time=video_winner_duration, options_font_path=options_font_path)
    account_clip = add_account_text(account_text, background_clip, account_font_path)

    # exit()

    video_clip = compose_video(video_total_duration, background_clip, logo_clip, question_clip, options_clips, account_clip, narration_audio, narration_audio_winner, sound_effects)

    # Limpieza de archivos temporales
    # os.remove(narration_audio_file)
    # os.remove(narration_audio_file_winner)
    
    return video_clip

# Función para generar un video con múltiples preguntas
def generate_combined_trivia_video(questions_json, background_video_path, logo_path, account_text, tictac_sound_path, ding_sound_path, output_file, question_font_path, options_font_path, account_font_path, question_image_font_path):
    start_time = time.time()  # Inicia el temporizador
    
    all_clips = []
    
    for question in questions_json:
        question_text = question['question_text']
        question_image = question['question_image']
        options = question['options']
        correct_option_index = question['correct_option_index']
        
        narration_text = f"¿{question_text}?"
        narration_text_winner = f"Es, {options[correct_option_index]}!"
        
        trivia_clip = generate_trivia_video(
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
    final_video = final_video.subclip(0, 10)
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
    
    end_time = time.time()  # Detiene el temporizador
    processing_time = end_time - start_time  # Calcula el tiempo de procesamiento

    print(f"Tiempo de procesamiento: {processing_time} segundos")


# Ejemplo de uso con JSON de entrada
questions_json = [
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐶",
        "options": ["Dog", "Cat", "Rabbit", "Mouse"],
        "correct_option_index": 0
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐱",
        "options": ["Dog", "Cat", "Rabbit", "Mouse"],
        "correct_option_index": 1
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐭",
        "options": ["Dog", "Cat", "Rabbit", "Mouse"],
        "correct_option_index": 3
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐰",
        "options": ["Dog", "Cat", "Rabbit", "Mouse"],
        "correct_option_index": 2
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐻",
        "options": ["Bear", "Lion", "Tiger", "Elephant"],
        "correct_option_index": 0
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐼",
        "options": ["Bear", "Lion", "Tiger", "Panda"],
        "correct_option_index": 3
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🦁",
        "options": ["Bear", "Lion", "Tiger", "Elephant"],
        "correct_option_index": 1
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐯",
        "options": ["Bear", "Lion", "Tiger", "Elephant"],
        "correct_option_index": 2
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🐘",
        "options": ["Bear", "Lion", "Tiger", "Elephant"],
        "correct_option_index": 3
    },
    {
        "question_text": "¿Cuál es la palabra en inglés para este emoji? 🦊",
        "options": ["Fox", "Wolf", "Dog", "Cat"],
        "correct_option_index": 0
    }
]

generate_combined_trivia_video(
    questions_json=questions_json,
    background_video_path="./assets/videos/background1.mp4",
    logo_path="./assets/images/logo.png",
    account_text="@elclubdelosgenios",
    tictac_sound_path="./assets/audios/clock.mp3",
    ding_sound_path="./assets/audios/ding.mp3",
    output_file=f"./videos/{uuidcode}.mp4",
    question_font_path="./assets/fonts/TT-Milks-Casual-Pie-Trial-Base.otf",
    options_font_path="./assets/fonts/Sniglet-Regular.ttf",
    account_font_path="./assets/fonts/Sniglet-Regular.ttf",
    question_image_font_path="./assets/fonts/AppleColorEmoji.ttf"
    
)