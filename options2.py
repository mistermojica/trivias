def add_options2(options, video_clip, options_font_path, correct_option_index, start_time, margin=170, top_margin=1000):
    option_clips = []
    first_option_pos = top_margin
    option_space = 170
    y_positions = [first_option_pos, first_option_pos + option_space, first_option_pos + (option_space * 2)]

    # Configuración de estilo
    circle_radius = int(40 * 1.5)  # Aumentar el radio del círculo en un 30%
    circle_color = '#6A5ACD'  # Color del círculo en formato hexadecimal (Lavender)
    option_bg_color = '#FFFFFF'  # Fondo blanco para las opciones
    correct_option_bg_color = 'yellow'  # Fondo amarillo para la opción correcta
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

        # Comprobar si la opción es la correcta y crear el fondo amarillo si es necesario
        if i == correct_option_index:
            correct_bg_image = Image.new("RGBA", (bg_width, option_bg_height), (255, 255, 255, 0))
            correct_rounded_rectangle = Image.new("RGBA", (bg_width, option_bg_height), correct_option_bg_color)
            correct_mask = Image.new("L", (bg_width, option_bg_height), 0)
            correct_mask_draw = ImageDraw.Draw(correct_mask)
            correct_mask_draw.rounded_rectangle([(0, 0), (bg_width, option_bg_height)], corner_radius, fill=255)
            correct_bg_image = Image.composite(correct_rounded_rectangle, correct_bg_image, correct_mask)

            # Convertir el fondo redondeado amarillo a ImageClip
            correct_bg_array = np.array(correct_bg_image)
            correct_option_bg_clip = ImageClip(correct_bg_array).set_duration(video_clip.duration).set_position((margin + 10, y_positions[i] + 1)).set_start(start_time)

            # Componer la opción final con fondo blanco y luego fondo amarillo
            composed_clip = CompositeVideoClip(
                [option_bg_clip, circle_clip, label_clip, option_text_clip, correct_option_bg_clip],
                size=(video_clip.w, video_clip.h)
            )
        else:
            # Componer la opción final solo con fondo blanco
            composed_clip = CompositeVideoClip([option_bg_clip, circle_clip, label_clip, option_text_clip], size=(video_clip.w, video_clip.h))

        # Añadir el clip compuesto a la lista de clips de opciones
        option_clips.append(composed_clip)

    return option_clips