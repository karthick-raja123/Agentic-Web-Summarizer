import requests
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import google.generativeai as genai
import os
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")
class AgentState(TypedDict):
    query: str
    urls: List[str]
    content: str
    summary: str
def search_node(state):
    api_key = "5bb84fd903aa487920271c447d4b2ef245e1fa60"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    data = {"q": state["query"]}
    response = requests.post("https://google.serper.dev/search", headers=headers, json=data)
    results = response.json()
    urls = [result["link"] for result in results.get("organic", [])][:3]
    print("\nFetched URLs:")
    for url in urls:
        print(url)
    state["urls"] = urls
    return state
def browse_node(state):
    combined_content = ""
    for url in state["urls"]:
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            combined_content += text[:1000]
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    state["content"] = combined_content
    return state
def summarize_node(state):
    prompt = f"Summarize this text in 5 bullet points:\n\n{state['content'][:8000]}"
    response = model.generate_content(prompt)
    summary = response.text
    print("\n----- SUMMARY -----\n")
    print(summary)
    print("\n-------------------")
    state["summary"] = summary
    return state
graph = StateGraph(AgentState)
graph.add_node("search", search_node)
graph.add_node("browse", browse_node)
graph.add_node("summarize", summarize_node)
graph.set_entry_point("search")
graph.add_edge("search", "browse")
graph.add_edge("browse", "summarize")
graph.add_edge("summarize", END)
app = graph.compile()
if __name__ == "__main__":
    user_query = input("Enter your topic to summarize: ")
    inputs = {"query": user_query}
    result = app.invoke(inputs)
    print("\nFinal Summary:\n", result["summary"])
