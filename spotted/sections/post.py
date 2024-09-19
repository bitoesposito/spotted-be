import os
from uuid import uuid4 as _uuid
from flask import Blueprint, request, jsonify
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

def uuid(): return str(_uuid())


post_bp = Blueprint('post_bp', __name__)


def wrap_text(text, font, max_width):
    wrapped_lines = []
    for line in text.split('\n'):
        if font.getsize(line)[0] <= max_width:
            wrapped_lines.append(line)
        else:
            words = line.split(' ')
            new_line = words[0]
            for word in words[1:]:
                if font.getsize(new_line + ' ' + word)[0] <= max_width:
                    new_line += ' ' + word
                else:
                    wrapped_lines.append(new_line)
                    new_line = word
            wrapped_lines.append(new_line)
    return wrapped_lines


def add_centered_text(image_path, text, font_path, font_size, text_color, file_name):
    image = Image.open(image_path)
    width, height = image.size

    font = ImageFont.truetype(font_path, font_size)

    draw = ImageDraw.Draw(image)

    max_text_width = width - 200

    wrapped_text = wrap_text(text, font, max_text_width)

    line_height = 50

    text_height = len(wrapped_text) * line_height

    y_start = (height - text_height) // 2

    for line in wrapped_text:
        line_width, _ = font.getsize(line)
        x_start = (width - line_width) // 2
        draw.text((x_start, y_start), line, font=font, fill=text_color)
        y_start += line_height

    image.save(f'./data/{file_name}.jpeg', 'JPEG')


@post_bp.route('', methods=['POST'])
def post_route():

    data = request.json

    text = data.get('text', None)
    if text is None:
        return "", 400

    if len(text) > 450:
        return "", 400

    image_path = './spotted/assets/post-bg.jpg'
    # Sostituisci con il percorso del tuo file di font
    font_path = './spotted/assets/font/BC_Falster_Grotesk_Bold.otf'
    font_size = 45
    # Colore del testo in formato RGB (nero in questo caso)
    text_color = (59, 130, 246)
    file_name = uuid()

    add_centered_text(image_path, text.upper(), font_path,
                      font_size, text_color, file_name)

    username = os.getenv("IG_USER_ID")
    password = os.getenv("IG_USER_PASS")

    cl = Client()
    cl.delay_range = [1, 3]
    
    session = None
    if os.path.exists("session.json"):
        session = cl.load_settings("session.json")

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(username, password)

            try:
                cl.get_timeline_feed()
            except LoginRequired:
                old_session = cl.get_settings()
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(username, password)

            login_via_session = True
        except Exception as e:
            pass

    if not login_via_session:
        try:
            if cl.login(username, password):
                login_via_pw = True
        except:
            pass

    if not login_via_pw and not login_via_session:
        print("Could not login to instagram!")
    else:
        if not os.path.exists("session.json"):
            cl.dump_settings("session.json")

        cl.photo_upload(f'./data/{file_name}.jpeg', "La vita di tutti i giorni, ma in anonimo!\nSpotta anche tu tramite il sito o l'app.\n•\n•\n•\n#spotted")
        os.remove(f'./data/{file_name}.jpeg')

    return "", 200
