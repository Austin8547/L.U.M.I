
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from src.tools.news_tool import fetch_news
from src.config import LLM_MODEL, LLM_TEMPERATURE


llm = ChatGroq(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)

tools = [
    fetch_news,
]

news_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are Lumi's news assistant. "
        "Use the news fetching tool whenever users request news "
        "about a topic, person, location, business, or category. "
        "Summarize the retrieved articles accurately. "
        "Include article titles, publication dates, and summaries "
        "when available. "
        "Do not invent headlines, dates, sources, or facts. "
        "If no articles are found, explain this clearly. "
        "Keep responses concise and easy to understand."
    ),
)
