from src.agent.utility_agent import system_resource_agent

response = system_resource_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is the CPU load and RAM status?"
        }
    ]
})

print(response["messages"][-1].content)