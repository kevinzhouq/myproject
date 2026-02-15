import requests
import json
from src.config import Config

class LLMClient:
    def generate(self, prompt):
        """
        Generate text using Ollama API.
        """
        try:
            payload = {
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3, # Low temperature for more deterministic output
                    "num_ctx": 4096      # Context window
                }
            }
            # Timeout set to 3 minutes as local inference can be slow
            response = requests.post(Config.OLLAMA_API_URL, json=payload, timeout=180)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Ollama at {Config.OLLAMA_API_URL}. Is it running?")
            return ""
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""
