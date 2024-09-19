from uuid import uuid4 as _uuid
from flask import Blueprint, request, jsonify
import openai
import os
from dotenv import load_dotenv

chatgpt_bp = Blueprint("chatgpt_bp", __name__)
openai.api_key = os.getenv("GPT_KEY")


def uuid(): return str(_uuid())


@chatgpt_bp.route("", methods=["POST"])
def check_message():
    data = request.json

    text = data.get("text", None)
    if not text:  # Check if text field is empty or not provided
        return "Text field is missing or empty.", 400

    if len(text) > 450:
        return "Text length exceeds the maximum limit of 450 characters.", 400

    try:
        chatgpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Non permettere parolacce, bestemmie, linguaggio offensivo, linguaggio d'odio, insulti, offese, minacce, ricatti, richieste di pubblicità, sponsor, link a siti o parlare di temi politici. In base a queste regole, controlla il seguente testo: {text}",
                }
            ],
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Rispondi esplicitamente solo con 'Si' (se il messaggio è appropriato) o 'No' (se il messaggio contiene contenuti non consentiti) senza specificare altro. Assicurati di rilevare e bloccare eventuali parolacce mascherate, bestemmie mascherate o qualsiasi altro linguaggio offensivo, linguaggio d'odio, insulti, offese, minacce, ricatti, richieste di pubblicità, sponsor, link o parlare di temi politici. In base a queste regole, controlla il seguente testo: {text}",
                }
            ],
        )

        chatgpt_entire_response = chatgpt_response.choices[0].message.content.strip()
        sentiment = response.choices[0].message.content.strip().lower()

        return jsonify({"result": sentiment, "chatgpt": chatgpt_entire_response }), 200
    except Exception as e:
        # Return the error message and 500 status code in case of API or parsing errors
        return jsonify({"error": e}), 500