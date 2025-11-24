"""
Voice Recognition module using speech_recognition
"""
import speech_recognition as sr
import threading
import queue


class VoiceRecognition:
    """Voice recognition with Turkish and English support"""
    
    def __init__(self, language='tr-TR'):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.language = language
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self._init_microphone()
    
    def _init_microphone(self):
        """Initialize microphone"""
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            self.microphone = None
    
    def listen_once(self, timeout=5, phrase_time_limit=10):
        """
        Listen for a single command
        Returns: (success: bool, text: str or error message)
        """
        if not self.microphone:
            return False, "Mikrofon bulunamadı"
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech
            try:
                # Try Turkish first
                text = self.recognizer.recognize_google(audio, language='tr-TR')
                return True, text
            except sr.UnknownValueError:
                # Try English if Turkish fails
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    return True, text
                except sr.UnknownValueError:
                    return False, "Ses anlaşılamadı"
            except sr.RequestError as e:
                return False, f"API hatası: {e}"
        
        except sr.WaitTimeoutError:
            return False, "Zaman aşımı"
        except Exception as e:
            return False, f"Hata: {e}"
    
    def listen_continuous(self, callback, stop_event=None):
        """
        Continuously listen for commands
        callback: function(text: str, language: str) -> None
        stop_event: threading.Event to stop listening
        """
        if not self.microphone:
            return None
        
        self.is_listening = True
        
        def _listen_loop():
            error_count = 0
            max_errors = 5
            
            # Open microphone once, reuse it
            try:
                with self.microphone as source:
                    # Initial ambient noise adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    while self.is_listening and (stop_event is None or not stop_event.is_set()):
                        try:
                            # Listen for audio with shorter timeout
                            try:
                                audio = self.recognizer.listen(
                                    source, 
                                    timeout=0.5, 
                                    phrase_time_limit=8
                                )
                            except sr.WaitTimeoutError:
                                continue
                            
                            # Try to recognize
                            text = None
                            language = None
                            
                            # Try Turkish first
                            try:
                                text = self.recognizer.recognize_google(audio, language='tr-TR')
                                language = 'tr'
                                error_count = 0  # Reset error count on success
                            except sr.UnknownValueError:
                                # Try English
                                try:
                                    text = self.recognizer.recognize_google(audio, language='en-US')
                                    language = 'en'
                                    error_count = 0
                                except sr.UnknownValueError:
                                    continue
                                except sr.RequestError as e:
                                    error_count += 1
                                    if error_count >= max_errors:
                                        print(f"Too many API errors, pausing...")
                                        import time
                                        time.sleep(2)
                                        error_count = 0
                                    continue
                            except sr.RequestError as e:
                                error_count += 1
                                if error_count >= max_errors:
                                    print(f"Too many API errors, pausing...")
                                    import time
                                    time.sleep(2)
                                    error_count = 0
                                continue
                            
                            if text and callback:
                                callback(text, language)
                        
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            error_count += 1
                            print(f"Error in continuous listening: {e}")
                            if error_count >= max_errors:
                                print(f"Too many errors, resetting microphone...")
                                try:
                                    # Re-adjust for ambient noise
                                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                                    error_count = 0
                                except:
                                    break
                            continue
            except Exception as e:
                print(f"Fatal error in listen loop: {e}")
                self.is_listening = False
        
        thread = threading.Thread(target=_listen_loop, daemon=True)
        thread.start()
        return thread
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
    
    def set_language(self, language):
        """Set recognition language ('tr-TR' or 'en-US')"""
        self.language = language

