from langchain.agents import create_agent
from langchain_groq import ChatGroq

from src.tools.trip_tool import shortest_path
from src.config import LLM_MODEL, LLM_TEMPERATURE

llm = ChatGroq(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)

system_tools = [
    shortest_path
]

trip_planner_agent = create_agent(
    model=llm,
    tools=system_tools,
    system_prompt=(
        "You are a trip-planning assistant. When the user asks for driving routes "
        "between two places, call the shortest_path tool exactly once with the "
        "start and end place names, then answer from its result. "
        "Never call it again for the same request, even if you want more detail. "
        "Reply concisely: one line per route with distance, duration and main roads, "
        "then a one-line recommendation. No emojis, no headers. "
        "If the tool returns an error, tell the user briefly and suggest trying again. "
        "Do not invent routes, roads or times that are not in the tool result."
    ),
)