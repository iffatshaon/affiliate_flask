from Utils.database import cursor,connection
from flask import make_response, Response
from Model.captcha_model import captcha_model
import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
from bs4 import BeautifulSoup
import os
import datetime
import jwt
from PIL import Image
from Utils.helpers import checkAdmin,checkToken, entries

captcha = captcha_model()

timeout=30

def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def send_email(receiver_email, subject, message):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_MAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'html'))

    s = smtplib.SMTP_SSL(smtp_server, port=smtp_port)
    s.login(smtp_username, smtp_password)
    s.sendmail(smtp_username, receiver_email, msg.as_string())
    s.quit()

def generate_token(username, id):
        payload = {
            'username': username,
            'id':id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)  # Token expiry time
        }
        token = jwt.encode(payload, str(os.getenv("SECRET_KEY")), algorithm='HS256')
        return token

class users_model():
    def __init__(self):
        self.con = connection
        self.cur = cursor
        
    def encrypt(self,password):
        password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(12))
        return str(hashed.decode('utf-8'))
        # return password

    def register_model(self,data):
        self.con.reconnect()
        getMatch = captcha.match_model({"hash":data['hash'],"text":data['text']})
        # getMatch = {'result':True}
        if getMatch['result']:
            password = self.encrypt(data['password'])
            self.cur.execute(f"SELECT * FROM users where email='{data['email']}' OR mobile='{data['mobile']}'")
            res = self.cur.fetchall()
            confirm_hash = generate_random_string()
            if(len(res)>0):
                return make_response({"result":"Email and/or Mobile number has already been used"},409)
            else:
                try:
                    if 'profile' not in data:
                        data['profile']='profiles/default.png'
                    self.cur.execute(f"INSERT INTO users(name,mobile,username,email,password,confirm,image) VALUES('{data['name']}','{data['mobile']}','{data['username']}','{data['email']}','{password}','{confirm_hash}','{data['profile']}')")
                    subject = "Welcome to Faisalitab AI"
                    with open("./Utils/activation.html", "r") as file:
                        message = file.read()
                    soup = BeautifulSoup(message,"html.parser")
                    a_tag = soup.find('a')
                    a_tag["href"]="https://faisaliteb.ai/confirm-mail/"+confirm_hash
                    send_email(data["email"], subject, str(soup))
                    return make_response({"result":"Verification link sent to mail"},201)
                except Exception as err:
                    return make_response({"result":"Unable to Register","error":str(err)},400)
        else:
            return make_response({"result":"Invalid captcha"},204)
    
    def confirmuser_model(self,data):
        self.con.reconnect()
        self.cur.execute(f"UPDATE users set confirm='1' where confirm='{data}'")
        return make_response({"result":"Registration successful"},200)

    def getusers_model(self):
        self.con.reconnect()
        self.cur.execute("SELECT id,name,mobile,username,email FROM users")
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response(result)
        else:
            return make_response({"result":"No data"},204)
        
    def get_personal_model(self,token):
        self.con.reconnect()
        id_check = checkToken(token)
        if isinstance(id_check, Response):
            return id_check
        self.cur.execute(f"SELECT id,name,mobile,username,email, token, image, package FROM users where id={id_check}")
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response(result[0])
        else:
            return make_response({"result":"No data"},204)

    def get_single_user_model(self,id_input,token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_input)==int(id) or checkAdmin(id)):
            return make_response({"result":"Unauthorized access"}, 401)
        self.cur.execute(f"SELECT id,name,mobile,username,email, token, image, package FROM users where id={id}")
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response({"result":result})
        else:
            return make_response({"result":"No data"},204)
    
    def remainingtoken_model(self,token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute("SELECT token FROM users where id=%s",[id])
        result = self.cur.fetchall()
        if len(result)>0:
            return make_response({"result":result})
        else:
            return make_response({"result":"No data"},204)
    
    def updateUser_model(self, data, id_d, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_d)==int(id) or checkAdmin(id)):
            return make_response({"result":"Unauthorized access"}, 401)
        sql = "UPDATE users SET"
        for x in data:
            if x != "id":
                sql+=f" {x}='{data[x]}',"
        sql = sql[:-1]
        sql += f" WHERE id={id_d}"
        self.cur.execute(sql)
        if self.cur.rowcount>0:
            return make_response({"result":data},201)
        else:
            return make_response({"result":"Nothing to update"},204)
        
    def changePassword_model(self,data, id_input, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_input)==int(id)):
            return make_response({"result":"Unauthorized access"}, 401)
        self.cur.execute(f"SELECT password FROM users WHERE id='{id}'")
        result = self.cur.fetchall()
        if(len(result)>0):
            if bcrypt.checkpw(data['password'].encode('utf-8'), result[0]["password"].encode('utf-8')):
                print("Hurra!! Password matched")
                if data['newPassword'] == data['confirmPassword']:
                    print("Hurra!! They are the same")
                    sql = f"UPDATE users SET password='{self.encrypt(data['newPassword'])}'"
                    self.cur.execute(sql)
                    return make_response({"result":"Passwords changed successfully"})
                else:
                    return make_response({"result":"Passwords didn't match"},201)
            else:
                return make_response({"result":"Invalid current password"},201)
        else:
            return make_response({"result":"User not found"},201)
        
    def forgotPassword_model(self, data, id_input, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_input)==int(id)):
            return make_response({"result":"Unauthorized access"}, 401)
        # confirm_hash = generate_random_string()
        # subject = "Welcome to Faisalitab AI"
        # with open("./Utils/activation.html", "r") as file:
        #     message = file.read()
        # soup = BeautifulSoup(message,"html.parser")
        # a_tag = soup.find('a')
        # a_tag["href"]="https://faisaliteb.ai/confirm-mail/"+confirm_hash
        # send_email(data["email"], subject, str(soup))
    
    def resetPassword_model(self, data, id_input, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_input)==int(id)):
            return make_response({"result":"Unauthorized access"}, 401)
    
    def get_image(self,path):
        with open(path, 'r') as file:
            file_content = file.read()
            return file_content

    def fetch_profile_pic(self, id_d, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_d)==int(id) or checkAdmin(id)):
            return make_response({"result":"Unauthorized access"}, 401)
        self.cur.execute("SELECT image from users where id=%s",[id])
        result = self.cur.fetchall()
        if(len(result)>0):
            image_path = result[0]['image']
            with open(image_path, 'rb') as file:
                image_content = file.read()
            headers = {"Content-disposition": "attachment; filename=profile.png"}
            mimetype = "image/png"
            return Response(image_content, mimetype=mimetype, headers=headers)
        else:
            return make_response({"Error":"File not found under this user"},400)

    def convert_to_png(self,path,image):
        temp_path = image.filename
        image.save(temp_path)
        img = Image.open(temp_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.save(path, format='PNG')
        os.remove(temp_path)

    def save_profile_pic(self, id_d, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if not (int(id_d) == int(id) or checkAdmin(id)):
            return make_response({"result": "Unauthorized access"}, 401)

        if 'profile' not in data:
            return make_response({"result": "No profile picture found in the request"}, 400)
        profile_image = data['profile']

        if profile_image.filename == '':
            return make_response({"result": "No selected file"}, 400)

        if profile_image:
            file_path = f"profiles/{id}.png"

            self.convert_to_png(file_path,profile_image)
            self.cur.execute(f"UPDATE users set image='{file_path}' where id='{id}'")

            return make_response({"result": "Profile picture saved successfully"}, 200)
        else:
            return make_response({"result": "No profile picture data found in the request"}, 400)

    
    def renew_token(self,id,data):
        try:
            decode = jwt.decode(data["token"],str(os.getenv("SECRET_KEY")),"HS256")
            token = generate_token(decode['username'],decode['id'])
            return make_response({"result":True, "token":token})
        except Exception as err:
            return make_response({"result":False, "error":str(err)}, 400)
    
    def login_model(self,data):
        self.con.reconnect()
        getMatch = captcha.match_model({"hash":data['hash'],"text":data['text']})
        if getMatch['result']:
            self.cur.execute(f"SELECT * FROM users WHERE username='{data['username']}'")
            result = self.cur.fetchall()
            if(len(result)>0):
                if bcrypt.checkpw(data['password'].encode('utf-8'), result[0]["password"].encode('utf-8')):
                    if result[0]['confirm']!="1":
                        return make_response({"result":False, "reason":"Verify user","email":result[0]["email"]})
                    token = generate_token(data['username'],result[0]['id'])
                    return make_response({"result":True, "token":token})
                else:
                    return make_response({"result":False,"reason":"Invalid username or password"})
            else:
                return make_response({"result":False,"reason":"User not found"})
        else:
            return make_response({"result":"Invalid captcha"})

        
    def delete_model(self, id, token):
        self.con.reconnect()
        id_d = checkToken(token)
        if isinstance(id_d, Response):
            return id_d
        if not (int(id_d)==int(id) or checkAdmin(id_d)):
            return make_response({"result":"Unauthorized access"}, 401)
        sql = f"DELETE FROM users WHERE id = {id}"
        self.cur.execute(sql)
        if self.cur.rowcount>0:
            return make_response({"result":f"User deleted by id:{id}"},201)
        else:
            return make_response({"result":f"User not found by id:{id}"},400)
    
    def logout_model(self,token):
        id_d = checkToken(token)
        if isinstance(id_d, Response):
            return id_d
        current_time = datetime.datetime.now()
        entry = (current_time, token)
        if id in entries:
            flag=True
            for existing_entry in entries[id]:
                if existing_entry[1] == token:
                    flag=False
            if flag:
                entries[id].append(entry)
        else:
            entries[id] = [entry]
        recent_time = current_time - datetime.timedelta(minutes=timeout)
        for token_id, entry_list in entries.items():
            entries[token_id] = [entry for entry in entry_list if entry[0] > recent_time]
            print(entries)
        return make_response({"result":"Logged out successfully"})
