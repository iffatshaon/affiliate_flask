from Utils.database import cursor, connection
from flask import make_response, Response
import asyncio
from sydney import SydneyClient
import os
from openai import OpenAI
from bs4 import BeautifulSoup
import requests
import urllib.parse
from datetime import datetime
import markdown
import jwt
from googlesearch import search
from Utils.helpers import checkToken
from unidecode import unidecode

word_count={
        "info article":2800, 
        "blog article":2800, 
        "manual subheading article":2800, 
        "product category":2000, 
        "amazon review":2000,
        "human touch content":2000,
        "info article":2000,
        "content rewrite":2000,
        "generated conclusion":2000,
        "generated introduction":2000,
        "blog article outline":2000,
        "blog single paragraph":2000
        }

def incLine(key,value):
    inc_line={
        "numFaq":f"Number of FAQs with answers - {value}.",
        "numImage":f"Add minimum {value} image placeholders with appropriate labels to the images where possible in markdown image format, label as the alt. All images should be different.",
        "label":f"There should be a label - {value}.",
        "numSubheading":f"Number of subheadings - {value}.",
        "subheadings":f"The subheadings of the article are - {value}.",
        "title":f"The title of the article is {value}.",
        "websiteCategory":f"The category of the website is {value}.",
        "productCategory":f"The category of the product is {value}.",
        "numOfProductPerArticle":f"There must be a minium of {value} products in the article.",
        "minimumPrice":f"The minimum price is {value}.",
        "maximumPrice":f"The maximum price is {value}.",
        "fullContent":f"The full content: {value}",
        "tone":f"The tone of the article will be {value}"
        }
    if(key not in inc_line):
        return ""
    return inc_line[key]

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

    def getImagePixabay(self,imageInfo):
        api_url = f"https://pixabay.com/api/?key={os.getenv('PIXABAY_KEY')}&q={urllib.parse.quote_plus(imageInfo)}&image_type=photo&safesearch=true&per_page=4"
        response = requests.get(api_url)
        # print(response.json()["hits"][0]["largeImageURL"])
        return response.json()["hits"][0]["largeImageURL"]

    def getImagePexels(self,imageInfo):
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": os.getenv('PEXELS_KEY')
        }
        params = {
            "query": imageInfo,
            "per_page": 4
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()["photos"][0]["src"]["original"]

    def markdown_to_html(self, markdown_text):
        # Convert Markdown text to HTML
        html_content = markdown.markdown(markdown_text)
        html_content = html_content.replace("Image Placeholder: ","")
        
        return html_content

    def create_model(self, data, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        if (data['type'] not in word_count) or ('keywords' not in data):
            return make_response({"result": "Category not found"}, 400)
        message = f"Write me a {data['type']} with more than {word_count[data['type']]} words using the keywords - {data['keywords']}. Use the keywords minimum 4 times in the texts and bold them. Headings must start from heading level 1 (Title must be Heading 1)."
        for x in data:
            message+=incLine(x,data[x])
        message+="Don't give me any examples. Better to keep a video or image after title. Should be plagiarism free, each time generating new. Every paragraph should have a minimum of 5 sentences. Don't use any special character or emoji."
        # print(message)
        
        messages = [ {"role": "system", "content":
              "You are a web developer"} ]
        messages.append(
            {"role": "user", "content": message},
        ) 
        chat = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply_md = chat.choices[0].message.content
        reply = self.markdown_to_html(reply_md)
        
        soup = BeautifulSoup(reply, features="html.parser")
        # print(soup)
        try:
            soup.body.append(soup.head.style)
        except:
            pass
        token_count = len(reply_md.split())
        ### Remove token counts from total tokens bought out here ###
        self.cur.execute("SELECT * from users where id=%s",[id])
        result = self.cur.fetchall()
        id_user = ""
        token_user = ""
        if(len(result)>0):
            id_user = result[0]["id"]
            token_user = result[0]["token"]
        self.cur.execute("UPDATE users SET token=%s WHERE id=%s",(int(token_user)-token_count,id_user))
        ### Remove token counts from total tokens bought out here ###
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
        title = str(soup.find("h1").text)
        file_name = datetime.now().strftime("%y%m%d%H%M%S")
        file_path = 'articles/'+file_name+'.txt'
        body_content=str(soup)+"""
        <style>
        h1, h2, h3{
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
        self.cur.execute("INSERT INTO article (id, user, title, link, token_count, prompt) VALUES (%s, %s, %s, %s, %s, %s)",(file_name, id, title, file_path, token_count, str(data)))
        return make_response({"article_id":file_name}, 201) #send_file("text_file_path",mimetype="txt")
    
    def free_model(self,data):
        # self.con.reconnect()
        # print("Hello all")
        asyncio.run(self.getAnswer())
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def edit_model(self, file_id, token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute("SELECT * from article where id=%s and user=%s",[file_id,id])
        result = self.cur.fetchall()
        if(len(result)>0):
            fileName = 'articles/'+file_id+'.txt'
            with open(fileName, 'r') as file:
                file_content = file.read()
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

    def get_list_model(self,token):
        self.con.reconnect()
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        self.cur.execute("SELECT * FROM article WHERE user=%s",[id])
        result = self.cur.fetchall()
        return make_response({"result":result})
    
    def suggestion_model(self,data):
        self.con.reconnect()
        suggestion_sites = []
        query = ' '.join(data['keywords']) + " suggestions"
        for url in search(query, num=5, stop=3, pause=2):  # Adjust num and stop as per your requirement
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                title = soup.title.string
                suggestion_sites.append((title, url))
            except Exception as e:
                print(f"Error fetching data from {url}: {e}")
        # url = "https://www.helpscout.com/blog/"
        # req = requests.get(url)
        # soup = BeautifulSoup(req.content, 'html.parser')
        # img_tags = soup.find_all('img')
        # print(len(img_tags))
        # print(soup.head.style)
        # soup.body.append(soup.head.style)
        # url = "https://api.pexels.com/v1/search"
        # headers = {
        #     "Authorization": "thcOL8fAtOCFvyXYov7V6m1QbJn3IulEw1AUnStTPNiYy5rdpzvaCPfF"
        # }
        # params = {
        #     "query": "nature in ice",
        #     "per_page": 1
        # }
        # response = requests.get(url, headers=headers, params=params)
        # print(response.json()["photos"][0]["src"]["original"])
        # api_url = f"https://pixabay.com/api/?key={os.getenv('PIXABAY_KEY')}&q=yellow+flowers&image_type=photo&safesearch=true&per_page=4"
        # response = requests.get(api_url)
        # print(response.json()["hits"])
        # self.getImagePixabay("Yellow flower")
        return make_response({"result":suggestion_sites}) #send_file("text_file_path",mimetype="txt")
    
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