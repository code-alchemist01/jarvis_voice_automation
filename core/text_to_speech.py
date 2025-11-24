"""
Text-to-Speech module with ElevenLabs and pyttsx3 fallback
"""
import pyttsx3
import threading
import queue
import io
from utils.config import config

# Try to import ElevenLabs
ELEVENLABS_AVAILABLE = False
try:
    from elevenlabs import generate, stream, set_api_key, Voice, VoiceSettings
    import pygame
    pygame.mixer.init()
    ELEVENLABS_AVAILABLE = True
    except ImportError:
        pass  # ElevenLabs not available, using pyttsx3 only

# Try to import pygame for audio playback
PYGAME_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    print("Pygame not available for audio playback")


class TextToSpeech:
    """Text-to-Speech engine with ElevenLabs (primary) and pyttsx3 (fallback) support"""
    
    def __init__(self):
        self.provider = config.get('tts.provider', 'elevenlabs' if ELEVENLABS_AVAILABLE else 'pyttsx3')
        self.elevenlabs_api_key = config.get('tts.elevenlabs.api_key', '')
        self.elevenlabs_voice_id = config.get('tts.elevenlabs.voice_id', '21m00Tcm4TlvDq8ikWAM')  # Default voice
        self.elevenlabs_model = config.get('tts.elevenlabs.model_id', 'eleven_multilingual_v2')
        self.elevenlabs_stability = config.get('tts.elevenlabs.stability', 0.5)
        self.elevenlabs_similarity = config.get('tts.elevenlabs.similarity_boost', 0.75)
        
        # Initialize ElevenLabs if available and configured
        if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            try:
                set_api_key(self.elevenlabs_api_key)
                print("ElevenLabs initialized successfully")
            except Exception as e:
                print(f"Error initializing ElevenLabs: {e}")
                self.provider = 'pyttsx3'
        
        # Initialize pyttsx3 as fallback
        self.pyttsx3_engine = None
        self.initialized = False
        self.speak_queue = queue.Queue()
        self.speaking = False
        self.speak_thread = None
        self._init_pyttsx3()
        self._start_speak_thread()
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine as fallback"""
        try:
            self.pyttsx3_engine = pyttsx3.init()
            
            # Set properties from config
            rate = config.get('tts.rate', 150)
            volume = config.get('tts.volume', 0.9)
            
            self.pyttsx3_engine.setProperty('rate', rate)
            self.pyttsx3_engine.setProperty('volume', volume)
            
            # Try to set Turkish voice if available
            voices = self.pyttsx3_engine.getProperty('voices')
            turkish_voice = None
            for voice in voices:
                if 'turkish' in voice.name.lower() or 'tr' in voice.id.lower():
                    turkish_voice = voice.id
                    break
            
            if turkish_voice:
                self.pyttsx3_engine.setProperty('voice', turkish_voice)
            
            self.initialized = True
        except Exception as e:
            print(f"Error initializing pyttsx3 engine: {e}")
            self.initialized = False
    
    def _start_speak_thread(self):
        """Start the speak thread that processes queue"""
        def _speak_worker():
            while True:
                try:
                    item = self.speak_queue.get()
                    if item is None:  # Poison pill
                        break
                    
                    text, language = item if isinstance(item, tuple) else (item, 'tr')
                    
                    # Try ElevenLabs first if configured
                    if self.provider == 'elevenlabs' and ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
                        try:
                            self._speak_elevenlabs(text, language)
                            self.speak_queue.task_done()
                            continue
                        except Exception as e:
                            print(f"ElevenLabs error, falling back to pyttsx3: {e}")
                            # Fall through to pyttsx3
                    
                    # Use pyttsx3 (fallback or primary)
                    if self.initialized:
                        try:
                            self._speak_pyttsx3(text, language)
                        except Exception as e:
                            print(f"Error in pyttsx3 speak: {e}")
                    
                    self.speak_queue.task_done()
                    
                except Exception as e:
                    print(f"Error in TTS worker thread: {e}")
                    try:
                        self.speak_queue.task_done()
                    except:
                        pass
        
        self.speak_thread = threading.Thread(target=_speak_worker, daemon=True)
        self.speak_thread.start()
    
    def _speak_elevenlabs(self, text, language='tr'):
        """Speak using ElevenLabs API"""
        if not ELEVENLABS_AVAILABLE or not self.elevenlabs_api_key:
            raise Exception("ElevenLabs not available")
        
        try:
            # Generate audio
            audio = generate(
                text=text,
                voice=self.elevenlabs_voice_id,
                model=self.elevenlabs_model,
                stream=False
            )
            
            # Play audio using pygame
            if PYGAME_AVAILABLE:
                audio_stream = io.BytesIO(audio)
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
            else:
                # Fallback: save to temp file and play
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                    f.write(audio)
                    temp_path = f.name
                
                try:
                    import subprocess
                    import platform
                    if platform.system() == 'Windows':
                        os.startfile(temp_path)
                    elif platform.system() == 'Darwin':
                        subprocess.run(['afplay', temp_path])
                    else:
                        subprocess.run(['mpg123', temp_path])
                    
                    # Wait a bit for playback
                    import time
                    time.sleep(len(text) * 0.1)  # Rough estimate
                finally:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error in ElevenLabs TTS: {e}")
            raise
    
    def _speak_pyttsx3(self, text, language='tr'):
        """Speak using pyttsx3 (fallback)"""
        if not self.initialized:
            return
        
        try:
            # Create a new engine instance for each speak to avoid "run loop already started" error
            engine = pyttsx3.init()
            
            # Set properties
            rate = config.get('tts.rate', 150)
            volume = config.get('tts.volume', 0.9)
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            
            # Try to set voice based on language
            try:
                voices = engine.getProperty('voices')
                selected_voice = None
                for voice in voices:
                    if language == 'tr' and ('turkish' in voice.name.lower() or 'tr' in voice.id.lower()):
                        selected_voice = voice.id
                        break
                    elif language == 'en' and ('english' in voice.name.lower() or 'en' in voice.id.lower()):
                        selected_voice = voice.id
                        break
                
                if selected_voice:
                    engine.setProperty('voice', selected_voice)
            except:
                pass
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"Error in pyttsx3 speak: {e}")
            raise
    
    def speak(self, text, language='tr'):
        """Speak text asynchronously"""
        if not text:
            return None
        
        try:
            # Add to queue
            self.speak_queue.put((text, language))
            return True
        except Exception as e:
            print(f"Error queuing TTS: {e}")
            return None
    
    def speak_sync(self, text, language='tr'):
        """Speak text synchronously (blocks until done)"""
        if not text:
            return
        
        # Try ElevenLabs first
        if self.provider == 'elevenlabs' and ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            try:
                self._speak_elevenlabs(text, language)
                return
            except Exception as e:
                print(f"ElevenLabs sync error, using pyttsx3: {e}")
        
        # Fallback to pyttsx3
        self._speak_pyttsx3(text, language)
    
    def set_rate(self, rate):
        """Set speech rate (for pyttsx3)"""
        if self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.setProperty('rate', rate)
                config.set('tts.rate', rate)
            except:
                pass
    
    def set_volume(self, volume):
        """Set speech volume (0.0 to 1.0)"""
        if self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.setProperty('volume', volume)
                config.set('tts.volume', volume)
            except:
                pass
    
    def set_provider(self, provider):
        """Switch TTS provider (elevenlabs or pyttsx3)"""
        if provider in ['elevenlabs', 'pyttsx3']:
            self.provider = provider
            config.set('tts.provider', provider)
            return True
        return False
    
    def set_elevenlabs_settings(self, stability=None, similarity_boost=None):
        """Update ElevenLabs voice settings"""
        if stability is not None:
            self.elevenlabs_stability = stability
            config.set('tts.elevenlabs.stability', stability)
        if similarity_boost is not None:
            self.elevenlabs_similarity = similarity_boost
            config.set('tts.elevenlabs.similarity_boost', similarity_boost)
    
    def stop(self):
        """Stop current speech"""
        # Clear queue
        try:
            while not self.speak_queue.empty():
                try:
                    self.speak_queue.get_nowait()
                except:
                    break
        except:
            pass
        
        # Stop pygame if playing
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        
        # Stop pyttsx3
        if self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.stop()
            except:
                pass
