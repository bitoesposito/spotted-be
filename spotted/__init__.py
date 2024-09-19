from flask import Flask, request
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "./uploads"

    # Configura CORS per consentire richieste da qualsiasi origine
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            return "", 200

    with app.app_context():
        from spotted.sections.post import post_bp
        from spotted.sections.chatgpt import chatgpt_bp

        app.register_blueprint(post_bp, url_prefix='/post')
        app.register_blueprint(chatgpt_bp, url_prefix="/chatgpt")

    return app