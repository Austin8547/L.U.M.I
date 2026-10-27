
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
)

VALID_ROUTES = {"chat", "arxiv", "resources", "trip", "websearch"}

router_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the intent router for Lumi, a personal AI assistant.

Choose exactly ONE route for the user's CURRENT request.

Available routes:

- chat: Greetings, casual conversation, explanations, programming
  questions, AI/ML concepts, general knowledge, and questions you
  can answer using the LLM's existing knowledge.
- arxiv: Finding academic papers, research papers, authors, abstracts,
  and arXiv links.
- resources: Checking CPU, RAM, GPU, battery, temperatures,
  and running processes.
- trip: Planning travel routes, distances, and directions.
- websearch: Requests to search the web, current information,
  latest news, websites, and information requiring online research.

Routing rules:
1. Prefer chat for ordinary questions and explanations.
2. Do NOT choose websearch just because a question asks for information.
3. Choose websearch when the user explicitly requests web searching,
   asks for current information, or needs online sources.
4. Choose arxiv for requests to find or investigate academic papers.
5. Use conversation history to understand follow-up questions.
6. Return only one route name, with no explanation.

Valid responses:
chat
arxiv
resources
trip
websearch

Recent conversation history:
{chat_history}
"""
    ),
    ("human", "{query}"),
])

router_chain = router_prompt | llm


# Prompt for answering ordinary questions directly.
chat_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are Lumi, a friendly and helpful personal AI assistant.

Answer the user's question directly using your existing knowledge.
Be conversational for greetings and casual conversation.
Explain technical topics clearly and give examples when helpful.
Do not claim to have searched the web or used tools unless you did.
Use the conversation history to maintain context.

Conversation history:
{chat_history}
"""
    ),
    ("human", "{query}"),
])

chat_chain = chat_prompt | llm


def _format_history(chat_history=None) -> str:
    """Convert stored conversation messages into readable history."""

    if not chat_history:
        return "No previous conversation."

    return "\n".join(
        f"{message.get('role', 'user')}: {message.get('content', '')}"
        for message in chat_history
    )


def route_query(query: str, chat_history=None) -> str:
    """Choose an agent or the direct LLM chat route."""

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    response = router_chain.invoke({
        "query": query.strip(),
        "chat_history": _format_history(chat_history),
    })

    # Accept only a clean route label.
    route = response.content.strip().lower().strip("`").strip()
    route = route.splitlines()[0].strip().strip(" .,:;")

    if route not in VALID_ROUTES:
        print(
            f"[Lumi Router] Unexpected output {route!r}; "
            "falling back to chat."
        )
        route = "chat"

    print(f"[Lumi Router] Selected route: {route}")
    return route


def chat_query(query: str, chat_history=None) -> str:
    """Answer directly with the LLM, without invoking a tool agent."""

    response = chat_chain.invoke({
        "query": query.strip(),
        "chat_history": _format_history(chat_history),
    })

    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = [
            item["text"]
            for item in content
            if isinstance(item, dict)
            and isinstance(item.get("text"), str)
        ]
        return " ".join(parts).strip()

    return str(content)
