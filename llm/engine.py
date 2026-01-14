import json
import ollama
try:
    from config import MODEL_ID, OLLAMA_URL
except ImportError:
    # Fallback/Updates in case config wasn't reloaded properly in some envs
    MODEL_ID = "llama3.1:8b"
    OLLAMA_URL = "http://localhost:11434"

from utils import parse_code_block

import subprocess
import time
import sys

class JarvisLLM:
    def __init__(self, mock=False):
        self.mock = mock
        self.client = ollama.Client(host=OLLAMA_URL)
        self.conversation_history = []  # Memory: List of {"role": "user"|"assistant", "content": ...}
        
        if not self.mock:
            self._ensure_service_running()
            self._ensure_model_available()
        else:
            print("Running in MOCK mode. Ollama checks skipped.")

    def _ensure_service_running(self):
        print(f"Connecting to Ollama at {OLLAMA_URL}...")
        try:
            self.client.list()
            print("Ollama is already running.")
        except Exception:
            print("Ollama not reachable. Attempting to start 'ollama serve'...")
            try:
                # Start ollama serve in a new process, detached
                if sys.platform == "win32":
                    subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen(["ollama", "serve"], start_new_session=True)
                
                print("Waiting for Ollama to start...", end="", flush=True)
                for _ in range(20): # Wait up to 20 seconds
                    try:
                        time.sleep(1)
                        self.client.list()
                        print("\nOllama started successfully.")
                        return
                    except:
                        print(".", end="", flush=True)
                print("\nFailed to start Ollama automatically. Please run 'ollama serve' manually.")
                sys.exit(1)
            except FileNotFoundError:
                print("\n'ollama' executable not found. Please install Ollama from ollama.com")
                sys.exit(1)

    def _ensure_model_available(self):
        print(f"Checking for model '{MODEL_ID}'...")
        try:
            models = self.client.list()
            # ollama.list returns a dict with 'models' key which is a list of dicts
            installed_models = [m['model'] for m in models.get('models', [])]
            
            # Simple check, might need fuzzy match if tags differ (e.g. :latest)
            if any(MODEL_ID in m for m in installed_models):
                print(f"Model '{MODEL_ID}' is ready.")
            else:
                print(f"Model '{MODEL_ID}' not found. Downloading (this may take a while)...")
                # Stream pull progress
                stream = self.client.pull(MODEL_ID, stream=True)
                for chunk in stream:
                    status = chunk.get('status', '')
                    completed = chunk.get('completed', 0)
                    total = chunk.get('total', 0)
                    if total:
                        percent = int((completed / total) * 100)
                        print(f"\rDownloading {MODEL_ID}: {status} - {percent}%", end="", flush=True)
                    else:
                        print(f"\rDownloading {MODEL_ID}: {status}", end="", flush=True)
                print(f"\nModel '{MODEL_ID}' downloaded successfully.")
                
        except Exception as e:
            print(f"Error checking/pulling model: {e}")
            sys.exit(1)

    def add_message(self, role, content):
        """Manually add a message to history."""
        self.conversation_history.append({"role": role, "content": str(content)})

    def generate_action(self, user_input, tools_schema):
        """
        Generates the JSON response. 
        If user_input is provided, it's added to history.
        If None, it generates based on existing history (continuation).
        """
        # Load system prompt
        try:
            with open("system_prompt.txt", "r", encoding="utf-8") as f:
                base_prompt = f.read()
        except FileNotFoundError:
            base_prompt = "You are an AI assistant."

        # Append tools to instructions
        full_system_prompt = f"{base_prompt}\n\nAVAILABLE TOOLS:\n{tools_schema}\n\nREMEMBER: Return ONLY JSON."

        # Add User Input to Memory if present
        if user_input:
            self.conversation_history.append({"role": "user", "content": user_input})

        # Build context from history (Last 10 exchanges for better context)
        history_text = ""
        for msg in self.conversation_history[-10:]:
            history_text += f"\n{msg['role'].capitalize()}: {msg['content']}"

        # If user_input was None, we are likely in a loop waiting for the next step
        # The prompt ends with the history, waiting for Assistant completion
        full_prompt = f"{full_system_prompt}\n\nPREVIOUS CONVERSATION:{history_text}\n\nJarvis:"

        if self.mock:
             if user_input and "youtube" in user_input.lower():
                 return '{"thought": "Mocking youtube search.", "type": "action", "content": {"action_name": "youtube_search", "args": {"query": "python tutorial"}}}'
             return '{"thought": "Mocking chat.", "type": "chat", "content": "I am in Mock mode."}'

        try:
            response = self.client.generate(
                model=MODEL_ID,
                prompt=full_prompt,
                format="json",
                stream=False,
                options={
                    "temperature": 0.7,
                    "num_predict": 4096,   # Allow long responses
                    "num_ctx": 4096,       # Larger context window
                }
            )
            resp_str = response.get('response', '')
            
            # Update Memory with Assistant's raw response
            self.conversation_history.append({"role": "assistant", "content": resp_str})

            return resp_str
        except Exception as e:
            return f'{{"thought": "Error generation", "type": "chat", "content": "Error: {str(e)}"}}'
