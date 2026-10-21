
from src.router.llm_router import route_query
from src.agent.arxiv_agent import arxiv_agent
from src.agent.utility_agent import system_resource_agent
from src.agent.route_planner_agent import trip_planner_agent
from src.agent.web_agent import web_agent


# Map agent names to existing agent objects.
AGENTS = {
    "arxiv": arxiv_agent,
    "resources": system_resource_agent,
    "trip": trip_planner_agent,
    "websearch": web_agent,
}


def dispatch_query(query: str):
    # Step 1: Ask the router to select an agent.
    agent_name = route_query(query)

    # Step 2: Find the selected agent.
    agent = AGENTS.get(agent_name)

    if agent is None:
        return f"Unknown agent selected: {agent_name}"

    # Step 3: Execute the selected agent.
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": query}
        ]
    })

    return result
