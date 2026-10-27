from src.agent.arxiv_agent import arxiv_agent


response = arxiv_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Find 3 papers about vision transformers "
            ),
        }
    ]
})

print(response["messages"][-1].content)
