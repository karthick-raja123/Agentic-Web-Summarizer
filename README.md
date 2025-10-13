# Visual-web-Agent
An AI-powered visual workflow system for automating web tasks using LangGraph and multi-agent coordination.
## overview
Visual Web Agent is an intelligent automation framework designed to interact with and control web environments visually. Built with LangGraph, this system enables the creation of AI-driven workflows that can browse, extract data, analyze content, and perform dynamic actions on web pages — all through agent-based collaboration.
## objective

-.The primary objective of this project is to develop an agentic  Pipeline with Gemini LLM that can automate the process of searching, scraping, and summarizing information from the web based on user queries. 
-.This system aims to reduce manual effort by retrieving the top relevant URLs, extracting meaningful content, and generating concise summaries in clear bullet points for easy understanding. Additionally, the   pipeline aims to provide multi-modal outputs such as downloadable CSV summaries for structured documentation and text-to-speech audio outputs to support auditory learners and revision on the go. 
By integrating Streamlit for an interactive UI, the project ensures ease of use for non-technical users. 
-.Overall, the goal is to enable efficient, accurate, and accessible knowledge extraction to support learners, researchers, and professionals in quickly grasping core insights from vast online resources without overwhelming them

## Tools:
#### Streamlit
- For building an interactive UI for input, displaying summaries, and downloading outputs.
#### gTTS (Google Text-to-Speech)
- Converts the text summary into audio for listening.
#### BeautifulSoup
- Parses and extracts clean text from fetched HTML content.
#### CSV module
- Saves summarized outputs in a CSV file for documentation and sharing.

## Technologies

#### LangChain + Gemini (Google GenAI)
- Used for advanced summarization from scraped content.

#### Serper.dev API
- Automates Google search and retrieves the top 3 relevant URLs based on the topic.

#### Requests
- Handles HTTP requests to fetch web pages and call APIs.

#### Base64 Encoding
- Embeds and plays back audio within the Streamlit web app.

#### Python Virtual Environment (venv)
- Ensures project isolation and organized dependency management.

## Implementation

Input: User gives topic in Streamlit UI.

Search: Uses Serper API to fetch top 3 relevant URLs.

Scrape: Uses requests + BeautifulSoup to extract clean text.

Summarize: Sends scraped text to Gemini API for 5-point summary.

Download & Audio: Generates CSV and audio for offline learning.

## Search & Scraping

-Search:

      Uses Serper API to perform Google-like search.
      Collects top 3 URLs for the entered topic.
      
-Scraping:
     Requests fetches the webpage.
     BeautifulSoup parses and extracts plain readable text from these URLs.
     Limits to first 1000 characters per site for relevance.

## Error Handling & Debugging

- Importance:

Ensures the pipeline does not crash during runtime.Makes the system robust and user-friendly.

- Methods Used:

Used try-except blocks in scraping to handle timeouts and broken links.

Validated user input to prevent blank queries.Displayed clear warning messages in Streamlit when no data found.

Limited text length to avoid API token overflow errors.

- Outcome:

Reduced run-time failures during multiple topic searches.Helped in maintaining smooth demo experience during presentations.


### Results and analysis

<img width="1882" height="788" alt="image" src="https://github.com/user-attachments/assets/cc4f8821-09df-492e-b1f8-2bcee44c02b7" />

- Outputs obtained:
- 
Top 3 relevant URLs fetched accurately for different topics.Clean, crisp 5-point summaries matching user queries.
Audio explanations played directly in UI.Summaries downloaded as CSV for records.Quick runtime 
Screenshots to include:
Streamlit UI with entered topic.Displayed URLs.Generated summary.Audio player in UI.


