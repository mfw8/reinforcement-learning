import requests
from typing import Optional
from config import Config


class LLaMAInterface:
    # Handles communication with LLaMA API
    
    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model
        self.config = Config()
    
    def generate(self, prompt: str) -> Optional[str]:
        # Send prompt to LLaMA and get response
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.TEMPERATURE,
                "top_p": self.config.TOP_P,
                "max_tokens": self.config.MAX_TOKENS
            }
        }
        
        try:
            print(f"Connecting to LLaMA ({self.model})...")
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response from model')
            
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to LLaMA. Is it running?"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Try again."
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
    
    def test_connection(self) -> bool:
        # Test if LLaMA is accessible
        try:
            response = self.generate("Say 'OK' if you can read this.")
            return response is not None and "Error:" not in response
        except:
            return False