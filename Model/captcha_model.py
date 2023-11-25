from Utils.database import cursor
from flask import make_response, send_file
import string
from io import BytesIO
from captcha.image import ImageCaptcha
import random
import uuid

class captcha_model:
    def __init__(self):
        self.cur = cursor
    
    def new_model(self):
        captcha_length = 5
        captcha_characters = string.ascii_letters + string.digits
        captcha_text = ''.join(random.choice(captcha_characters) for _ in range(captcha_length))
        image = ImageCaptcha(width=250, height=90, fonts=['assets/fonts/roman.ttf'])
        captcha_image = image.generate(captcha_text)
        hash_value = uuid.uuid4().hex
        self.cur.execute(f"INSERT INTO captcha(hash,text) VALUES('{hash_value}','{captcha_text}')")
        captcha_image = BytesIO(captcha_image.read())
        captcha_image.seek(0)
        response = make_response(send_file(captcha_image,mimetype="image/png"))
        response.headers["hash"] = hash_value
        return response
    
    def match_model(self,data):
        self.cur.execute(f"SELECT * FROM captcha WHERE hash='{data.hash}'")
        result = self.cur.fetchall()
        if len(result)>0:
            for x in result:
                if x.text == data.text:
                    return make_response({"result":True})
            return make_response({"result":False})
        return make_response({"result":False},204)