import os
from dotenv import load_dotenv
import httpx
from openai import OpenAI
from tavily import TavilyClient
from open_deep_research.graph import run_workflow
"""2025 June 
"""

# 1️⃣ Load config
load_dotenv()
OPENAI_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_PROXY = os.getenv("OPENAI_PROXY_URL")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_HTTP_PROXY = os.getenv("TAVILY_HTTP_PROXY")
TAVILY_HTTPS_PROXY = os.getenv("TAVILY_HTTPS_PROXY")

# 2️⃣ LLM client (self‑hosted with proxy)
client_opts = {"api_key": "dummy", "base_url": OPENAI_BASE}
if OPENAI_PROXY:
    client_opts["http_client"] = httpx.Client(proxies={"all://": OPENAI_PROXY})
llm_client = OpenAI(**client_opts)

# 3️⃣ Tavily client (proxy enabled)
tavily = TavilyClient(
    TAVILY_API_KEY,
    proxies={"http": TAVILY_HTTP_PROXY, "https": TAVILY_HTTPS_PROXY}
)

# 4️⃣ Define search
def custom_search(topic: str):
    resp = tavily.search(
        query=topic,
        search_depth="advanced",
        max_results=5,
        include_raw_content=True
    )
    return resp["results"]

# 5️⃣ Define LLM wrapper
def llm_fn(prompt: str) -> str:
    resp = llm_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

# 6️⃣ Combine search + LLM
def research_company(company_name: str) -> str:
    return run_workflow(
        topic=company_name,
        search_fn=custom_search,
        llm_fn=llm_fn
    )

# 🏁 Run it
if __name__ == "__main__":
    report = research_company("OpenAI")
    print(report)
