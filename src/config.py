"""

Modules that consume these settings:
  src/router/llm_router.py     - LLM model, router & chat prompts
  src/agent/*.py               - Per-agent LLM settings
  src/voice/tts_piper.py       - Piper TTS model path
  src/voice/sst_whisper.py     - Faster-Whisper STT settings
  src/memory/memory.py         - SQLite DB path & query limits
  src/memory/mem_middleware.py - Context window trimming
  src/router/dispatcher.py     - History limits passed to middleware
  src/web/web_search.py        - Tavily search settings
  src/arxiv/arxiv_search.py    - arXiv API settings
  src/news/news_fetch.py       - RSS feed URLs & article limits
  src/osm/route_find.py        - ORS/Nominatim settings & route variants
  src/tools/news_tool.py       - News tool article-count validation
  src/tools/arxiv_tool.py      - Default max_results for arXiv tool
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load .env from the project root (lumi/).
load_dotenv()


# Project paths


# Absolute path to the project root (lumi/).
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
# Absolute path to the src package.
SRC_ROOT: Path = Path(__file__).resolve().parent


# API Keys ( / .env)

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
ORS_API_KEY: str = os.getenv("ORS_API_KEY", "")


# LLM

LLM_MODEL: str = "qwen/qwen3.8-27b"
LLM_TEMPERATURE: float = 0.0


# Router - Valid routes dispatched by llm_router.py / dispatcher.py
# Exact set accepted by route_query(); must match AGENTS keys in dispatcher.
VALID_ROUTES: set = {
    "chat",
    "arxiv",
    "resources",
    "trip",
    "websearch",
    "news",
}

# Fallback route when the LLM returns an unexpected label.
DEFAULT_ROUTE: str = "chat"



# Conversation Memory - src/memory/memory.py

#memory database path

MEMORY_DB_PATH: Path = SRC_ROOT / "memory" / "lumi_memory.db"
# Maximum messages returned by ConversationMemory.get_history().
MEMORY_HISTORY_LIMIT: int = 20



# Memory Middleware - src/memory/mem_middleware.py / dispatcher.py


# Maximum number of messages forwarded to the LLM after trimming.
CONTEXT_MAX_MESSAGES: int = 6
# Maximum total characters of conversation context forwarded to the LLM.
CONTEXT_MAX_CHARS: int = 3000
# Minimum character headroom required before a message is truncated
CONTEXT_MIN_REMAINING_CHARS: int = 200


# Voice - STT: Faster-Whisper (src/voice/sst_whisper.py)


# Whisper model size. Options: tiny, base, small, medium, large-v2, large-v3
WHISPER_MODEL_SIZE: str = "base"
# Compute device. Use "cuda" for GPU, "cpu" for CPU-only.
WHISPER_DEVICE: str = "cuda"
# Quantisation precision. "float16" for GPU; "int8" for CPU-only mode.
WHISPER_COMPUTE_TYPE: str = "float16"
# Audio sample rate (Hz) used during recording.
WHISPER_SAMPLE_RATE: int = 16_000
# Default recording duration (seconds) when voice mode is active.
WHISPER_RECORD_DURATION: int = 5
# Beam size for Whisper decoding (1 = greedy / fastest).
WHISPER_BEAM_SIZE: int = 1
# Voice Activity Detection filter - skips silent audio segments.
WHISPER_VAD_FILTER: bool = True
# Language hint passed to Whisper transcription.
WHISPER_LANGUAGE: str = "en"




# Voice - TTS: Piper (src/voice/tts_piper.py)


# Absolute path to the Piper ONNX voice model file.
PIPER_MODEL_PATH: Path = (
    SRC_ROOT / "voice" / "files" / "en_US-lessac-medium.onnx"
)
# Audio streaming chunk size (samples) for sounddevice OutputStream.
PIPER_CHUNK_SIZE: int = 1_024
# Polling interval (ms) in the keyboard-listener loop during TTS playback.
PIPER_KEY_POLL_MS: int = 10
# Pause-check interval (ms) when TTS is paused before resuming.
PIPER_PAUSE_POLL_MS: int = 50




# Web Search - Tavily (src/web/web_search.py)


# Maximum number of web results returned per query.
TAVILY_MAX_RESULTS: int = 3
# Search topic passed to TavilySearch.
TAVILY_TOPIC: str = "general"
# Search depth. Options: "basic" | "advanced"
TAVILY_SEARCH_DEPTH: str = "basic"
# Whether to include a synthesised answer in Tavily results.
TAVILY_INCLUDE_ANSWER: bool = False
# Whether to include raw page content in Tavily results.
TAVILY_INCLUDE_RAW_CONTENT: bool = False




# arXiv Research (src/arxiv/arxiv_search.py)


# arXiv Atom API base URL.
ARXIV_API_URL: str = "https://export.arxiv.org/api/query"
# HTTP User-Agent header sent with every arXiv request.
ARXIV_USER_AGENT: str = "LumiResearchAgent/1.0 (arXiv paper search)"
# HTTP request timeout (seconds) for arXiv API calls.
ARXIV_TIMEOUT: int = 30
# Default sort field passed to the arXiv API.
ARXIV_SORT_BY: str = "relevance"
# Default sort order passed to the arXiv API.
ARXIV_SORT_ORDER: str = "descending"
# Multiplier applied to max_results when fetching candidate papers for
# re-ranking by title similarity. Fetches max(max_results * 5, 25) entries.
ARXIV_FETCH_MULTIPLIER: int = 5
ARXIV_FETCH_MIN: int = 25
# Default number of results returned by the arxiv_paper_search tool.
ARXIV_TOOL_DEFAULT_MAX_RESULTS: int = 3
# Hard upper limit on results accepted by the arxiv_paper_search tool.
ARXIV_TOOL_MAX_RESULTS_LIMIT: int = 10


# News - RSS Feeds (src/news/news_fetch.py)


# The Hindu section RSS feeds, keyed by lowercase category name.
HINDU_FEEDS: dict = {
    "home":          "https://www.thehindu.com/feeder/default.rss",
    "national":      "https://www.thehindu.com/news/national/feeder/default.rss",
    "international": "https://www.thehindu.com/news/international/feeder/default.rss",
    "editorial":     "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
    "opinion":       "https://www.thehindu.com/opinion/feeder/default.rss",
    "business":      "https://www.thehindu.com/business/feeder/default.rss",
    "economy":       "https://www.thehindu.com/business/Economy/feeder/default.rss",
    "technology":    "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
    "science":       "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
    "kerala":        "https://www.thehindu.com/news/national/kerala/feeder/default.rss",
    "tamil nadu":    "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "karnataka":     "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
}

# Google News RSS base URL template for topics not found in HINDU_FEEDS.
GOOGLE_NEWS_RSS_BASE: str = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)

# Default number of articles fetched per news query.
NEWS_DEFAULT_LIMIT: int = 5
# Maximum article summary length (chars) kept in tool output to stay within
# LLM context limits.
NEWS_SUMMARY_MAX_CHARS: int = 400
# Valid inclusive range for the article limit accepted by the news tool.
NEWS_TOOL_MIN_LIMIT: int = 1
NEWS_TOOL_MAX_LIMIT: int = 5


# Route Planning - OpenRouteService + Nominatim (src/osm/route_find.py)


# OpenRouteService driving-car directions endpoint.
ORS_URL: str = "https://api.openrouteservice.org/v2/directions/driving-car"
# Nominatim forward geocoding (place name -> coordinates) endpoint.
NOMINATIM_SEARCH_URL: str = "https://nominatim.openstreetmap.org/search"
# Nominatim reverse geocoding (coordinates -> place name) endpoint.
NOMINATIM_REVERSE_URL: str = "https://nominatim.openstreetmap.org/reverse"
# HTTP User-Agent for Nominatim requests (required by OSM usage policy).
OSM_USER_AGENT: str = "AITravelAgent/1.0"
# Default country code bias for forward geocoding. "in" = India.
OSM_DEFAULT_COUNTRY: str = "in"
# Nominatim rate-limit: minimum seconds between consecutive requests.
NOMINATIM_RATE_LIMIT_SECONDS: float = 1.0
# Nominatim request timeout (seconds).
NOMINATIM_TIMEOUT: int = 15
# LRU cache sizes for geocoding results to avoid redundant API calls.
GEOCODE_CACHE_SIZE: int = 256
REVERSE_GEOCODE_CACHE_SIZE: int = 1_024
# Decimal places used when rounding lat/lon for the reverse-geocode cache
REVERSE_GEOCODE_ROUND_DIGITS: int = 2
# Maximum distinct driving routes returned per trip query.
ORS_MAX_ROUTES: int = 3
# ORS (connect timeout, read timeout) in seconds.
ORS_CONNECT_TIMEOUT: int = 5
ORS_READ_TIMEOUT: int = 20
# Number of ORS retry attempts on transient server-side errors (5xx / 429).
ORS_RETRIES: int = 1
# Pause between ORS retry attempts (seconds).
ORS_RETRY_SLEEP: float = 1.5
# Route deduplication thresholds: two routes are considered identical if their
# distance and duration are both within these tolerances.
ORS_DEDUP_DISTANCE_THRESHOLD_M: int = 500   # metres
ORS_DEDUP_DURATION_THRESHOLD_S: int = 60    # seconds
# ORS alternative-route request parameters.
ORS_ALT_TARGET_COUNT: int = 3
ORS_ALT_WEIGHT_FACTOR: float = 1.6
ORS_ALT_SHARE_FACTOR: float = 0.6
# Named route preference variants fetched in parallel alongside alternatives
ROUTE_VARIANTS: list = [
    ("fastest",           {"preference": "fastest"}),
    ("shortest",          {"preference": "shortest"}),
    ("avoiding highways", {
        "preference": "recommended",
        "options": {"avoid_features": ["highways"]},
    }),
]
# Maximum number of named roads included in a route description string.
ORS_MAX_ROADS_IN_DESCRIPTION: int = 3
# Number of evenly-spaced points along the route geometry that are
ORS_WAYPOINT_COUNT: int = 2
# Precision used when decoding Google-encoded polyline geometry.
ORS_POLYLINE_PRECISION: int = 5
