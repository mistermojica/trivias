from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# Crear un clip de color para simular el clip de fondo inicial
background_clip = ColorClip(size=(640, 480), color=(0, 128, 255)).set_duration(20)  # Azul

# Crear un clip de color para simular el clip de fondo que reemplazará al inicial
overlay_clip = ColorClip(size=(640, 480), color=(255, 128, 0)).set_duration(10).set_start(10)  # Naranja

# Crear un clip de texto
txt_clip = TextClip("Hello, World!", fontsize=70, color='white')
txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(10).set_start(5)

# Crear un clip de texto para emular una imagen con un emoji
image_clip = TextClip("😊", fontsize=200, color='white')
image_clip = image_clip.set_duration(5).set_start(15).set_pos(('center', 'center'))

# Asegurarse de que todos los clips tengan la misma resolución y fps
overlay_clip = overlay_clip.set_fps(24)
txt_clip = txt_clip.set_fps(24)
image_clip = image_clip.set_fps(24)

# Combinar los clips
final_clip = CompositeVideoClip([background_clip, overlay_clip, txt_clip, image_clip])

# Guardar el video final
final_clip.write_videofile("final_output.mp4", codec="libx264", fps=24)