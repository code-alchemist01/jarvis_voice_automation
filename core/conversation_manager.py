"""
Conversation history management for JARVIS
"""
import json
from pathlib import Path
from typing import List, Dict
from utils.config import config


CONVERSATION_FILE = Path(__file__).parent.parent / "conversation_history.json"
MAX_HISTORY = config.get('conversation.max_history', 10)


class ConversationManager:
    """Manages conversation history for context-aware responses"""
    
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.user_name = config.get('user.name', 'Kullanıcı')
        self.max_history = MAX_HISTORY
        self.save_history = config.get('conversation.save_history', False)
        self.load_history()
    
    def load_history(self):
        """Load conversation history from file"""
        if not self.save_history or not CONVERSATION_FILE.exists():
            return
        
        try:
            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = data.get('history', [])
                # Limit history
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            self.history = []
    
    def save_history_to_file(self):
        """Save conversation history to file"""
        if not self.save_history:
            return
        
        try:
            with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.history,
                    'user_name': self.user_name
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving conversation history: {e}")
    
    def add_message(self, role: str, content: str):
        """Add a message to history"""
        message = {"role": role, "content": content}
        self.history.append(message)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        if self.save_history:
            self.save_history_to_file()
    
    def get_recent_context(self, n: int = None) -> List[Dict[str, str]]:
        """Get recent conversation context"""
        if n is None:
            n = self.max_history
        return self.history[-n:] if len(self.history) > n else self.history
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        if self.save_history:
            self.save_history_to_file()
    
    def update_user_name(self, name: str):
        """Update user name"""
        self.user_name = name
        config.set('user.name', name)
    
    def get_user_name(self) -> str:
        """Get user name"""
        return self.user_name

