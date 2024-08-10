from PIL import Image, ImageDraw, ImageFont

# Emoji de la bandera (República Dominicana)
unicode_text = "\U0001F1E9\U0001F1F4"

# Información de la fuente y tamaño del emoji
font_info = {
    'appleemoji': [r"./assets/fonts/AppleColorEmoji.ttf", 137]
}

for i, item in enumerate(font_info.items()):
    path, size = item[1]
    font = ImageFont.truetype(path, size)
    
    # Calcula el tamaño del texto (emoji) utilizando getbbox
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
    im.save(f"./images/output_image_{item[0]}.png")
