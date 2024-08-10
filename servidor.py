import http.server
import socketserver
import os
from datetime import datetime
import mimetypes

# Define el puerto en el que el servidor va a escuchar
PORT = 8787

# Define el directorio que se va a servir
DIRECTORY = "./videos"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(directory=DIRECTORY, *args, **kwargs)

    def list_directory(self, path):
        try:
            # Obtener la lista de archivos en el directorio
            file_list = os.listdir(path)
        except os.error:
            self.send_error(http.HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None

        # Obtener la ruta completa de los archivos y ordenarlos por fecha de creación en orden descendente
        file_list = [os.path.join(path, file) for file in file_list]
        file_list.sort(key=lambda file: os.path.getctime(file), reverse=True)

        # Construir la respuesta HTML con Bootstrap, Font Awesome y cards
        response = f"""
        <html>
        <head>
            <title>Videos Generados</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
            <style>
                .card {{
                    margin-bottom: 20px;
                }}
                .card-body {{
                    padding: 10px;
                }}
                .card-title {{
                    font-size: 1rem;
                    margin-bottom: 5px;
                }}
                .btn {{
                    padding: 5px 10px;
                    font-size: 1.2rem;
                }}
                .video-container {{
                    position: relative;
                    padding-bottom: 56.25%;
                    height: 0;
                }}
                .video-container iframe, .video-container video {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2 class="mt-4">Videos Generados</h2>
                <hr>
                <div class="row">
        """

        for index, file in enumerate(file_list):
            display_name = link_name = os.path.basename(file)
            file_time = datetime.fromtimestamp(os.path.getctime(file)).strftime('%Y-%m-%d %H:%M:%S')
            file_size_mb = round(os.path.getsize(file) / (1024 * 1024), 2)  # Convertir a MB y redondear a 2 decimales
            file_duration = "Unknown duration"  # Placeholder for video duration
            if not os.path.isdir(file) and mimetypes.guess_type(file)[0].startswith('video'):
                file_duration = self.get_video_duration(file)
            
            response += f"""
                <div class="col-12 col-sm-6 col-md-4">
                    <div class="card">
                        <div class="video-container">
                            <video class="card-img-top" controls>
                                <source src="{link_name}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">{display_name}</h5>
                            <p class="card-text"><small class="text-muted">Created: {file_time}</small></p>
                            <p class="card-text"><small class="text-muted">Duration: {file_duration}</small></p>
                            <p class="card-text"><small class="text-muted">Size: {file_size_mb} MB</small></p>
                            <a href="#" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#videoModal{index}">
                                <i class="fas fa-play"></i>
                            </a>
                            <a href="{link_name}" class="btn btn-success" download>
                                <i class="fas fa-download"></i>
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Modal -->
                <div class="modal fade" id="videoModal{index}" tabindex="-1" aria-labelledby="videoModalLabel{index}" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="videoModalLabel{index}">{display_name}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="video-container">
                                    <video controls>
                                        <source src="{link_name}" type="video/mp4">
                                        Your browser does not support the video tag.
                                    </video>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """

        response += """
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """

        encoded = response.encode("utf-8", "surrogateescape")
        
        # Configuración de los encabezados HTTP y envío del contenido
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

    def get_video_duration(self, filepath):
        # Aquí puedes implementar una función que extraiga la duración del video usando una librería como ffmpeg o similar.
        # Este método es un placeholder.
        return "00:00:00"

# Configura el servidor
with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Serving HTTP on port {PORT} (http://localhost:{PORT})")
    print(f"Serving directory: {os.path.abspath(DIRECTORY)}")
    httpd.serve_forever()
