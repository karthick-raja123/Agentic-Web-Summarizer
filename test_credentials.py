import gradio as gr
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# Function to fetch OpenGraph image
def fetch_og_image(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image['content']:
            return og_image['content']
    except:
        return None

# Function to generate hashtags
def generate_hashtags(summary):
    words = summary.split()
    keywords = list(set([word.strip('.,') for word in words if len(word) > 5]))[:5]
    hashtags = ["#" + word.capitalize() for word in keywords]
    return ' '.join(hashtags)

# Function to save summary as image
def save_summary_image(summary):
    img = Image.new('RGB', (600, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((20, 20), summary, fill=(0, 0, 0), font=font)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# Main pipeline function
def insight_harvester_pipeline(url, user_query):
    og_image_url = fetch_og_image(url)
    content = f"Summarize the following page focusing on {user_query} in 5 bullet points." + url
    response = llm.invoke(content)
    summary = response.content
    hashtags = generate_hashtags(summary)
    img = save_summary_image(summary)
    return summary, hashtags, img, og_image_url

# Gradio UI
title = "🚀 InsightHarvester: Smart Web Summarizer"
desc = "Enter your query and URL to get 5 bullet point summaries, hashtags, and an instant shareable image for LinkedIn."

demo = gr.Interface(
    fn=insight_harvester_pipeline,
    inputs=[
        gr.Textbox(label="Enter URL"),
        gr.Textbox(label="Enter your query (e.g., Key Points, Advantages, etc.)")
    ],
    outputs=[
        gr.Textbox(label="Summary"),
        gr.Textbox(label="Hashtags for Sharing"),
        gr.Image(label="Shareable Summary Image"),
        gr.Image(label="Page Thumbnail Preview", elem_id="og_image_preview")
    ],
    title=title,
    description=desc,
    theme="default",
    allow_flagging="never"
)

demo.launch()
