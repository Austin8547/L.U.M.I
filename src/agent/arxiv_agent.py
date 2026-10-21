
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from src.tools.arxiv_tool import arxiv_paper_search
import os

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
)

tools = [
    arxiv_paper_search,
]

arxiv_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a research assistant. "
        "Use the arXiv search tool when users request "
        "research papers. Summarize the results accurately "
        "and include paper titles and source URLs. "
        "Do not invent papers or bibliographic details."
    ),
)
