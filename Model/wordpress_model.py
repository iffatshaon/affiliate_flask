from Utils.database import cursor,connection
from flask import make_response, send_file
import mysql.connector
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

class wordpress_model:
    def __init__(self):
        self.con = connection
        self.cur = cursor
    
    def getall_model(self):
        self.con.reconnect()
        self.cur.execute(f"SELECT * FROM wordpress")
        result = self.cur.fetchall()
        return make_response({"result":result})

    def update_model(self,data):
        self.con.reconnect()
        if 'id' not in data:
            return make_response({"result": "Missing 'id'"}, 400)
        
        try:
            self.cur.execute("UPDATE wordpress SET site=%s, username=%s, password=%s WHERE id=%s",
                             (data['site'], data['username'], data['password'], data['id']))
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Update"}, 204)
    
    def add_model(self,data):
        self.con.reconnect()
        try:
            self.cur.execute("INSERT INTO faq (site, username, password) VALUES (%s, %s, %s)",
                             (data['site'], data['username'], data['password']))
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add"}, 204)
    
    def delete_model(self,data):
        self.con.reconnect()
        query = f"DELETE FROM wordpress WHERE id={data['id']}"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response({"result": data}, 201)
        except mysql.connector.Error as err:
            print("Error:", err)
            return make_response({"result": "Unable to Add"}, 204)
    
    def publish_model(self,data):
        self.con.reconnect()
        wordpress_url = 'https://example.com/xmlrpc.php'  # Replace with your WordPress site URL
        wordpress_username = 'your_username'  # Replace with your WordPress username
        wordpress_password = 'your_application_password'  # Replace with your WordPress application password
        # Create a WordPress client
        client = Client(wordpress_url, wordpress_username, wordpress_password)

        post = WordPressPost()
        post.title = data['title']
        post.content = data['content']

        # Assign categories and tags if provided
        if data['categories']:
            post.terms_names = {'category': data['categories']}
        if data['tags']:
            post.terms_names['post_tag'] = data['tags']

        # Publish the post
        post_id = client.call(NewPost(post))
        print("Article posted successfully! Post ID:", post_id)