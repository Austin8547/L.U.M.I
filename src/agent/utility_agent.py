import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from src.tools.system_tools import (
    get_cpu_status,
    get_ram_status,
    get_battery_status,
    get_gpu_status,
    get_temperature_status,
)

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b"
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

