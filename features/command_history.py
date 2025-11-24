"""
Command history and learning features
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from utils.config import config


HISTORY_FILE = Path(__file__).parent.parent / "command_history.json"


def load_history():
    """Load command history from file"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading history: {e}")
        return []


def save_history(history):
    """Save command history to file"""
    try:
        # Keep only last 1000 commands
        history = history[-1000:]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")


def add_command(command_text, success=True, response=""):
    """Add a command to history"""
    try:
        history = load_history()
        history.append({
            'command': command_text,
            'success': success,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        save_history(history)
    except Exception as e:
        print(f"Error adding command to history: {e}")


def get_command_stats():
    """Get command usage statistics"""
    try:
        history = load_history()
        if not history:
            return True, "Henüz komut geçmişi yok."
        
        total_commands = len(history)
        successful = sum(1 for cmd in history if cmd.get('success', False))
        success_rate = (successful / total_commands * 100) if total_commands > 0 else 0
        
        # Most common commands
        commands = [cmd['command'].lower() for cmd in history]
        command_counts = Counter(commands)
        top_commands = command_counts.most_common(5)
        
        stats_text = f"Toplam komut: {total_commands}\n"
        stats_text += f"Başarı oranı: {success_rate:.1f}%\n"
        stats_text += f"Başarılı: {successful}, Başarısız: {total_commands - successful}\n\n"
        stats_text += "En çok kullanılan komutlar:\n"
        for i, (cmd, count) in enumerate(top_commands, 1):
            stats_text += f"{i}. {cmd} ({count} kez)\n"
        
        return True, stats_text
    except Exception as e:
        print(f"Error getting stats: {e}")
        return False, f"İstatistikler alınırken hata oluştu: {str(e)}"


def get_frequent_commands(limit=5):
    """Get most frequently used commands"""
    try:
        history = load_history()
        if not history:
            return True, "Henüz komut geçmişi yok."
        
        commands = [cmd['command'].lower() for cmd in history]
        command_counts = Counter(commands)
        top_commands = command_counts.most_common(limit)
        
        result = "Sık kullanılan komutlar:\n"
        for i, (cmd, count) in enumerate(top_commands, 1):
            result += f"{i}. {cmd} ({count} kez)\n"
        
        return True, result
    except Exception as e:
        print(f"Error getting frequent commands: {e}")
        return False, f"Sık kullanılan komutlar alınırken hata oluştu: {str(e)}"


def get_recent_commands(days=1, limit=10):
    """Get recent commands"""
    try:
        history = load_history()
        if not history:
            return True, "Henüz komut geçmişi yok."
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            cmd for cmd in history
            if datetime.fromisoformat(cmd['timestamp']) >= cutoff
        ]
        recent = recent[-limit:]
        
        if not recent:
            return True, f"Son {days} günde komut bulunamadı."
        
        result = f"Son {days} gündeki komutlar:\n"
        for i, cmd in enumerate(reversed(recent), 1):
            timestamp = datetime.fromisoformat(cmd['timestamp']).strftime('%H:%M')
            status = "✓" if cmd.get('success') else "✗"
            result += f"{i}. [{timestamp}] {status} {cmd['command']}\n"
        
        return True, result
    except Exception as e:
        print(f"Error getting recent commands: {e}")
        return False, f"Son komutlar alınırken hata oluştu: {str(e)}"

