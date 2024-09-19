from spotted import create_app
import socket
import os

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

app = create_app()

debug = os.getenv("FLASK_ENV") != "main"

if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0')
