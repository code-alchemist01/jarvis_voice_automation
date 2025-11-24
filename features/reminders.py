"""
Reminders and timers features
"""
import json
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from core.text_to_speech import TextToSpeech


REMINDERS_FILE = Path(__file__).parent.parent / "reminders.json"
tts = TextToSpeech()


def load_reminders():
    """Load reminders from file"""
    try:
        if REMINDERS_FILE.exists():
            with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading reminders: {e}")
        return []


def save_reminders(reminders):
    """Save reminders to file"""
    try:
        with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving reminders: {e}")
        return False


def parse_time_duration(text):
    """Parse time duration from text (e.g., '10 dakika', '1 saat', '30 saniye')"""
    text_lower = text.lower()
    
    # Extract numbers
    import re
    numbers = re.findall(r'\d+', text)
    if not numbers:
        return None
    
    amount = int(numbers[0])
    
    # Parse time units
    if any(word in text_lower for word in ['saniye', 'second']):
        return timedelta(seconds=amount)
    elif any(word in text_lower for word in ['dakika', 'minute', 'min']):
        return timedelta(minutes=amount)
    elif any(word in text_lower for word in ['saat', 'hour', 'hr']):
        return timedelta(hours=amount)
    elif any(word in text_lower for word in ['gün', 'day']):
        return timedelta(days=amount)
    else:
        # Default to minutes
        return timedelta(minutes=amount)


def create_reminder(message, duration_str=None, absolute_time=None):
    """Create a reminder"""
    try:
        reminders = load_reminders()
        
        if absolute_time:
            reminder_time = datetime.fromisoformat(absolute_time)
        elif duration_str:
            duration = parse_time_duration(duration_str)
            if not duration:
                return False, "Zaman süresi anlaşılamadı. Örneğin: '10 dakika', '1 saat'"
            reminder_time = datetime.now() + duration
        else:
            return False, "Zaman belirtilmedi"
        
        reminder = {
            'id': len(reminders) + 1,
            'message': message,
            'time': reminder_time.isoformat(),
            'created': datetime.now().isoformat(),
            'active': True
        }
        
        reminders.append(reminder)
        save_reminders(reminders)
        
        # Start timer thread
        _start_reminder_timer(reminder)
        
        time_str = reminder_time.strftime("%H:%M")
        return True, f"Hatırlatıcı oluşturuldu: '{message}' - {time_str}"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def _start_reminder_timer(reminder):
    """Start a timer thread for reminder"""
    def reminder_callback():
        reminder_time = datetime.fromisoformat(reminder['time'])
        wait_time = (reminder_time - datetime.now()).total_seconds()
        
        if wait_time > 0:
            time.sleep(wait_time)
            
            # Check if reminder is still active
            reminders = load_reminders()
            for r in reminders:
                if r['id'] == reminder['id'] and r.get('active', True):
                    # Trigger reminder
                    tts.speak(f"Hatırlatma: {reminder['message']}")
                    
                    # Mark as inactive
                    r['active'] = False
                    save_reminders(reminders)
                    break
    
    thread = threading.Thread(target=reminder_callback, daemon=True)
    thread.start()


def list_reminders(active_only=True):
    """List reminders"""
    try:
        reminders = load_reminders()
        
        if active_only:
            reminders = [r for r in reminders if r.get('active', True)]
        
        if not reminders:
            return True, "Aktif hatırlatıcı bulunmuyor"
        
        result = f"{len(reminders)} hatırlatıcı:\n"
        for reminder in reminders[:10]:  # Limit to 10
            reminder_time = datetime.fromisoformat(reminder['time'])
            time_str = reminder_time.strftime("%Y-%m-%d %H:%M")
            status = "Aktif" if reminder.get('active', True) else "Tamamlandı"
            result += f"- [{reminder['id']}] {reminder['message']} - {time_str} ({status})\n"
        
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def delete_reminder(reminder_id):
    """Delete a reminder"""
    try:
        reminders = load_reminders()
        reminders = [r for r in reminders if r['id'] != reminder_id]
        
        if save_reminders(reminders):
            return True, f"Hatırlatıcı {reminder_id} silindi"
        else:
            return False, "Hatırlatıcı silinemedi"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def start_timer(duration_str):
    """Start a countdown timer"""
    try:
        duration = parse_time_duration(duration_str)
        if not duration:
            return False, "Zaman süresi anlaşılamadı"
        
        total_seconds = int(duration.total_seconds())
        
        def timer_callback():
            time.sleep(total_seconds)
            tts.speak("Zamanlayıcı bitti!")
        
        thread = threading.Thread(target=timer_callback, daemon=True)
        thread.start()
        
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        if minutes > 0:
            time_str = f"{minutes} dakika {seconds} saniye"
        else:
            time_str = f"{seconds} saniye"
        
        return True, f"Zamanlayıcı başlatıldı: {time_str}"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


# Load and start existing active reminders on import
def _initialize_reminders():
    """Initialize and start existing active reminders"""
    try:
        reminders = load_reminders()
        for reminder in reminders:
            if reminder.get('active', True):
                reminder_time = datetime.fromisoformat(reminder['time'])
                if reminder_time > datetime.now():
                    _start_reminder_timer(reminder)
    except:
        pass


# Initialize on module load
_initialize_reminders()

