"""
Command processor - routes commands to appropriate feature modules
Now with LLM integration for natural language understanding
"""
import re
import json
from features import (system_control, file_operations, web_search, weather, 
                     calculator, notes, reminders, media_control, system_monitor,
                     security, email, calendar, command_history, entertainment,
                     personalization)
from core.llm_client import LLMClient
from core.prompts import get_system_prompt, get_chat_prompt
from core.conversation_manager import ConversationManager
from core.multi_step_processor import MultiStepProcessor
import features.command_history as command_history_module

# Import optional modules
try:
    from features import spotify_control
except ImportError:
    spotify_control = None

try:
    from features import smart_home
except ImportError:
    smart_home = None

try:
    from features import scenarios
except ImportError:
    scenarios = None


class CommandProcessor:
    """Processes voice commands and routes them to appropriate modules"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.conversation_manager = ConversationManager()
        self.use_llm = self.llm_client.is_available()
        self.multi_step_processor = MultiStepProcessor(self)
        
        # Fallback regex patterns (kept for when LLM is unavailable)
        self.turkish_patterns = {
            'open_app': [
                r'(aç|open)\s+(.+?)(?:i|ı|u|ü|ü|yi|yı|yu|yü)?$',
                r'(.+?)(?:i|ı|u|ü|ü|yi|yı|yu|yü)?\s+aç',
            ],
            'volume_up': [
                r'ses\s+(seviyesini|seviyesi)\s+(artır|yükselt|aç)',
                r'sesi\s+(artır|yükselt|aç)',
            ],
            'volume_down': [
                r'ses\s+(seviyesini|seviyesi)\s+(azalt|düşür|kapat)',
                r'sesi\s+(azalt|düşür|kapat)',
            ],
            'weather': [
                r'(hava|weather)\s+(durumu|nasıl|how)',
                r'bugün\s+hava\s+nasıl',
            ],
            'calculate': [
                r'(.+?)\s+(artı|eksi|çarpı|bölü|kere)\s+(.+?)\s+(kaç|edir|eder|eşittir)',
            ],
            'save_note': [
                r'not\s+(kaydet|save)\s*:?\s*(.+)',
            ],
            'list_notes': [
                r'notlar(ı|i)?\s+(listele|göster|show)',
            ],
            'search': [
                r'google.*ara\s*:?\s*(.+)',
                r'ara\s*:?\s*(.+)',
            ],
        }
    
    def process_command(self, text, language='tr'):
        """Process a command using LLM first, fallback to regex"""
        text = text.strip()
        original_text = text
        
        # Add to conversation history
        self.conversation_manager.add_message("user", text)
        
        # Check for multi-step command first
        if self.use_llm and self.llm_client.is_available():
            success, message = self.multi_step_processor.process_multi_step(text)
            if success is not None:
                # It was a multi-step command
                try:
                    command_history_module.add_command(original_text, success, message)
                except:
                    pass
                return success, message
        
        # Try LLM first if available
        if self.use_llm and self.llm_client.is_available():
            success, response = self._process_with_llm(text, language)
        else:
            # Fallback to regex patterns
            success, response = self._process_with_regex(text.lower(), language, original_text)
        
        # Add command to history
        try:
            command_history_module.add_command(original_text, success, response)
        except:
            pass  # Don't fail if history fails
        
        return success, response
    
    def _process_with_llm(self, text, language):
        """Process command using LLM"""
        try:
            # Get system prompt
            system_prompt = get_system_prompt()
            
            # Get conversation context
            context = self.conversation_manager.get_recent_context(5)
            
            # Parse command with LLM
            success, command_data, raw_response = self.llm_client.parse_command(text, system_prompt)
            
            if not success:
                # LLM error, try fallback
                return self._process_with_regex(text.lower(), language, text)
            
            # Extract intent and parameters
            intent = command_data.get('intent', 'chat')
            parameters = command_data.get('parameters', {})
            llm_response = command_data.get('response', '')
            
            # Execute command based on intent
            if intent == 'chat':
                # General chat - use LLM response directly
                self.conversation_manager.add_message("assistant", llm_response)
                return True, llm_response
            
            elif intent == 'open_app':
                app_name = parameters.get('app_name', '')
                if not app_name:
                    # Try to extract from text
                    app_name = self._extract_app_name(text)
                # Clean app_name - remove Turkish suffixes and normalize
                app_name = app_name.strip()
                # Remove common Turkish suffixes
                app_name = re.sub(r'(i|ı|u|ü|yi|yı|yu|yü|i|ı|u|ü)\s*$', '', app_name, flags=re.IGNORECASE).strip()
                result = system_control.open_application(app_name)
                response = llm_response if llm_response else result[1]
                self.conversation_manager.add_message("assistant", response)
                return result[0], response
            
            elif intent == 'close_app':
                app_name = parameters.get('app_name', '')
                result = system_control.close_application(app_name)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'volume_up':
                amount = parameters.get('amount', 10)
                result = system_control.increase_volume(amount)
                # Always return success if LLM understood the command
                if result[0]:
                    response = llm_response if llm_response else result[1]
                else:
                    # If system call failed, still acknowledge the command
                    response = llm_response if llm_response else f"Ses seviyesi artırıldı. ({result[1]})"
                return True, response
            
            elif intent == 'volume_down':
                amount = parameters.get('amount', 10)
                result = system_control.decrease_volume(amount)
                # Always return success if LLM understood the command
                if result[0]:
                    response = llm_response if llm_response else result[1]
                else:
                    response = llm_response if llm_response else f"Ses seviyesi azaltıldı. ({result[1]})"
                return True, response
            
            elif intent == 'set_volume':
                level = parameters.get('level', 50)
                result = system_control.set_volume(level)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'weather':
                city = parameters.get('city', None)
                result = weather.get_weather(city)
                # If weather API fails, still acknowledge the command
                if result[0]:
                    if llm_response:
                        response = f"{llm_response} {result[1]}"
                    else:
                        response = result[1]
                    return True, response
                else:
                    # API key missing or error
                    if "API anahtarı" in result[1]:
                        response = "Hava durumu özelliği için OpenWeatherMap API anahtarı gerekiyor. Lütfen config.json dosyasına API anahtarınızı ekleyin."
                    else:
                        response = llm_response if llm_response else result[1]
                    return False, response
            
            elif intent == 'calculate':
                expression = parameters.get('expression', text)
                result = calculator.simple_calculate(expression)
                if not result[0]:
                    result = calculator.calculate(expression)
                # Use LLM response if available, otherwise use calculator result
                response = llm_response if llm_response and result[0] else result[1]
                return result[0], response
            
            elif intent == 'save_note':
                note_text = parameters.get('note_text', '')
                # If note_text is empty, try to extract from text
                if not note_text:
                    # Remove common prefixes
                    note_text = text
                    for prefix in ['not kaydet', 'not al', 'not yaz', 'not ekle', 'save note']:
                        if prefix in text.lower():
                            note_text = text.lower().split(prefix, 1)[-1].strip()
                            break
                    # If still empty or too short, it's just "not" command
                    if len(note_text) < 3:
                        # This is a question, not a command to save
                        response = llm_response if llm_response else "Not kaydetmek için ne yazmak istersiniz? Örneğin: 'Not kaydet: Yarın toplantı var'"
                        return True, response
                
                result = notes.save_note(note_text)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'list_notes':
                result = notes.list_notes()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'web_search':
                query = parameters.get('query', text)
                result = web_search.search_google(query)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'open_website':
                url = parameters.get('url', text)
                result = web_search.open_website(url)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'system_info':
                result = system_control.get_system_info()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'time' or intent == 'date':
                from datetime import datetime
                if intent == 'time':
                    time_str = datetime.now().strftime("%H:%M")
                    response = llm_response if llm_response else f"Şu an saat {time_str}"
                else:
                    date_str = datetime.now().strftime("%d %B %Y")
                    response = llm_response if llm_response else f"Bugün {date_str}"
                self.conversation_manager.add_message("assistant", response)
                return True, response
            
            elif intent == 'create_reminder':
                message = parameters.get('message', '')
                duration = parameters.get('duration', '')
                if not message:
                    response = llm_response if llm_response else "Hatırlatıcı mesajı belirtilmedi"
                    return False, response
                result = reminders.create_reminder(message, duration)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'list_reminders':
                result = reminders.list_reminders()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'start_timer':
                duration = parameters.get('duration', text)
                result = reminders.start_timer(duration)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'screenshot':
                try:
                    # Check if user wants to save to Pictures folder
                    text_lower = text.lower()
                    save_to_pictures = any(word in text_lower for word in ['resimler', 'pictures', 'görseller'])
                    
                    result = media_control.take_screenshot(save_to_pictures=save_to_pictures)
                    
                    # If successful, also open the folder where it was saved
                    if result[0]:
                        # Extract folder path from result message or use default
                        try:
                            from pathlib import Path
                            if save_to_pictures:
                                folder_path = Path.home() / "Pictures"
                                if not folder_path.exists():
                                    folder_path = Path.home() / "Resimler"
                            else:
                                folder_path = Path.home() / "Desktop"
                                if not folder_path.exists():
                                    folder_path = Path.home() / "Masaüstü"
                            
                            if folder_path.exists():
                                # Optionally open the folder (commented out to avoid annoyance)
                                # file_operations.open_folder(str(folder_path))
                                pass
                        except:
                            pass
                    
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                except Exception as e:
                    print(f"Screenshot error: {e}")
                    import traceback
                    traceback.print_exc()
                    return False, f"Ekran görüntüsü alınırken hata oluştu: {str(e)}"
            
            elif intent == 'play_media' or intent == 'pause_media':
                result = media_control.play_media()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'next_track':
                result = media_control.next_track()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'previous_track':
                result = media_control.previous_track()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'system_status' or intent == 'system_monitor':
                result = system_monitor.get_system_status()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'memory_usage':
                result = system_monitor.get_memory_usage()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'cpu_usage':
                result = system_monitor.get_cpu_usage()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'disk_usage':
                result = system_monitor.get_disk_usage()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'battery_status':
                result = system_monitor.get_battery_status()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'mute_volume':
                result = system_control.mute_volume()
                # Always return success if LLM understood the command
                if result[0]:
                    response = llm_response if llm_response else result[1]
                else:
                    response = llm_response if llm_response else f"Ses kapatma komutu gönderildi. ({result[1]})"
                return True, response
            
            elif intent == 'unmute_volume':
                result = system_control.unmute_volume()
                # Always return success if LLM understood the command
                if result[0]:
                    response = llm_response if llm_response else result[1]
                else:
                    response = llm_response if llm_response else f"Ses açma komutu gönderildi. ({result[1]})"
                return True, response
            
            elif intent == 'get_volume':
                result = system_control.get_current_volume()
                if result[0]:
                    response = f"Ses seviyesi: %{result[1]}"
                else:
                    response = "Ses seviyesi okunamadı"
                return result[0], response
            
            elif intent == 'open_documents' or intent == 'open_downloads' or intent == 'open_folder':
                folder_name = parameters.get('folder_name', '')
                if not folder_name:
                    # Try to extract from text
                    text_lower = text.lower()
                    if 'belgeler' in text_lower or 'documents' in text_lower:
                        folder_name = 'documents'
                    elif 'indirilenler' in text_lower or 'downloads' in text_lower:
                        folder_name = 'downloads'
                    elif 'resimler' in text_lower or 'pictures' in text_lower or 'görseller' in text_lower:
                        folder_name = 'pictures'
                    elif 'videolar' in text_lower or 'videos' in text_lower:
                        folder_name = 'videos'
                    elif 'müzik' in text_lower or 'music' in text_lower:
                        folder_name = 'music'
                    elif 'masaüstü' in text_lower or 'desktop' in text_lower:
                        folder_name = 'desktop'
                    else:
                        # Use intent to determine
                        if intent == 'open_documents':
                            folder_name = 'documents'
                        elif intent == 'open_downloads':
                            folder_name = 'downloads'
                
                if folder_name:
                    result = file_operations.open_folder_by_name(folder_name)
                else:
                    if intent == 'open_documents':
                        result = file_operations.open_documents_folder()
                    elif intent == 'open_downloads':
                        result = file_operations.open_downloads_folder()
                    else:
                        result = (False, "Klasör adı belirtilmedi")
                
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'recent_files':
                result = file_operations.get_recent_files()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'search_file':
                filename = parameters.get('filename', text)
                result = file_operations.search_file_in_desktop(filename)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'lock_computer':
                result = security.lock_computer()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'sleep_display':
                result = security.sleep_display()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'send_email':
                to_email = parameters.get('to_email', '')
                subject = parameters.get('subject', '')
                body = parameters.get('body', '')
                if to_email and body:
                    result = email.send_email(to_email, subject, body)
                else:
                    # Try simplified format
                    recipient = parameters.get('recipient', '')
                    message = parameters.get('message', body or text)
                    result = email.send_email_simple(recipient, message)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'add_event' or intent == 'create_event':
                title = parameters.get('title', text)
                date_time = parameters.get('date_time', None)
                duration = parameters.get('duration', 60)
                result = calendar.add_event(title, date_time, duration)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'get_today_events' or intent == 'today_events':
                result = calendar.get_today_events()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'get_tomorrow_events' or intent == 'tomorrow_events':
                result = calendar.get_tomorrow_events()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'wikipedia_search':
                query = parameters.get('query', text)
                result = web_search.search_wikipedia(query)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'get_news' or intent == 'news':
                country = parameters.get('country', 'tr')
                category = parameters.get('category', 'general')
                result = web_search.get_news(country, category)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'youtube_search':
                query = parameters.get('query', text)
                result = web_search.search_youtube(query)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'command_stats' or intent == 'get_stats':
                result = command_history.get_command_stats()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'frequent_commands':
                limit = parameters.get('limit', 5)
                result = command_history.get_frequent_commands(limit)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'recent_commands' or intent == 'command_history':
                days = parameters.get('days', 1)
                limit = parameters.get('limit', 10)
                result = command_history.get_recent_commands(days, limit)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'tell_joke' or intent == 'joke':
                result = entertainment.tell_joke()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'flip_coin':
                result = entertainment.flip_coin()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'random_number':
                min_num = parameters.get('min', 1)
                max_num = parameters.get('max', 100)
                result = entertainment.random_number(min_num, max_num)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'tell_story':
                result = entertainment.tell_story()
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'copy_file':
                source = parameters.get('source', '')
                destination = parameters.get('destination', '')
                result = file_operations.copy_file(source, destination)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'move_file':
                source = parameters.get('source', '')
                destination = parameters.get('destination', '')
                result = file_operations.move_file(source, destination)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'rename_file':
                old_path = parameters.get('old_path', '')
                new_name = parameters.get('new_name', '')
                result = file_operations.rename_file(old_path, new_name)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'delete_event':
                event_title = parameters.get('event_title', text)
                result = calendar.delete_event(event_title)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'read_emails':
                max_results = parameters.get('max_results', 5)
                result = email.read_emails(max_results)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'search_emails':
                query = parameters.get('query', text)
                result = email.search_emails(query)
                response = llm_response if llm_response else result[1]
                return result[0], response
            
            elif intent == 'play_spotify' or intent == 'spotify_play':
                if spotify_control:
                    song_name = parameters.get('song_name', text)
                    result = spotify_control.play_song(song_name)
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi. Lütfen spotipy paketini yükleyin."
            
            elif intent == 'spotify_pause':
                if spotify_control:
                    result = spotify_control.pause_playback()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi."
            
            elif intent == 'spotify_resume':
                if spotify_control:
                    result = spotify_control.resume_playback()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi."
            
            elif intent == 'spotify_next':
                if spotify_control:
                    result = spotify_control.next_track()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi."
            
            elif intent == 'spotify_previous':
                if spotify_control:
                    result = spotify_control.previous_track()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi."
            
            elif intent == 'spotify_current' or intent == 'what_playing':
                if spotify_control:
                    result = spotify_control.get_current_track()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi."
            
            elif intent == 'spotify_playlists':
                if spotify_control:
                    result = spotify_control.get_playlists()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Spotify modülü yüklenemedi."
            
            elif intent == 'control_light':
                if smart_home:
                    light_name = parameters.get('light_name', '')
                    state = parameters.get('state', 'on')
                    brightness = parameters.get('brightness', None)
                    result = smart_home.control_light(light_name, state, brightness)
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Akıllı ev modülü yüklenemedi."
            
            elif intent == 'set_thermostat':
                if smart_home:
                    temperature = parameters.get('temperature', 22)
                    entity_name = parameters.get('entity_name', 'climate')
                    result = smart_home.set_thermostat(temperature, entity_name)
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Akıllı ev modülü yüklenemedi."
            
            elif intent == 'get_temperature':
                if smart_home:
                    entity_name = parameters.get('entity_name', 'climate')
                    result = smart_home.get_temperature(entity_name)
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Akıllı ev modülü yüklenemedi."
            
            elif intent == 'run_scenario' or intent == 'scenario':
                if scenarios:
                    scenario_name = parameters.get('scenario_name', text)
                    result = scenarios.run_scenario(scenario_name, self)
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Senaryo modülü yüklenemedi."
            
            elif intent == 'list_scenarios':
                if scenarios:
                    result = scenarios.list_scenarios()
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Senaryo modülü yüklenemedi."
            
            elif intent == 'create_scenario':
                if scenarios:
                    scenario_name = parameters.get('scenario_name', '')
                    tasks = parameters.get('tasks', [])
                    if not scenario_name or not tasks:
                        return False, "Senaryo adı ve görevler belirtilmedi"
                    result = scenarios.create_scenario(scenario_name, tasks)
                    response = llm_response if llm_response else result[1]
                    return result[0], response
                else:
                    return False, "Senaryo modülü yüklenemedi."
            
            elif intent == 'multi_step' or intent == 'multi_task':
                # Try multi-step processor
                success, message = self.multi_step_processor.process_multi_step(text)
                if success is not None:
                    return success, message
                # If not a multi-step command, fall through to else
            
            else:
                # Unknown intent, use LLM response as chat
                self.conversation_manager.add_message("assistant", llm_response)
                return True, llm_response
        
        except Exception as e:
            print(f"Error in LLM processing: {e}")
            # Fallback to regex
            return self._process_with_regex(text.lower(), language, text)
    
    def _process_with_regex(self, text, language, original_text):
        """Fallback: Process command using regex patterns"""
        patterns = self.turkish_patterns
        
        # Try to match patterns
        for command_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return self._execute_command(command_type, match, text, language)
        
        # If no pattern matches, try generic handlers
        return self._try_generic_handlers(text, language, original_text)
    
    def _extract_app_name(self, text):
        """Extract application name from text"""
        # Common app names mapping
        app_keywords = {
            'notepad': 'notepad',
            'not defteri': 'notepad',
            'hesap makinesi': 'calculator',
            'calculator': 'calculator',
            'kalkülatör': 'calculator',
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'microsoft edge': 'msedge',
            'edge': 'msedge',
            'firefox': 'firefox',
            'mozilla firefox': 'firefox',
            'whatsapp': 'whatsapp',
            'discord': 'discord',
            'spotify': 'spotify',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
            'paint': 'mspaint',
            'tarayıcı': 'browser',
            'browser': 'browser',
        }
        
        text_lower = text.lower()
        
        # Check for multi-word app names first (longer matches first)
        for keyword, app_name in sorted(app_keywords.items(), key=lambda x: len(x[0]), reverse=True):
            if keyword in text_lower:
                return app_name
        
        # Try to extract after "aç" or "open" - get full phrase
        match = re.search(r'(?:aç|open)\s+([^\s]+(?:\s+[^\s]+)*)', text_lower)
        if match:
            extracted = match.group(1).strip()
            # Remove Turkish suffixes
            extracted = re.sub(r'(i|ı|u|ü|yi|yı|yu|yü|i|ı|u|ü)$', '', extracted).strip()
            # Check if it's a known app
            if extracted in app_keywords:
                return app_keywords[extracted]
            # Return as-is for unknown apps (let open_application handle it)
            return extracted
        
        return text
    
    def _execute_command(self, command_type, match, full_text, language):
        """Execute a matched command (regex fallback)"""
        try:
            if command_type == 'open_app':
                app_name = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                app_name = app_name.strip()
                app_map = {
                    'notepad': 'notepad',
                    'hesap makinesi': 'calculator',
                    'calculator': 'calculator',
                    'kalkülatör': 'calculator',
                    'chrome': 'browser',
                    'tarayıcı': 'browser',
                    'browser': 'browser',
                }
                app_name = app_map.get(app_name, app_name)
                return system_control.open_application(app_name)
            
            elif command_type == 'volume_up':
                return system_control.increase_volume(10)
            
            elif command_type == 'volume_down':
                return system_control.decrease_volume(10)
            
            elif command_type == 'weather':
                city_match = re.search(r'(?:in|için|for)\s+([a-zA-ZğüşıöçĞÜŞİÖÇ\s]+)', full_text)
                city = city_match.group(1).strip() if city_match else None
                return weather.get_weather(city)
            
            elif command_type == 'calculate':
                expr = match.group(1) if len(match.groups()) >= 1 else full_text
                result = calculator.simple_calculate(expr)
                if not result[0]:
                    result = calculator.calculate(expr)
                return result
            
            elif command_type == 'save_note':
                note_text = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                return notes.save_note(note_text.strip())
            
            elif command_type == 'list_notes':
                return notes.list_notes()
            
            elif command_type == 'search':
                query = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                return web_search.search_google(query.strip())
        
        except Exception as e:
            return False, f"Hata: {str(e)}"
        
        return False, "Komut anlaşılamadı"
    
    def _try_generic_handlers(self, text, language, original_text):
        """Try generic command handlers when patterns don't match"""
        # Check for numbers (might be a calculation)
        if re.search(r'\d+', text):
            result = calculator.simple_calculate(text)
            if result[0]:
                return result
        
        # Check for "open" or "aç" at the start
        if re.match(r'^(aç|open)\s+', text):
            app_name = re.sub(r'^(aç|open)\s+', '', text).strip()
            return system_control.open_application(app_name)
        
        # Check for search keywords
        if any(word in text for word in ['ara', 'search', 'google']):
            query = re.sub(r'.*(ara|search|google)\s*:?\s*', '', text).strip()
            if query:
                return web_search.search_google(query)
        
        # If LLM was available but didn't return a command, try simple chat
        if self.use_llm and self.llm_client.is_available():
            try:
                success, response = self.llm_client.get_simple_response(
                    original_text,
                    self.conversation_manager.get_recent_context(3)
                )
                if success:
                    self.conversation_manager.add_message("assistant", response)
                    return True, response
            except:
                pass
        
        return False, "Komut anlaşılamadı. Lütfen tekrar deneyin."
