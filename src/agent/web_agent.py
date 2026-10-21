
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from src.tools.web_tools import web_search

load_dotenv()

SYSTEM_PROMPT = """
You are Lumi's Web Research Agent.

Your responsibilities:
1. Understand the user's web research request.
2. Use the web_search tool when external information is required.
3. Summarize search results accurately.
4. Include relevant source URLs in your response.
5. Never invent search results, facts, or URLs.
6. State clearly when the available results are insufficient.
7. Distinguish information found in search results from your own reasoning.
"""

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
)

tools = [web_search]

web_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)
