from langchain.agents import create_agent
from langchain_groq import ChatGroq

from src.tools.system_tools import (
    get_cpu_status,
    get_ram_status,
    get_battery_status,
    get_gpu_status,
    get_temperature_status,
)
from src.config import LLM_MODEL, LLM_TEMPERATURE

llm = ChatGroq(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)

system_tools = [
    get_temperature_status,
    get_gpu_status,
    get_ram_status,
    get_cpu_status,
    get_battery_status,
]

system_resource_agent = create_agent(
    model=llm,
    tools=system_tools,
    system_prompt="You are a helpful system resource monitoring assistant."
)

