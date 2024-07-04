import os
from openai import OpenAI
import re
import markdown
import concurrent.futures
from bs4 import BeautifulSoup
from unidecode import unidecode
from datetime import datetime
from Utils.database import cursor, connection
import requests
import urllib.parse

class OpenAIChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("GPT_SECRET"))

    def get_response(self, role, msg):
        messages = [{"role": "system", "content": roles[role]}]
        messages.append({"role": "user", "content": msg})
        chat = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        response = chat.choices[0].message.content
        return response

class ArticleGenerator:
    def __init__(self, data, totalWord, id):
        self.con = connection
        self.cur = cursor
        self.chat = OpenAIChat()
        self.data = data
        self.id=id
        self.totalWord = totalWord
        self.image_in_single_content = 0
        self.word_in_single_content = 0
        self.images = ["Example"]
        self.realData = data.copy()
        self.file_name = ""
        self.images_link = []
        if(data['type']=="info article" or data['type']=="blog article"):
            self.generate_info_article()
        elif(data['type']=="human touch content"):
            self.generate_human_touch()
        elif(data['type']=="manual sub-heading artilce"):
            self.generate_manual_subheading()
        elif(data['type']=="bulk article"):
            self.generate_bulk_article()
        elif(data['type']=="generated introduction"):
            self.generate_introduction()
        elif(data['type']=="generated conclusion"):
            self.generate_conclusion()
        elif(data['type']=="product category"):
            self.generate_product_content()
        elif(data['type']=="blog article outline"):
            self.generate_blog_outline()
        elif(data['type']=="blog single paragraph"):
            self.generate_blog_paragraph()
        elif(data['type']=="content rewrite"):
            self.generate_rewrite_content()
    
    def get_file_name(self):
        return self.file_name
    
    def suggestion(self):
        message = f"Give me 5 unique titles from these keywords: {self.data['keywords']}. Give me only the answer in numbered list. Example: [1] Title 1, [2] Title 2"
        titles = self.chat.get_response("info article", message)
        cleaned_list = []
        for item in titles.split('\n'):
            # print(item)
            cleaned_title = item.split('] ', 1)[-1].replace('"','').strip()
            cleaned_list.append(cleaned_title)
        return cleaned_list

    def get_title(self):
        message = f"Give me a title of an article based on keywords-'{self.data['keywords']}'. The title must contain the keyword. Give me only the answer."
        title = self.chat.get_response(self.data['type'], message)
        if title.startswith(("'", '"')) and title.endswith(("'", '"')):
            title = title[1:-1]
        return title

    def get_headings(self):
        if(self.data['numSubheading']=="random"):
            subhead_count = "more than 6"
        else:
            subhead_count = self.data['numSubheading']
        message = f"Give me {subhead_count} headings on writing an info article on keywords - '{self.data['keywords']}' and of title '{self.data['title']}'. One of the headings must use this direct keyword. Give me only the answer."
        headings = self.chat.get_response(self.data['type'], message)
        pattern = re.compile(r'\d+\.\s*|\.$')
        result = [pattern.sub('', line) for line in headings.split('\n')]
        return result

    def get_content(self, imaged):
        message = f"Write a part of a complete article in {self.word_in_single_content} words about {self.data['subHeadings']}, don't add any headings in your answer. Don't add any introduction or conclusion in this, only answer about the topic in two or three paragraphs only. For information the title of the article is {self.data['title']}, don't include the title in your answer. The content must have keywords- '{self.data['keywords']}' once."
        if imaged:
            # message += f"Add minimum {self.image_in_single_content} image labels in a markdown image format. In the markdown image the appropriate labels should be related to the contents. The labels must point to the specific image and should be kept as alt. The labels should not contain similar to the following: {','.join(self.images)}"
            message += f"Add minimum {self.image_in_single_content} figure captions in a markdown image format for image search. The captions must point to the specific image related to the content and should be kept as alt. For example, suppose there is a content on climate change, and the passage is on effect on climate change, so the image will generate '![Effects on climate change](#)'. The captions should not contain similar to the following: {','.join(self.images)}"
            if self.image_in_single_content > 1:
                message += "All images should be different."
        content = self.chat.get_response(self.data['type'], message)
        content_html = self.markdown_to_html(content)
        soup = BeautifulSoup(content_html, features="html.parser")
        img_tags = soup.find_all('img')
        for x in img_tags:
            self.images.append(x.get('alt', ''))
        return content

    def get_conclusion(self):
        message = f"Write a conclusion of an article in more than 300 words whose headings are these - {str(self.data['subHeadings'])} in only one paragraph. Don't include any heading (Conclusion) in your answer. Give me only the answer."
        conclusion = self.chat.get_response(self.data['type'], message)
        return conclusion

    def get_faq_answers(self,faq_question):
        content = ""
        for ques in faq_question:
            message = f"Write the answer to this faq question: '{ques}'. Write only the answer."
            answer = self.chat.get_response(self.data['type'], message)
            content += f"**{ques}**\n\n{answer}\n\n"
        return content

    def get_faq(self):
        message = f"Write a minimum of {self.data['numFaq']} FAQs of an article whose title is {self.data['title']}. The questions should be in ordered list. Answer only the ordered list."
        faq = self.chat.get_response(self.data['type'], message)
        questions = [line.split('. ', 1)[1] for line in faq.split('\n')]
        faq_content = self.get_faq_answers(questions)
        return faq_content
    
    def get_intro(self):
        message = f"Write only the introduction for this section within {self.totalWord} to {int(self.totalWord)+200} words about this content: {self.data['fullContent']}. Give me only the answer."
        intro = self.chat.get_response(self.data['type'], message)
        return intro

    def check_missing_headings(self):
        has_faq = False
        has_conclusion = False
        for heading in self.data['subHeadings']:
            if "FAQ" in heading or "Frequently Asked Question" in heading:
                has_faq = True
            elif "Conclusion" in heading:
                has_conclusion = True
        if not has_conclusion:
            self.data['subHeadings'].append("Conclusion")
            self.data['contents'].append(self.get_conclusion())
        if not has_faq:
            self.data['subHeadings'].append("FAQ")
            self.data['contents'].append(self.get_faq())

    def markdown_to_html(self, markdown_text):
        html_content = markdown.markdown(markdown_text)
        html_content = html_content.replace("Image Placeholder: ", "")
        return html_content

    def create_html_document(self):
        html_content = ""
        for heading, content in zip(self.data['subHeadings'], self.data['contents']):
            html_content += f"<h2>{heading}</h2>\n<p>{self.markdown_to_html(content)}</p>\n"
        return html_content

    def process_with_threads(self, imaged):
        contents = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_heading = {executor.submit(self.get_content, imaged): heading for heading in self.data['subHeadings']}
            for future in concurrent.futures.as_completed(future_to_heading):
                heading = future_to_heading[future]
                try:
                    content = future.result()
                    contents.append(content)
                except Exception as exc:
                    print(f'Heading {heading} generated an exception: {exc}')
        return contents

    def generate_info_article(self):
        if not self.data["title"]:
            self.data['title'] = self.get_title()
        self.data['subHeadings'] = self.get_headings()
        self.image_in_single_content = int(self.data['numImage']) / len(self.data['subHeadings'])
        self.word_in_single_content = "more than "+str(self.totalWord / len(self.data['subHeadings']))
        self.data['contents'] = self.process_with_threads(True)
        
        self.check_missing_headings()
        html = self.create_html_document()
        body_content = self.get_image(html)
        self.create_file(self.data['title'], body_content)

    def generate_manual_subheading(self):
        self.image_in_single_content = int(self.data['numImage']) / len(self.data['subHeadings'])
        self.word_in_single_content = "more than "+str(self.totalWord / len(self.data['subHeadings']))
        self.data['contents'] = self.process_with_threads(True)    
        self.check_missing_headings()
        html = self.create_html_document()
        body_content = self.get_image(html)
        self.create_file(self.data['title'], body_content) 

    def generate_introduction(self):
        content = self.get_intro()
        words = content.split()
        title = ' '.join(words[:6])
        body_content = self.get_image(content)
        self.create_file(title, body_content) 

    def generate_conclusion(self):
        content = self.get_conclusion()
        words = content.split()
        title = ' '.join(words[:6])
        body_content = self.get_image(content)
        self.create_file(title, body_content) 
    
    def generate_product_content(self):
        if not self.data["title"]:
            self.data['title'] = self.get_title()
        self.data['subHeadings'] = ["Product introduction","Product description","FAQ"]

        self.word_in_single_content = self.totalWord / len(self.data['subHeadings'])
        self.data['contents'] = self.process_with_threads(True)
        
        html = self.create_html_document()
        body_content = self.get_image(html)
        self.create_file(self.data['title'], body_content) 
    
    def generate_rewrite_content(self):
        message = f"Rewrite this within {self.totalWord} to {int(self.totalWord)+200} words about this content: {self.data['fullContent']}. The content must contain {self.data['numImage']} image labels written in markdown image format inside of the content. SHould add {self.data['numFaq']} at the end. Give me only the answer."
        content = self.chat.get_response(self.data['type'], message)
        title="Rewrite content"
        body_content = self.get_image(content)
        self.create_file(title, body_content) 
    
    def generate_blog_outline(self):
        message = f"Generate a blog outline from this short description: {self.data['shortDescription']} in {self.data['toine']}. The outline must contain these keywords atleast 3 times: {self.data['keywords']}. Give me only the answer."
        content = self.chat.get_response(self.data['type'], message)
        title="Blog outline"
        body_content = self.get_image(content)
        self.create_file(title, body_content) 
    
    def generate_blog_paragraph(self):
        message = f"Generate a blog single paragraph from this short description: {self.data['shortDescription']} in {self.data['toine']}. The outline must contain these keywords atleast 3 times: {self.data['keywords']}. Give me only the answer."
        content = self.chat.get_response(self.data['type'], message)
        title="Blog single paragraph"
        body_content = self.get_image(content)
        self.create_file(title, body_content) 
    
    def generate_bulk_article(self):
        allKeywords = self.data['keywords']
        output = []
        for keyword in allKeywords.split('\n'):
            self.data['keywords'] = keyword
            self.generate_info_article()
            singleResult={"title":self.data['title'],"article_id":self.file_name}
            self.data['title']=""
            output.append(singleResult)
        self.file_name = output

    def generate_human_touch(self):
        self.image_in_single_content = int(self.data['numImage']) / len(self.data['subHeadings'])
        self.word_in_single_content = "more than "+str(self.totalWord / len(self.data['subHeadings']))
        has_conclusion=False
        self.data['subHeadings'] = self.data['subHeadings'].split("\n")
        self.data['faqs'] = self.data['faqs'].split("\n")
        for heading in self.data['subHeadings']:
            if "FAQ" in heading or "Frequently Asked Question" in heading or "faq" in heading:
                del self.data['subHeadings']['FAQ']
                del self.data['subHeadings']['faq']
                del self.data['subHeadings']['Frequently Asked Question']
            elif "Conclusion" in heading or "conclusion" in heading:
                has_conclusion = True
        self.data['contents'] = self.process_with_threads(True)
        
        if not has_conclusion:
            self.data['subHeadings'].append("Conclusion")
            self.data['contents'].append(self.get_conclusion())
        self.data['subHeadings'].append("FAQ")
        self.data['contents'].append(self.get_faq_answers(self.data['faqs']))

        html = self.create_html_document()
        body_content = self.get_image(html)
        self.create_file(self.data['title'], body_content)
    
    def getImagePixabay(self,imageInfo):
        api_url = f"https://pixabay.com/api/?key={os.getenv('PIXABAY_KEY')}&q={urllib.parse.quote_plus(imageInfo)}&image_type=photo&safesearch=true&per_page=10"
        response = requests.get(api_url)
        hits = response.json().get("hits", [])
        # print(response.json()["hits"][0]["largeImageURL"])
        for hit in hits:
            image_url = hit["largeImageURL"]
            image_title = hit.get("tags", "No title")

            if image_url not in self.images_link:
                self.images_link.append(image_url)
                return image_url, image_title

    def getImagePexels(self,imageInfo):
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": os.getenv('PEXELS_KEY')
        }
        params = {
            "query": imageInfo,
            "per_page": 10
        }
        response = requests.get(url, headers=headers, params=params)
        photos = response.json().get("photos", [])

        for photo in photos:
            image_url = photo["src"]["original"]
            image_title = photo.get("alt", "No title")  # Get the alt text as the title

            if image_url not in self.images_link:
                self.images_link.append(image_url)
                return image_url, image_title
    
    def getImageGoogle(self, search_term, num=10):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": search_term,
            "cx": '124161338f8724c47',#os.getenv('GOOGLE_CSE_ID'),
            "key": 'AIzaSyCPHUGkoMq-Z7qO3nUDTDBrz1erVmSPm3M',#os.getenv('GOOGLE_API_KEY'),
            "searchType": "image",
            "num": num,
            "fileType": "jpg|png",
            "rights": "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"
        }
        response = requests.get(url, params=params)
        print(params, response)
        result = response.json()
        # images = [item['link'] for item in result.get('items', [])]
        for x in result.get('items', []):
            if x['link'] not in self.images_link:
                self.images_link.append(x['link'])
                return x['link'], x.get('title', 'No title')

    def get_image(self,reply):
        soup = BeautifulSoup(reply, features="html.parser")
        img_tags = soup.find_all('img')
        for img in img_tags:
            alt_value = img.get('alt', '').split(':')[-1]
            try:
                resultImage, title = self.getImageGoogle(str(alt_value))
                img['src'] = resultImage
                figure = soup.new_tag("figure")
                figcaption = soup.new_tag("figcaption")
                figcaption.string = title if title else "Image"

                # Insert image into figure and add figcaption
                img.wrap(figure)
                figure.append(figcaption)
            except Exception as e:
                try:
                    print("Couldnt find image in google: ",alt_value)
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
        body_content = body_content.replace("\n", "")
        return body_content
    
    def create_file(self, title, content):
        self.file_name = datetime.now().strftime("%y%m%d%H%M%S")
        file_path = 'articles/'+self.file_name+'.txt'
        with open(file_path, 'w') as file:
            file.write(content)
        self.cur.execute("INSERT INTO article (id, user, title, link, token_count, prompt) VALUES (%s, %s, %s, %s, %s, %s)",(self.file_name, self.id, title, file_path, 0, str(self.realData)))
        

# Sample usage:
roles = {
    "info article": "You are a article writer",
    "manual subheading article":"You are a article content writer",
    "blog article":"You are a blog writer", 
    "product category":"You are a product description writer",
    "amazon review":"You are a amazon product reviewer",
    "human touch content":"You are a article writer",
    "content rewrite":"You are a article writer",
    "generated conclusion":"You are a article writer",
    "generated introduction":"You are a article writer",
    "blog article outline":"You are a blog writer",
    "blog single paragraph":"You are a blog writer",
    "bulk article":"You are a article writer"
    }
