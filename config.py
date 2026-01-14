# Configuration for Jarvis Assistant

# Model Configuration
# Use the model tag as it appears in 'ollama list'
# Examples: "codellama", "llama3", "mistral"
MODEL_ID = "llama3.1:8b" 

# OLLAMA Configuration
OLLAMA_URL = "http://localhost:11434" # Default Ollama URL

# (Old Transformers Config - Ignored if using Ollama)
LOAD_IN_4BIT = True
MODEL_CACHE_DIR = None

# API Keys
# Leave empty if you don't use these specific actions or rely on libraries that don't need them
GOOGLE_API_KEY = "AIzaSyDCMoSwDzUampLmiheirJAFw_ABchHdfXE"
GOOGLE_CSE_ID = "077e28e62d4e243ef"
