from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatOpenAI(
    model="openai/gpt-oss-20b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    max_tokens=300,
    temperature=0.3,
)

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', 'you are a helpful AI'),
        ('human', "{question}")
    ]
)

parser = StrOutputParser()

chain = prompt | model | parser

print('Welcome to Synapse AI')

while True:

    user_input = input('Type your question or type exit to exit the app: \n')

    if user_input.lower()=='exit':
        print("Thank you for using the app")
        break

    else: 

        response = chain.invoke({"question": user_input})

        print(response)