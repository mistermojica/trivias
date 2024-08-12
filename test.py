theme = "banderas de países identificadas por emoji"
num_options = 4

# Genera la lista de opciones
options_list = [f'"Opción {i+1}"' for i in range(num_options)]

prompt = (
    f"Genera una lista de preguntas en formato JSON para un quiz / trivia sobre '{theme}'. Cada pregunta debe incluir: "
    f"el texto de la pregunta, {'una imagen representada como un emoji,' if 'emoji' in theme.lower() else ''} "
    f"opciones de respuesta con {num_options} opciones, "
    "y el índice de la opción correcta. Aquí hay un ejemplo del formato:\n\n"
    "[\n"
    "    {\n"
    f"        \"question_text\": \"Pregunta de ejemplo?\",\n"
    f"        \"question_image\": \"{'🇩🇴' if 'emoji' in theme.lower() else ''}\",\n"
    f"        \"options\": {options_list},\n"
    f"        \"correct_option_index\": 0\n"
    "    }\n"
    "]"
)

print(prompt)