import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import base64
import csv
import tempfile
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
)
def search_serper(query):
    api_key = "5bb84fd903aa487920271c447d4b2ef245e1fa60"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    data = {"q": query}
    response = requests.post("https://google.serper.dev/search", headers=headers, json=data)
    results = response.json()
    urls = [result["link"] for result in results.get("organic", [])][:3]
    return urls
def scrape_content(urls):
    combined_content = ""
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            combined_content += text[:1000]
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return combined_content
def summarize_with_gemini(content):
    prompt = f"Summarize this text clearly in 5 key bullet points:\n\n{content[:3000]}"
    summary = llm.invoke(prompt).content
    return summary
def generate_tts(summary_text):
    tts = gTTS(summary_text)
    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(fp.name)
    return fp.name
def create_csv(summary_text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline='', encoding="utf-8")
    writer = csv.writer(tmp)
    writer.writerow(["Summary"])
    for line in summary_text.split("\n"):
        writer.writerow([line])
    tmp.close()
    return tmp.name
st.title("QuickGlance: Agentic Browser Pipeline")
query = st.text_input("Enter your topic for summarization:")
if st.button("Search, Scrape, and Summarize"):
    if query.strip() == "":
        st.warning("⚠ Please enter a topic to proceed.")
    else:
        with st.spinner("🔍 Searching using Serper..."):
            urls = search_serper(query)
            st.write("Top URLs found:")
            for url in urls:
                st.write(url)

        with st.spinner("🪄 Scraping content..."):
            content = scrape_content(urls)

        with st.spinner("Summarizing using Gemini..."):
            summary = summarize_with_gemini(content)
            st.success("Summary Generated:")
            st.write(summary)
        csv_path = create_csv(summary)
        with open(csv_path, "rb") as f:
            st.download_button("⬇ Download Summary as CSV", f, file_name="summary.csv", mime="text/csv")
        audio_path = generate_tts(summary)
        audio_bytes = open(audio_path, "rb").read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)