from Utils.database import cursor,connection
from flask import make_response, send_file, Response
import mysql.connector
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import jwt
import os

class wordpress_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def checkToken(self,token):
        if not token:
            return make_response({"result": "Token not found"}, 401)
        try:
            decode = jwt.decode(token,str(os.getenv("SECRET_KEY")),"HS256")
            return decode['id']
        except:
            return make_response({"result": "Token expired"}, 401)
    
    def getall_model(self,token):
        self.con.reconnect()
        id = self.checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute(f"SELECT * FROM wordpress where id={id}")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def getuser_model(self,user):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM wordpress where id={user}")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def update_model(self, data, token):
        self.con.reconnect()
        id = self.checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            self.cur.execute("UPDATE wordpress SET site=%s, username=%s, password=%s WHERE id=%s AND user=%s",
                             (data['site'], data['username'], data['password'], data['id'], id))
            
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Update","error":err}, 500)
    
    def add_model(self,data, token):
        self.con.reconnect()
        id = self.checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            self.cur.execute("INSERT INTO wordpress (site, username, password, user) VALUES (%s, %s, %s, %s)",
                             (data['site'], data['username'], data['password'], str(id)))
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add","error":err}, 500)
    
    def delete_model(self, data, token):
        self.con.reconnect()
        id = self.checkToken(token)
        if isinstance(id, Response):
            return id
        query = f"DELETE FROM wordpress WHERE id={data['id']} AND user={id}"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add", "error":err}, 500)
    
    def publish_model(self,data, token):
        self.con.reconnect()
        id = self.checkToken(token)
        if isinstance(id, Response):
            return id
        wordpress_url = data['site']  # Replace with your WordPress site URL
        wordpress_username = data['username']  # Replace with your WordPress username
        wordpress_password = data['password']  # Replace with your WordPress application password
        # Create a WordPress client
        client = Client(wordpress_url, wordpress_username, wordpress_password)

        post = WordPressPost()
        post.title = data['title']
        post.content = data['content']
        
        try:
            post_id = client.call(NewPost(post))
            sql = f"UPDATE article SET wordpress=1 WHERE id={id}"
            self.cur.execute(sql)
            return make_response({"result": "Article posted successfully! Post ID: "+post_id}, 201)
        except Exception as err:
            return make_response({"result":"Unable to publish", "error":str(err)},500)