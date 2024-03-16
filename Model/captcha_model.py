from Utils.database import cursor, connection
from flask import make_response, send_file, Response
import string
from io import BytesIO,StringIO
from captcha.image import ImageCaptcha
import random
import uuid
from math import floor

class captcha_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def new_model(self):
        self.con.reconnect()
        captcha_length = 5
        captcha_characters = string.ascii_letters + string.digits
        # captcha_text = ''.join(random.choice(captcha_characters) for _ in range(captcha_length))
        fnumber = floor(random.random()*99)
        lnumber = floor(random.random()*99)
        captcha_text = str(fnumber)+"+"+str(lnumber)
        image = ImageCaptcha(width=250, height=90, fonts=['assets/fonts/roman.ttf'])
        captcha_image = image.generate(captcha_text)
        hash_value = uuid.uuid4().hex
        self.cur.execute(f"INSERT INTO captcha(hash,text) VALUES('{hash_value}','{str(fnumber+lnumber)}')")
        captcha_image = BytesIO(captcha_image.read())
        captcha_image.seek(0)
        headers = {"Content-disposition": "attachment; filename=captcha.png","hash":hash_value}
        mimetype = "image/png"
        return Response(captcha_image.read(), mimetype=mimetype, headers=headers)
    
    def match_model(self,data):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM captcha WHERE hash='{data['hash']}'")
        result = self.cur.fetchall()
        if len(result)>0:
            for x in result:
                if x["text"] == data["text"]:
                    return {"result":True}
            return {"result":False}
        return {"result":False}