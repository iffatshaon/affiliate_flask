from Utils.database import cursor,connection
from flask import make_response, Response
import mysql.connector
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.posts import GetPosts
from wordpress_xmlrpc.methods.posts import GetPostTypes
from wordpress_xmlrpc.methods.taxonomies import GetTerms,GetTerm
from Utils.helpers import checkToken
from Model.articles_model import fetch_article

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
        if site:
            query = f"SELECT * FROM sites where user={id} and type='{site}'"
        else:
            query = f"SELECT * FROM sites where user={id}"
        self.cur.execute(query)
        result = self.cur.fetchall()
        return make_response({"sites":result})

    def getuser_model(self,user):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM sites where user={user}")
        result = self.cur.fetchall()
        return make_response({"sites":result})

    def update_model(self, sid, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            self.cur.execute("UPDATE sites SET site=%s, username=%s WHERE id=%s AND user=%s",
                             (data['site'], data['username'], sid, id))
            
            return make_response(data, 200)
        except mysql.connector.Error as err:
            return make_response({"result": "Unable to Update","error":str(err)}, 400)
    
    def add_model(self,data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            self.cur.execute("INSERT INTO sites (site, username, type, user) VALUES (%s, %s, %s, %s)",
                             (data['site'], data['username'], data['type'], str(id)))
            return make_response(data, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add","error":err}, 400)
    
    def delete_model(self, sid, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        query = f"DELETE FROM sites WHERE id={sid} AND user={id}"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response(sid, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add", "error":err}, 400)
    
    def publish_model(self, site_id, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        
        query = f"SELECT * FROM sites where id={site_id}"
        self.cur.execute(query)
        result = self.cur.fetchall()
        
        wordpress_url = result[0]['site']
        if "xmlrpc.php" not in wordpress_url:
            if wordpress_url[-1] != "/":
                wordpress_url = wordpress_url+"/"
            wordpress_url += "xmlrpc.php"
        wordpress_username = result[0]['username']
        wordpress_password = data['password']

        client = Client(wordpress_url, wordpress_username, wordpress_password)

        
        query = f"SELECT * from article where id={data['article_id']}"
        self.cur.execute(query)
        result = self.cur.fetchall()

        post = WordPressPost()
        post.title = result[0]['title']
        post.content = fetch_article(result[0]['link'])
        if "category" in data:
            post.terms = []
            for cats in client.call(GetTerms('category')):
                if cats.id in data["category"]:
                    post.terms.append(cats)
            post.post_status = 'publish'
        try:
            post_id = client.call(NewPost(post))
            sql = f"UPDATE article SET wordpress=1 WHERE id={id}"
            self.cur.execute(sql)
            return make_response({"result": "Article posted successfully! Post ID: "+post_id}, 200)
        except Exception as err:
            return make_response({"result":"Unable to publish", "error":str(err)},400)
    
    def get_category(self, site_id, data, token):
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        
        query = f"SELECT * FROM sites where id={site_id}"
        self.cur.execute(query)
        result = self.cur.fetchall()
        
        wordpress_url = result[0]['site']
        if "xmlrpc.php" not in wordpress_url:
            if wordpress_url[-1] != "/":
                wordpress_url = wordpress_url+"/"
            wordpress_url += "xmlrpc.php"
        wordpress_username = result[0]['username']
        wordpress_password = data['password']

        client = Client(wordpress_url, wordpress_username, wordpress_password)
        categories = client.call(GetTerms('category'))
        category_names = [{"id":category.id,"name":category.name} for category in categories]

        return make_response({"categories":category_names},200)