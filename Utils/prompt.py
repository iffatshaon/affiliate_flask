import os
from openai import OpenAI
import re
import markdown

client = OpenAI(api_key=os.getenv("GPT_SECRET"))

roles = {
    "article":"You are an article writer"
}

def getResponse(role,msg):
    messages = [ {"role": "system", "content":
              roles[role]} ]
    messages.append(
        {"role": "user", "content": msg},
    )
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    response = chat.choices[0].message.content
    return response

def getTitle(keywords):
    message = f"Give me a title of an article based on keywords-'{keywords}'. The title must contain the keyword. Give me only the answer."
    title = getResponse("article",message)
    if title.startswith(("'", '"')) and title.endswith(("'", '"')):
        title = title[1:-1]
    return title

def getHeadings(title,keywords):
    message = f"Give me more than 6 headings on writing an info article on keywords - '{keywords}' and of title '{title}'. One of the headings must use this direct keyword. Give me only the answer."
    headings = getResponse("article",message)
    pattern = re.compile(r'\d+\.\s*|\.$')
    result = [pattern.sub('', line) for line in headings.split('\n')]
    return result

def getContent(title, heading, word_count, image_count, imaged):
    message = f"Write an article content in more than {word_count} words of the heading: {heading}, don't include the heading in your answer. The title of the article is {title}, don't incluide the title in your answer."
    if imaged:
        message+=f"Add minimum {image_count} image placeholders with appropriate labels to the images where possible in markdown image format, label as the alt."
        if image_count>1:
            message+="All images should be different."
    content = getResponse("article",message)
    return content

def getConclusion(headings):
    message=f"Write a conclusion of an article in more than 300 words whose headings are these - {str(headings)}"
    conclusion = getResponse("article",message)
    return conclusion

def getFaq(title, faqCount):
    message=f"Write a minimum of {faqCount} FAQs of an article with answer whose title is {title}. The questions should be a heading and answer in normal text."
    faq = getResponse("article",message)
    return faq


def checkMissingHeadings(headings,title,faqcount):
    has_faq = False
    has_conclusion = False
    for heading in headings:
        if "FAQ" in heading or "Frequently Asked Question" in heading:
            has_faq = True
        elif "Conclusion" in heading:
            has_conclusion = True
    newContents=[]
    if not has_conclusion:
        headings.append("Conclusion")
        newContents.append(getConclusion(headings))
    if not has_faq:
        headings.append("FAQ")
        newContents.append(getFaq(title,faqcount))

    return headings,newContents

def markdown_to_html(markdown_text):
    html_content = markdown.markdown(markdown_text)
    html_content = html_content.replace("Image Placeholder: ","")
    return html_content

def create_html_document(headings, contents):
    html_content=""
    for heading, content in zip(headings, contents):
        html_content += f"<h2>{heading}</h2>\n<p>{markdown_to_html(content)}</p>\n"
    return html_content


def generateInfoArticle(data):
    title = getTitle(data['keywords'])
    if 'headings' not in data:
        headings = getHeadings(title,data['keywords'])
    else:
        headings = data['headings'].split(',')
    imageInSingleContent = int(data['imageCount'])/len(headings)
    wordInSingleContent = 1800/len(headings)
    contents = []
    for heading in headings:
        content = getContent(title,heading,wordInSingleContent,imageInSingleContent,True)
        contents.append(content)
    headings,newContents = checkMissingHeadings(headings,title,data['faq'])
    contents+=newContents
    html = create_html_document(headings,contents)
    return title,html

def generateManualSubheading(data):
    imageInSingleContent = int(data['imageCount'])/len(headings)
    wordInSingleContent = 1800/len(data['subheadings'])
    contents = []
    for heading in data['subheadings']:
        content = getContent(data['title'],heading,wordInSingleContent,imageInSingleContent,True)
        contents.append(content)
    headings,newContents = checkMissingHeadings(data['subheadings'],data['title'],data['faq'])
    contents+=newContents
    html = create_html_document(headings,contents)
    return data['title'],html
    