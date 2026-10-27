
from src.web.web_search import tavily_web_search

def main():
    query = "Vision Transformers for medical image analysis"

    results = tavily_web_search(query)

    print(results)


if __name__ == "__main__":
    main()
