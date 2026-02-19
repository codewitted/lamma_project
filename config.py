import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Generation Parameters
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "1"))

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTCASES_DIR = os.path.join(BASE_DIR, "testcases")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Hybrid Mode
FALLBACK_TO_CLOUD = os.getenv("FALLBACK_TO_CLOUD", "False").lower() == "true"
CLOUD_FALLBACK_MODEL = os.getenv("CLOUD_FALLBACK_MODEL", "gpt-4o")
