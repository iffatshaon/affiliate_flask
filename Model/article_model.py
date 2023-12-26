from Utils.database import cursor, connection
from flask import make_response, send_file
import asyncio
from sydney import SydneyClient
import os

class article_model:
    def __init__(self):
        self.con = connection
        os.environ["BING_COOKIES"] = "nAJilHEhUGcuWwH6MuDQDa2OSNq9cpDqasRNOdiyeHlllxIG8zxwHAGnBJPqSmzJDUTlauhxBTmnL2eNeE5wX0%2FBMSlJBkXWQ%2BX6P1jpoC4F0oDrtDipFMf8XWyMgSLFkXSrehPWQPhmGXviVeLV34PwxTaoVbA27pQ4xfmE1Z384OT%2BkNkzq8qb9LWvW1oYMcZ%2FH3NVsHOZf4M5jkwz1y%2FQk6UVeUL2yq6cZPQkrLyALFMbUokDcowF85WSONx0MgTdFlZ6i9m1YE4VZMV6rY47QJhTZqIc3hqv0VoLDWCJcCuuvbdk5rsu3DTzSJOqTOlMlLsRPRC6tKZdFnLKTNFXJo0qQhljWP3LSP7ubCRrEEV8HAhL4mlS%2B6obvFLTA1VOiuWctVPM7vlyL6OQUy61uyEGlJM8xwrgYURktc0%2F%2FVFD8bN%2Bkc9oQGS%2FybYGJ9ZE%2FF38zy0q9paWXXyo2WqcgrGWIi9YMm8w32BPpSwOb5xsqcQ6MvwnmxXPzgiPbDOu6%2BdKT5FVAgPneGgKg7KB9RlzsuFg98NIg6%2FgYnQqGdxva50Q3JyrJ8w7GrpxFeL6zJ3bTb%2FpaBAc9BZ2eQnujEJOyT35oE7bjJcBg%2Bpe5HR6JTJWWy8ZkhIzezn%2F0KVgNVp3m7jawMyrx3Kn6awZH6KyN2hOGdo8CdF7Cnn4jr6HeeMXu3kz9Q1C3yvHYht%2FptfVLvK9o5Vg3J91P8vOwc%2FFtJ0XGniZ504HZvnBtFIMj%2BS6%2B57y0U18RxC0%2Fx2zirf1AuzUa%2B%2FwcBPPax9%2BWAJuj1q03nNE%2BBdHMnEndbdZYaxX%2FZFvPUgUyiT5uOqx0NDTlL1nXsfco0eHLlpZfLOvMgg9%2Bhf0%2Fjo8c63Ev7taPHa4mlvI19enm2xqgPd80%2FWC77VGPHDZUf8o%2F4fPtgkl%2BRiVRaKfPPBDz5nmdQciYKRa%2BneayhyeNQLwGwg3bSrkdCKAktSCkH39MyzH1XaewbweIvJOywkG8NuSyjLQ16IWP41Xxy3etJ%2F%2FiigaKppNYcnTPMDsfWWrV0BhFGU1Duw4CVB3Hg%2B2Ajwb05Ejyd6V7tCh2%2FWLl%2B7fgByveVFlGOqaM9BeGfWBowr7zZ2BAdo5ADTbNgxIRMJs83KuozEomw8Zuomjyo3XebKwdESjwXULGqDwTdmf%2BQ%3D%3D"
        self.cur = cursor
    
    async def getAnswer(e) -> None:
        print(e)
        async with SydneyClient() as sydney:
            prompt = "Write an article using the keywords - money, seo, unknown. "

            print("Sydney: ", end="", flush=True)
            async for response in sydney.ask_stream(prompt):
                print(response, end="", flush=True)
            print("\n")

    def generate_cookie():
        return "cookie text"

    def create_model(self):
        self.con.reconnect()
        cookie = self.generate_cookie()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def free_model(self,data):
        # self.con.reconnect()
        # print("Hello all")
        asyncio.run(self.getAnswer())
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")
    
    def suggestion_model(self,data):
        self.con.reconnect()
        return make_response({"result":"Incomplete API"}) #send_file("text_file_path",mimetype="txt")