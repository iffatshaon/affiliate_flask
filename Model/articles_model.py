from Utils.database import cursor, connection
from flask import make_response, Response
from sydney import SydneyClient
import os
from openai import OpenAI
from bs4 import BeautifulSoup
import requests
import urllib.parse
from datetime import datetime
import markdown
from googlesearch import search
from Utils.helpers import checkToken
from unidecode import unidecode
import re
from Utils.prompt import ArticleGenerator
import mysql.connector

word_count={
        "info article":1800, 
        "blog article":1800, 
        "manual subheading article":1800, 
        "product category":600, 
        "amazon review":1000,
        "human touch content":1000,
        "info article":1000,
        "content rewrite":1000,
        "generated conclusion":1000,
        "generated introduction":1000,
        "blog article outline":1000,
        "blog single paragraph":1000,
        "bulk article":1800
        }

def incLine(key,value):
    inc_line={
        "numFaq":f"Number of FAQs with answers - {value}.",
        "numImage":f"Add minimum {value} image placeholders with appropriate labels to the images where possible in markdown image format, label as the alt. All images should be different.",
        "label":f"There should be a label - {value}.",
        "numSubheading":f"Number of subheadings - {value}.",
        "c":f"The subheadings of the article are - {value}.",
        "title":f"The title of the article is {value}.",
        "websiteCategory":f"The category of the website is {value}.",
        "productCategory":f"The category of the product is {value}.",
        "numOfProductPerArticle":f"There must be a minium of {value} products in the article.",
        "minimumPrice":f"The minimum price is {value}.",
        "maximumPrice":f"The maximum price is {value}.",
        "fullContent":f"The full content: {value}",
        "tone":f"The tone of the article will be {value}",
        "shortDescription":f"Short description of the blog is: {value}"
        }
    if(key not in inc_line):
        return ""
    return inc_line[key]

def fetch_article(fileName):
    with open(fileName, 'r') as file:
        file_content = file.read()
        return file_content

class articles_model:
    def __init__(self):
        self.con = connection
        os.environ["BING_COOKIES"] = "ipv6=hit=1703688473310&t=6; MUID=3DEE40628BB36AB5078C51FD8AB26BCC; SRCHD=AF=ANAB01; SRCHUID=V=2&GUID=58CD49D7CA2F4E4CA2124C4F6EDB19EF&dmnchg=1; MUIDB=3DEE40628BB36AB5078C51FD8AB26BCC; EDGSRVCPERSIST=; USRLOC=HS=1&CLOC=LAT=28.609184542770894|LON=-81.204502638892|A=733.4464586120832|TS=231227134046|SRC=W; SRCHUSR=DOB=20220509&T=1703634516000; _RwBf=ilt=5&ihpd=0&ispd=1&rc=12&rb=0&gb=0&rg=200&pc=12&mtu=0&rbb=0&g=0&cid=&clo=0&v=1&l=2023-12-26T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2023-12-26T23:48:40.2280687+00:00&rwred=0&r=0&wls=&wlb=&lka=0&lkt=0&TH=&ard=0001-01-01T00:00:00.0000000&wle=&ccp=&aad=0; _EDGE_S=SID=2735D64A6DE7643D2269C5BE6CF065CF; _SS=SID=2735D64A6DE7643D2269C5BE6CF065CF; EDGSRVC=lightschemeovr=displaytheme=edgeservices&EN=language=edgeservices; EDGSRVCSCEN=shell=clientscopes=noheader-coauthor-chat-visibilitypm-udsedgeshop-udsdlpconsent-docvisibility-channelstable&chat=clientscopes=chat-noheader-udsedgeshop-channelstable-udsdlpconsent; SRCHHPGUSR=SRCHLANG=en&BRW=NOTP&BRH=S&CW=540&CH=654&SW=1366&SH=768&DPR=1&UTC=-300&DM=0&EXLTT=5&HV=1703684879&PV=10.0.0&PRVCW=1318&PRVCH=654&WTS=63839281665&IG=2CCFB3A1EAA8458AA8ACFDFDDCDCF64E&SCW=1164&SCH=3722&CIBV=1.1381.12; GC=0yd9NB_jysCRblaZlkZ97FczkFmXfZ-n1Cplxzk20IFJ-jRovNSzTEY8lB1rax8qY3tmq7PbOcNlwHt_B2a_Jw; EDGSRCHHPGUSR=CIBV=1.1381.12&CMUID=3DEE40628BB36AB5078C51FD8AB26BCC; BFBUSR=CMUID=3DEE40628BB36AB5078C51FD8AB26BCC"
        self.client = OpenAI(api_key=os.getenv("GPT_SECRET"))
        self.cur = cursor

    async def getAnswer(e) -> None:
        print(e)
        async with SydneyClient() as sydney:
            prompt = "Write an HTML code of an article using the keywords - money, seo, unknown. A blogger site, type - tech, label - tech. Number of subheadings - random. Number of FAQs - random. Place minimum 3 image placeholders in places where images can be inserted, also provide an appropriate image anchor in all the placeholders. Should be plagiarism free. Only keep the article in your answer. Dont write labels for heading or subheading. "

            print("Sydney: ", end="", flush=True)
            async for response in sydney.ask_stream(prompt):
                print(response, end="", flush=True)
            print("\n")

    def generate_cookie():
        return "cookie text"

    def markdown_to_html(self, markdown_text):
        # Convert Markdown text to HTML
        html_content = markdown.markdown(markdown_text)
        html_content = html_content.replace("Image Placeholder: ","")
        soup = BeautifulSoup(html_content, 'html.parser')
        headers = soup.find_all(re.compile('^h[1-6]$'))  # Find all header tags (h1, h2, ..., h6)
        
        if headers:
            first_header = headers[0]
            if first_header.name != 'h1':
                first_header.name = 'h1'
        
        return str(soup)

    def create_model(self,data,token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        article_gen = ArticleGenerator(data,word_count[data['type']],id)
        file_name=article_gen.get_file_name()
        del article_gen
        # except Exception as e:
        #     return make_response({"Error":str(e)},400)
        return make_response({"article":file_name}, 201)

    def free_model(self,data):
        article_gen = ArticleGenerator(data,word_count[data['type']])
        if(data['type']=="info article" or data['type']=="blog article" or data['type']=="human touch content"):
            title,reply = article_gen.generate_info_article()
        elif(data['type']=="manual sub-heading artilce"):
            title,reply = article_gen.generate_manual_subheading()
        elif(data['type']=="generated introduction"):
            title,reply = article_gen.generate_introduction()
        elif(data['type']=="generated conclusion"):
            title,reply = article_gen.generate_conclusion()
        elif(data['type']=="product category"):
            title,reply = article_gen.generate_product_content()
        elif(data['type']=="blog article outline"):
            title,reply = article_gen.generate_blog_outline()
        elif(data['type']=="blog single paragraph"):
            title,reply = article_gen.generate_blog_paragraph()
        elif(data['type']=="content rewrite"):
            title,reply = article_gen.generate_rewrite_content()
        del article_gen
        file_name = datetime.now().strftime("%y%m%d%H%M%S")
        file_path = 'articles/'+file_name+'.txt'
        soup = BeautifulSoup(reply, features="html.parser")
        img_tags = soup.find_all('img')
        for img in img_tags:
            alt_value = img.get('alt', '')
            try:
                resultImage = self.getImagePexels(alt_value) 
                img['src'] = resultImage
            except:
                try:
                    resultImage = self.getImagePixabay(alt_value)
                except:
                    print("Could not find image for:",alt_value)
        body_content=str(soup)+"""
        <style>
        h1{
        text-align:center;
        }
        img{
        width:100%;
        }
        </style>
        """
        body_content = unidecode(body_content)
        with open(file_path, 'w') as file:
            file.write(body_content)
        self.cur.execute("INSERT INTO article (id, user, title, link, token_count, prompt) VALUES (%s, %s, %s, %s, %s, %s)",(file_name, id, title, file_path, 0, str(data)))
        return make_response({"result":[title,body_content]}) #send_file("text_file_path",mimetype="txt")

    def edit_model(self, file_id, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute("SELECT * from article where id=%s and user=%s",[file_id,id])
        result = self.cur.fetchall()
        if(len(result)>0):
            fileName = 'articles/'+file_id+'.txt'
            file_content = fetch_article(fileName)
            return make_response({"content":file_content,"token_count":result[0]['token_count'],"title":result[0]['title']})
        else:
            return make_response({"Error":"File not found under this user"},400)

    def save_model(self, file_id, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        fileName = 'articles/'+file_id+'.txt'
        content = unidecode(data['content'])
        with open(fileName, 'w') as file:
            file.write(content)
            try:
                self.cur.execute("UPDATE article SET title=%s where id=%s",[data['title'],file_id])
                return make_response({"result":"Saved successfully"}, 201)
            except Exception as e:
                return make_response({"result":"Unable to update", "error":str(e)},400)
            
    def delete_model(self,id,token):
        self.con.reconnect()
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        query = f"DELETE FROM article WHERE id={id}"
        try:
            self.cur.execute(query)
            self.con.commit()
            return make_response({"result": "Success"}, 200)
        except mysql.connector.Error as err:
            return make_response({"result": "Unable to Add","Error":str(err)}, 400)

    def get_list_model(self,token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute("SELECT id,title,wordpress,token_count FROM article WHERE user=%s ORDER BY id DESC",[id])
        result = self.cur.fetchall()
        return make_response({"result":result})
    
    def suggestion_model(self,data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        suggestion_sites = []
        query = ' '.join(data['keywords']) + " suggestions"
        for url in search(query, num=5, stop=3, pause=2):
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                title = soup.title.string
                suggestion_sites.append((title, url))
            except Exception as e:
                print(f"Error fetching data from {url}: {e}")
        return make_response({"suggestions":suggestion_sites})
    
    def keyword_model(self, data):
        self.con.reconnect()
        message = f"This is about some topic - {data['topic']}. Write the keywords for SEO optimization. Give me only the keywords, no extra texts."
        messages = [ {"role": "system", "content":
              "You are a web developer"} ]
        messages.append(
            {"role": "user", "content": message},
        )
        chat = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = chat.choices[0].message.content
        return make_response({"result":reply})