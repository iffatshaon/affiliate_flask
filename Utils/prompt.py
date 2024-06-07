import os
from openai import OpenAI
import re
import markdown
import concurrent.futures
from bs4 import BeautifulSoup

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
    def __init__(self, data, totalWord):
        self.chat = OpenAIChat()
        self.data = data
        self.totalWord = totalWord
        self.image_in_single_content = 0
        self.word_in_single_content = 0
        self.images = ["Example"]

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
            message += f"Add minimum {self.image_in_single_content} figure captions in a markdown image format for image search. The captions must point to the specific image related to the content and should be kept as alt. The captions should not contain similar to the following: {','.join(self.images)}"
            if self.image_in_single_content > 1:
                message += "All images should be different."
        content = self.chat.get_response(self.data['type'], message)
        # print("Content: ",content)
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

    def get_faq(self):
        message = f"Write a minimum of {self.data['numFaq']} FAQs of an article with answer whose title is {self.data['title']}. The questions should be bold and answer in normal text in the next line. Don't include any heading (FAQ...) in your answer."
        faq = self.chat.get_response(self.data['type'], message)
        return faq
    
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
        return self.data['title'], html

    def generate_manual_subheading(self):
        self.image_in_single_content = int(self.data['numImage']) / len(self.data['subHeadings'])
        self.word_in_single_content = "more than "+str(self.totalWord / len(self.data['subHeadings']))
        self.data['contents'] = self.process_with_threads(True)    
        self.check_missing_headings()
        html = self.create_html_document()
        return self.data['title'], html

    def generate_introduction(self):
        content = self.get_intro()
        words = content.split()
        title = ' '.join(words[:6])
        return title,content

    def generate_conclusion(self):
        content = self.get_conclusion()
        words = content.split()
        title = ' '.join(words[:6])
        return title,content
    
    def generate_product_content(self):
        if not self.data["title"]:
            self.data['title'] = self.get_title()
        self.data['subHeadings'] = ["Product introduction","Product description","FAQ"]

        self.word_in_single_content = self.totalWord / len(self.data['subHeadings'])
        self.data['contents'] = self.process_with_threads(True)
        
        html = self.create_html_document()
        return self.data['title'], html
    
    def generate_rewrite_content(self):
        message = f"Rewrite this within {self.totalWord} to {int(self.totalWord)+200} words about this content: {self.data['fullContent']}. The content must contain {self.data['numImage']} image labels written in markdown image format inside of the content. SHould add {self.data['numFaq']} at the end. Give me only the answer."
        content = self.chat.get_response(self.data['type'], message)
        title="Rewrite content"
        return title,content
    
    def generate_blog_outline(self):
        message = f"Generate a blog outline from this short description: {self.data['shortDescription']} in {self.data['toine']}. The outline must contain these keywords atleast 3 times: {self.data['keywords']}. Give me only the answer."
        content = self.chat.get_response(self.data['type'], message)
        title="Blog outline"
        return title,content
    
    def generate_blog_paragraph(self):
        message = f"Generate a blog single paragraph from this short description: {self.data['shortDescription']} in {self.data['toine']}. The outline must contain these keywords atleast 3 times: {self.data['keywords']}. Give me only the answer."
        content = self.chat.get_response(self.data['type'], message)
        title="Blog single paragraph"
        return title,content

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
    "blog single paragraph":"You are a blog writer"

    }
