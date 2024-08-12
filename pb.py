from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, ImageClip, CompositeVideoClip
import numpy as np

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

def create_progress_bar_with_emoji(duration, width=800, height=100, scale_height=0.8, emoji_size=100, bar_height=100, bar_color="green", bg_color="black", emoji="🚀", constant_font_size=137, font_path="path_to_your_font.ttf"):
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
    content_width = int(width * 0.8)
    margin = (width - content_width) // 2  # Espacio en blanco a los lados

    def make_frame(t):
        # Crear una imagen de fondo con color sólido
        img = np.full((bar_height, content_width, 3), bg_color_rgb, dtype=np.uint8)
        
        # Calcular el ancho del progress bar basado en el tiempo t y la duración total
        bar_width = int((t / duration) * content_width)
        
        # Rellenar el progress bar
        img[:, :bar_width] = bar_color_rgb
        
        return img

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

# Ejemplo de uso
duration = 10  # Duración de 10 segundos
progress_bar_with_emoji = create_progress_bar_with_emoji(
  duration, 
  width=800,         # Ancho del video
  height=0,          # Altura inicial del video (no se usa directamente ahora)
  scale_height=1,    # Reducir la altura del video al 80%
  emoji_size=50,    # Tamaño del emoji 
  bar_height=30,     # Altura de la barra de progreso
  bar_color="yellow", 
  bg_color="gray", 
  emoji="🚀", 
  constant_font_size=137,     # Tamaño del emoji 
  font_path="./assets/fonts/AppleColorEmoji.ttf"
)

# Guardar el video o previsualizarlo
progress_bar_with_emoji.write_videofile("progress_bar_with_emoji.mp4", fps=24)
