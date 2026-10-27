
# Lumi

Lumi is a terminal-based personal AI assistant built with Python, LangChain, and LangGraph. It combines AI agents, offline voice processing, and persistent memory for text and voice interactions.

## Features

- **Text & Voice Chat** — interact through the terminal.
- **Offline STT** — speech recognition using Faster-Whisper.
- **Offline TTS** — speech synthesis using Piper.
- **AI Agents** — web search, arXiv research, system utilities, and route planning.
- **Conversation Memory** — persistent memory using SQLite.
- **Agent Workflows** — modular routing and orchestration with LangGraph.
- **LLM Integration** — supports LLM-powered conversations and agents.

## Tech Stack

- Python
- LangChain & LangGraph
- SQLite
- Faster-Whisper (Offline STT)
- Piper TTS (Offline TTS)
- Groq API
- Tavily Search API
- arXiv API
- OpenStreetMap / OpenRouteService

## Setup

### 1. Clone the Repository

```bash
git clone <https://github.com/Austin8547/L.U.M.I>
cd lumi
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

install required dependencies inside the venv just created

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add the API keys required by your agents.

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
ORS_API_KEY=your_openrouteservice_api_key
```

Keep your `.env` file private and never commit API keys to Git.

## Run Lumi

With the virtual environment activated, run:

```bash
python -m src.main
```

Choose an operating mode:

- `T` — Text Mode
- `V` — Voice Mode
- `Q` — Quit

## Launch Lumi from Anywhere in the linux Terminal

If you use a dedicated virtual environment at `/home/austin/agentic/gen_ai`, add this function to your `~/.bashrc`:

```bash
lumi() {
    cd /home/austin/agentic/lumi || return
    source /home/austin/agentic/gen_ai/bin/activate
    python -m src.main
}
```

Reload your shell configuration:

```bash
source ~/.bashrc
```

Now launch Lumi from the linux terminal by just typing:

```bash
lumi
```

**Note:** The `lumi` function uses your existing `gen_ai` virtual environment. If you use the `.venv` created in Step 2 instead, change the activation line to:

```bash
source /home/austin/agentic/lumi/.venv/bin/activate
```

## Development Goals

Lumi is evolving toward a private, locally powered personal AI assistant with improved memory, local LLM integration, and modular AI agents.

