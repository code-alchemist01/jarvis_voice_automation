"""
Notes management features
"""
import json
from pathlib import Path
from datetime import datetime


NOTES_FILE = Path(__file__).parent.parent / "notes.json"


def load_notes():
    """Load notes from file"""
    try:
        if NOTES_FILE.exists():
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading notes: {e}")
        return []


def save_notes(notes):
    """Save notes to file"""
    try:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving notes: {e}")
        return False


def save_note(note_text):
    """Save a new note"""
    try:
        notes = load_notes()
        
        new_note = {
            'id': len(notes) + 1,
            'text': note_text,
            'timestamp': datetime.now().isoformat()
        }
        
        notes.append(new_note)
        
        if save_notes(notes):
            return True, f"Not kaydedildi: {note_text[:50]}..."
        else:
            return False, "Not kaydedilemedi"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def list_notes(limit=5):
    """List recent notes"""
    try:
        notes = load_notes()
        
        if not notes:
            return True, "Kayıtlı not bulunmuyor"
        
        # Get most recent notes
        recent_notes = notes[-limit:] if len(notes) > limit else notes
        
        result = f"Son {len(recent_notes)} not:\n"
        for note in recent_notes:
            timestamp = datetime.fromisoformat(note['timestamp']).strftime('%Y-%m-%d %H:%M')
            result += f"- {note['text'][:50]} ({timestamp})\n"
        
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def delete_note(note_id):
    """Delete a note by ID"""
    try:
        notes = load_notes()
        notes = [n for n in notes if n['id'] != note_id]
        
        if save_notes(notes):
            return True, f"Not {note_id} silindi"
        else:
            return False, "Not silinemedi"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"

