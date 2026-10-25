from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=os.getenv("GROQ_BASE_URL"),
    # max_tokens=300,
    temperature=0.3,
    streaming=True
)