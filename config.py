import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

#Load the contents of .env
load_dotenv()

MODEL = "gpt-4.1-mini"

#Key recovery
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY: 
    raise RuntimeError(
        "OPENAI_API_KEY not found. Check that the .env file exists"
    )

CSV_PATH = os.path.join("Data", "Sample - Superstore.csv")

#LLM factory
def get_llm(temperature : float = 0):
    return ChatOpenAI(model = MODEL, temperature = temperature)

#Maximum number of coder execution
MAX_CODE_ATTEMPTS = 3