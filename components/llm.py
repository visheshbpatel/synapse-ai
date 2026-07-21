from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


model = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    max_tokens=200,
    temperature=0.3,
    streaming=True
)