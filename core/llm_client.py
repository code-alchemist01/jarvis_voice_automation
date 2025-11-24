"""
LM Studio API Client for JARVIS
"""
import requests
import json
import time
from typing import List, Dict, Optional, Tuple
from utils.config import config


class LLMClient:
    """Client for LM Studio OpenAI-compatible API"""
    
    def __init__(self):
        self.api_url = config.get('llm.api_url', 'http://localhost:1234/v1/chat/completions')
        self.model = config.get('llm.model', 'qwen3-4b-2507')
        self.temperature = config.get('llm.temperature', 0.7)
        self.max_tokens = config.get('llm.max_tokens', 200)
        self.timeout = config.get('llm.timeout', 10)
        self.enabled = config.get('llm.enabled', True)
        self._connection_ok = None
        self._last_check = 0
    
    def is_available(self) -> bool:
        """Check if LM Studio API is available"""
        if not self.enabled:
            return False
        
        # Cache connection check for 30 seconds
        current_time = time.time()
        if self._connection_ok is not None and (current_time - self._last_check) < 30:
            return self._connection_ok
        
        try:
            # Simple health check
            response = requests.get(
                self.api_url.replace('/v1/chat/completions', '/v1/models'),
                timeout=2
            )
            self._connection_ok = response.status_code == 200
        except:
            self._connection_ok = False
        
        self._last_check = current_time
        return self._connection_ok
    
    def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[bool, str]:
        """
        Send chat request to LM Studio
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
        
        Returns:
            (success: bool, response: str or error message)
        """
        if not self.enabled:
            return False, "LLM devre dışı"
        
        if not self.is_available():
            return False, "LM Studio bağlantısı yok"
        
        try:
            # Prepare messages
            api_messages = []
            
            # Add system prompt if provided
            if system_prompt:
                api_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add conversation messages
            api_messages.extend(messages)
            
            # Prepare request
            payload = {
                "model": self.model,
                "messages": api_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            # Send request
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return True, content.strip()
            else:
                return False, f"API hatası: {response.status_code}"
        
        except requests.exceptions.Timeout:
            return False, "Zaman aşımı - LM Studio yanıt vermedi"
        except requests.exceptions.ConnectionError:
            self._connection_ok = False
            return False, "LM Studio bağlantı hatası"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def parse_command(self, user_input: str, system_prompt: str) -> Tuple[bool, Dict, str]:
        """
        Parse user command using LLM
        
        Returns:
            (success: bool, command_data: dict, raw_response: str)
        """
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        success, response = self.chat(messages, system_prompt)
        
        if not success:
            return False, {}, response
        
        # Try to parse JSON from response
        try:
            # Extract JSON from response (might be wrapped in text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                command_data = json.loads(json_str)
                return True, command_data, response
            else:
                # No JSON found, treat as chat response
                return True, {"intent": "chat", "response": response}, response
        
        except json.JSONDecodeError:
            # Response is not JSON, treat as chat
            return True, {"intent": "chat", "response": response}, response
    
    def get_simple_response(self, user_input: str, context: List[Dict[str, str]] = None) -> Tuple[bool, str]:
        """
        Get simple text response from LLM (for chat)
        
        Args:
            user_input: User's message
            context: Optional conversation history
        
        Returns:
            (success: bool, response: str)
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.extend(context)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return self.chat(messages)

