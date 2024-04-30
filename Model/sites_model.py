from Utils.database import cursor,connection
from flask import make_response, Response
import mysql.connector
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.posts import GetPosts
from wordpress_xmlrpc.methods.posts import GetPostTypes
from wordpress_xmlrpc.methods.taxonomies import GetTerms
from Utils.helpers import checkToken

import collections
collections.Iterable = collections.abc.Iterable

class sites_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def getall_model(self,site,token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute(f"SELECT * FROM wordpress where user={id}")
        result = self.cur.fetchall()
        return make_response({"sites":result})

    def getuser_model(self,user):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM wordpress where user={user}")
        result = self.cur.fetchall()
        return make_response({"sites":result})

    def update_model(self, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            self.cur.execute("UPDATE wordpress SET site=%s, username=%s WHERE id=%s AND user=%s",
                             (data['site'], data['username'], data['id'], id))
            
            return make_response(data, 200)
        except mysql.connector.Error as err:
            return make_response({"result": "Unable to Update","error":str(err)}, 400)
    
    def add_model(self,data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            self.cur.execute("INSERT INTO wordpress (site, username, password, user) VALUES (%s, %s, %s, %s)",
                             (data['site'], data['username'], "", str(id)))
            return make_response(data, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add","error":err}, 400)
    
    def delete_model(self, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        query = f"DELETE FROM wordpress WHERE id={data['id']} AND user={id}"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response(data, 200)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add", "error":err}, 400)
    
    def publish_model(self, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        wordpress_url = data['site']
        wordpress_username = data['username']
        wordpress_password = data['password']

        client = Client(wordpress_url, wordpress_username, wordpress_password)

        post = WordPressPost()
        post.title = data['title']
        post.content = data['content']
        
        try:
            post_id = client.call(NewPost(post))
            sql = f"UPDATE article SET wordpress=1 WHERE id={id}"
            self.cur.execute(sql)
            return make_response({"result": "Article posted successfully! Post ID: "+post_id}, 200)
        except Exception as err:
            return make_response({"result":"Unable to publish", "error":str(err)},400)
    
    def get_category(self, data, token):
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        wordpress_url = data['site']
        wordpress_username = data['username']
        wordpress_password = data['password']

        client = Client(wordpress_url, wordpress_username, wordpress_password)
        categories = client.call(GetTerms('category'))
        category_names = [category.name for category in categories]

        return make_response({"categories":category_names},200)