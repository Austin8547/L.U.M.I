
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
)


# 2. Define the router instructions
router_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are the routing controller for Lumi.

        Select exactly ONE agent for the user's query.

        Available agents:

        - arxiv:
          Search academic papers, research topics,
          authors, abstracts, and arXiv links.

        - resources:
          Monitor CPU, RAM, GPU, battery, temperatures,
          and running system processes.

        - trip:
          Plan travel routes between locations and
          retrieve distances and directions.

        - websearch:
          Search the web for current information,
          news, websites, and general online queries.

        Rules:
        1. Understand the user's primary intent.
        2. Select the most appropriate agent.
        3. Return only the agent name.
        4. Do not answer the user's query.

        Valid responses:
        arxiv
        resources
        trip
        websearch
        """
    ),
    ("human", "{query}"),
])


# 3. Build the routing chain
router_chain = router_prompt | llm


# 4. Route the user's query
def route_query(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    response = router_chain.invoke({
        "query": query.strip()
    })

    agent_name = response.content.strip().lower().strip("`")

    print(f"[Lumi Router] Selected agent: {agent_name}")

    return agent_name
