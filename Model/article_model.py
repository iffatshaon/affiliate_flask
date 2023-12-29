from Utils.database import cursor, connection
from flask import make_response, send_file
import asyncio
from sydney import SydneyClient
import os
from openai import OpenAI


class article_model:
    def __init__(self):
        self.con = connection
        os.environ["BING_COOKIES"] = "ipv6=hit=1703688473310&t=6; MUID=3DEE40628BB36AB5078C51FD8AB26BCC; SRCHD=AF=ANAB01; SRCHUID=V=2&GUID=58CD49D7CA2F4E4CA2124C4F6EDB19EF&dmnchg=1; MUIDB=3DEE40628BB36AB5078C51FD8AB26BCC; EDGSRVCPERSIST=; USRLOC=HS=1&CLOC=LAT=28.609184542770894|LON=-81.204502638892|A=733.4464586120832|TS=231227134046|SRC=W; SRCHUSR=DOB=20220509&T=1703634516000; _RwBf=ilt=5&ihpd=0&ispd=1&rc=12&rb=0&gb=0&rg=200&pc=12&mtu=0&rbb=0&g=0&cid=&clo=0&v=1&l=2023-12-26T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2023-12-26T23:48:40.2280687+00:00&rwred=0&r=0&wls=&wlb=&lka=0&lkt=0&TH=&ard=0001-01-01T00:00:00.0000000&wle=&ccp=&aad=0; _EDGE_S=SID=2735D64A6DE7643D2269C5BE6CF065CF; _SS=SID=2735D64A6DE7643D2269C5BE6CF065CF; EDGSRVC=lightschemeovr=displaytheme=edgeservices&EN=language=edgeservices; EDGSRVCSCEN=shell=clientscopes=noheader-coauthor-chat-visibilitypm-udsedgeshop-udsdlpconsent-docvisibility-channelstable&chat=clientscopes=chat-noheader-udsedgeshop-channelstable-udsdlpconsent; SRCHHPGUSR=SRCHLANG=en&BRW=NOTP&BRH=S&CW=540&CH=654&SW=1366&SH=768&DPR=1&UTC=-300&DM=0&EXLTT=5&HV=1703684879&PV=10.0.0&PRVCW=1318&PRVCH=654&WTS=63839281665&IG=2CCFB3A1EAA8458AA8ACFDFDDCDCF64E&SCW=1164&SCH=3722&CIBV=1.1381.12; GC=0yd9NB_jysCRblaZlkZ97FczkFmXfZ-n1Cplxzk20IFJ-jRovNSzTEY8lB1rax8qY3tmq7PbOcNlwHt_B2a_Jw; EDGSRCHHPGUSR=CIBV=1.1381.12&CMUID=3DEE40628BB36AB5078C51FD8AB26BCC; BFBUSR=CMUID=3DEE40628BB36AB5078C51FD8AB26BCC"
        self.client = OpenAI(api_key=os.getenv("GPT_SECRET"))
        self.cur = cursor
    
    async def getAnswer(e) -> None:
        print(e)
        async with SydneyClient() as sydney:
            prompt = "Write an article using the keywords - money, seo, unknown. A blogger site, type - tech, label - tech. Number of subheadings - random. Number of FAQs - random. Place minimum 3 image placeholders in places where images can be inserted, also provide an appropriate image anchor in all the placeholders. Should be plagiarism free. Only keep the article in your answer. Dont write labels for heading or subheading."

            print("Sydney: ", end="", flush=True)
            async for response in sydney.ask_stream(prompt):
                print(response, end="", flush=True)
            print("\n")

    def generate_cookie():
        return "cookie text"

    def create_model(self,data):
        message = f"Write an article using the keywords - {data['keywords']}. A {data['site']} site, type - {data['type']}, label - {data['label']}. Number of subheadings - {data['subheading']}. Number of FAQs - {data['faq']}. Place minimum {data['imageCount']} image placeholders in places where images can be inserted, also provide an appropriate image anchor in all the placeholders. Should be plagiarism free. Only keep the article in your answer. Dont write labels for heading or subheading."
        messages = [ {"role": "system", "content":
              "You are a content writer."} ]
        messages.append(
            {"role": "user", "content": message},
        ) 
        chat = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = chat.choices[0].message.content
        return make_response({"result":reply}) #send_file("text_file_path",mimetype="txt")
    
    def free_model(self,data):
        # self.con.reconnect()
        # print("Hello all")
        asyncio.run(self.getAnswer())
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def suggestion_model(self,data):
        self.con.reconnect()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")