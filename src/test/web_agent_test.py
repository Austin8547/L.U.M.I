
from src.agent.web_agent import web_agent


def main():
    response = web_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": (
                    "Find three recent papers about "
                    "Vision Transformers for medical imaging."
                ),
            }
        ]
    })

    print("\n===== WEB AGENT RESPONSE =====\n")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    main()
