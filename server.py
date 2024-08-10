import http.server
import socketserver
import os

# Define el puerto en el que el servidor va a escuchar
PORT = 8787

# Define el directorio que se va a servir
DIRECTORY = "./videos"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

# Configura el servidor
with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Serving HTTP on port {PORT} (http://localhost:{PORT})")
    print(f"Serving directory: {os.path.abspath(DIRECTORY)}")
    httpd.serve_forever()
