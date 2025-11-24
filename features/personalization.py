"""
Personalization features with advanced profile management
"""
import json
from pathlib import Path
from datetime import datetime
from utils.config import config

PROFILES_FILE = Path(__file__).parent.parent / "user_profiles.json"


def load_profiles():
    """Load user profiles"""
    try:
        if PROFILES_FILE.exists():
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading profiles: {e}")
        return {}


def save_profiles(profiles):
    """Save user profiles"""
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving profiles: {e}")


def set_tts_rate(rate):
    """Set TTS speech rate"""
    try:
        config.set('tts.rate', rate)
        return True, f"Konuşma hızı {rate} olarak ayarlandı"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def set_tts_volume(volume):
    """Set TTS volume (0.0 to 1.0)"""
    try:
        if 0.0 <= volume <= 1.0:
            config.set('tts.volume', volume)
            return True, f"Ses seviyesi {int(volume * 100)}% olarak ayarlandı"
        else:
            return False, "Ses seviyesi 0 ile 1 arasında olmalı"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def set_tts_provider(provider):
    """Set TTS provider (elevenlabs or pyttsx3)"""
    try:
        if provider in ['elevenlabs', 'pyttsx3']:
            config.set('tts.provider', provider)
            return True, f"TTS sağlayıcı {provider} olarak ayarlandı"
        else:
            return False, "Geçersiz sağlayıcı. 'elevenlabs' veya 'pyttsx3' kullanın"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def set_default_app(app_name, app_path):
    """Set default application for a name"""
    try:
        apps = config.get('applications', {})
        apps[app_name] = app_path
        config.set('applications', apps)
        return True, f"Varsayılan uygulama ayarlandı: {app_name}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def create_profile(profile_name, settings):
    """Create a new user profile"""
    try:
        profiles = load_profiles()
        profiles[profile_name.lower()] = {
            'name': profile_name,
            'settings': settings,
            'created_at': datetime.now().isoformat()
        }
        save_profiles(profiles)
        return True, f"Profil oluşturuldu: {profile_name}"
    except Exception as e:
        print(f"Error creating profile: {e}")
        return False, f"Profil oluşturulurken hata oluştu: {str(e)}"


def load_profile(profile_name):
    """Load and apply a user profile"""
    try:
        profiles = load_profiles()
        profile = profiles.get(profile_name.lower())
        
        if not profile:
            return False, f"'{profile_name}' adında profil bulunamadı"
        
        settings = profile.get('settings', {})
        
        # Apply settings
        if 'tts_rate' in settings:
            config.set('tts.rate', settings['tts_rate'])
        if 'tts_volume' in settings:
            config.set('tts.volume', settings['tts_volume'])
        if 'tts_provider' in settings:
            config.set('tts.provider', settings['tts_provider'])
        
        return True, f"Profil yüklendi: {profile_name}"
    except Exception as e:
        print(f"Error loading profile: {e}")
        return False, f"Profil yüklenirken hata oluştu: {str(e)}"


def list_profiles():
    """List all user profiles"""
    try:
        profiles = load_profiles()
        
        if not profiles:
            return True, "Kayıtlı profil bulunamadı"
        
        result = "Kayıtlı profiller:\n"
        for name, profile in profiles.items():
            result += f"- {profile['name']}\n"
        
        return True, result
    except Exception as e:
        print(f"Error listing profiles: {e}")
        return False, f"Profiller listelenirken hata oluştu: {str(e)}"


def get_time_based_profile():
    """Get profile based on time of day"""
    try:
        from datetime import datetime
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return 'sabah'
        elif 12 <= hour < 18:
            return 'öğleden sonra'
        elif 18 <= hour < 22:
            return 'akşam'
        else:
            return 'gece'
    except:
        return None

