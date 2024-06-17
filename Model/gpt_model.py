from flask import make_response, Response
from Utils.helpers import checkToken
import os
from openai import OpenAI

class OpenAIChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("GPT_SECRET"))

    def get_response(self, model, msg):
        messages = [{"role": "system", "content": "You are a response generator"}]
        messages.append({"role": "user", "content": msg})
        chat = self.client.chat.completions.create(model=model, messages=messages)
        response = chat.choices[0].message.content
        return response

class gpt_model:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("GPT_SECRET"))
        self.chat = OpenAIChat()

    def query_model(self, data, token):
        id = checkToken(token)
        if isinstance(id, Response):
            return id
        try:
            response = self.chat.get_response(data['model'], data['query'])
            return make_response({"response":response})
        except Exception as e:
            return make_response({"error":str(e)},400)