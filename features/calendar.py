"""
Calendar integration features with Google Calendar API
"""
import subprocess
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.config import config
from utils.oauth2_helper import get_calendar_service

# Fallback to web if API not available
WEB_FALLBACK = True


def _parse_datetime(date_time_str):
    """Parse date/time string to datetime object"""
    try:
        if not date_time_str:
            return None
        
        # Try common formats
        now = datetime.now()
        
        # Relative times
        if 'yarın' in date_time_str.lower() or 'tomorrow' in date_time_str.lower():
            base_date = now + timedelta(days=1)
        elif 'bugün' in date_time_str.lower() or 'today' in date_time_str.lower():
            base_date = now
        else:
            base_date = now
        
        # Extract time
        import re
        time_match = re.search(r'(\d{1,2}):(\d{2})', date_time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Try to parse directly
        try:
            return date_parser.parse(date_time_str)
        except:
            return base_date
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return None


def add_event(title, date_time=None, duration_minutes=60):
    """Add event to calendar using Google Calendar API or fallback"""
    try:
        # Try Google Calendar API first
        service, error = get_calendar_service()
        
        if service and not error:
            try:
                # Parse date_time if it's a string
                if isinstance(date_time, str):
                    event_datetime = _parse_datetime(date_time)
                else:
                    event_datetime = date_time if date_time else datetime.now() + timedelta(hours=1)
                
                if not event_datetime:
                    event_datetime = datetime.now() + timedelta(hours=1)
                
                # Create event
                event = {
                    'summary': title,
                    'start': {
                        'dateTime': event_datetime.isoformat(),
                        'timeZone': 'Europe/Istanbul',
                    },
                    'end': {
                        'dateTime': (event_datetime + timedelta(minutes=duration_minutes)).isoformat(),
                        'timeZone': 'Europe/Istanbul',
                    },
                }
                
                # Insert event
                event = service.events().insert(calendarId='primary', body=event).execute()
                
                return True, f"Etkinlik takvime eklendi: {title} ({event_datetime.strftime('%d.%m.%Y %H:%M')})"
            except Exception as e:
                print(f"Google Calendar API error: {e}")
                # Fall through to web fallback
        
        # Fallback to web interface
        if WEB_FALLBACK:
            calendar_type = config.get('calendar.type', 'google')
            
            if calendar_type == 'windows':
                try:
                    subprocess.Popen(['start', 'ms-calendar:'], shell=True)
                    return True, f"Windows Takvim açıldı. Lütfen '{title}' etkinliğini ekleyin."
                except:
                    calendar_type = 'google'
            
            if calendar_type == 'google':
                title_encoded = urllib.parse.quote(title)
                url = f'https://calendar.google.com/calendar/r/eventedit?text={title_encoded}'
                webbrowser.open(url)
                return True, f"Google Takvim açıldı. '{title}' etkinliği için form dolduruluyor."
            elif calendar_type == 'outlook':
                title_encoded = urllib.parse.quote(title)
                url = f'https://outlook.live.com/calendar/0/deeplink/compose?subject={title_encoded}'
                webbrowser.open(url)
                return True, f"Outlook Takvim açıldı. '{title}' etkinliği için form dolduruluyor."
        
        return False, "Takvim servisine erişilemedi."
    except Exception as e:
        print(f"Error adding event: {e}")
        return False, f"Etkinlik eklenirken hata oluştu: {str(e)}"


def get_today_events():
    """Get today's events from Google Calendar API or fallback"""
    try:
        service, error = get_calendar_service()
        
        if service and not error:
            try:
                # Get today's events
                now = datetime.now()
                time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
                time_max = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
                
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                if not events:
                    return True, "Bugün etkinlik bulunamadı."
                
                result = "Bugünkü etkinlikleriniz:\n"
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    try:
                        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_str = start_time.strftime('%H:%M')
                    except:
                        time_str = "Tüm gün"
                    
                    result += f"- {time_str}: {event.get('summary', 'Etkinlik adı yok')}\n"
                
                return True, result
            except Exception as e:
                print(f"Google Calendar API error: {e}")
                # Fall through to web fallback
        
        # Fallback to web
        if WEB_FALLBACK:
            calendar_type = config.get('calendar.type', 'google')
            if calendar_type == 'google':
                webbrowser.open('https://calendar.google.com/calendar/r/day')
                return True, "Bugünkü etkinlikler görüntüleniyor. Google Takvim açıldı."
            elif calendar_type == 'outlook':
                webbrowser.open('https://outlook.live.com/calendar/0/view/day')
                return True, "Bugünkü etkinlikler görüntüleniyor. Outlook Takvim açıldı."
        
        return False, "Takvim servisine erişilemedi."
    except Exception as e:
        print(f"Error getting events: {e}")
        return False, f"Etkinlikler alınırken hata oluştu: {str(e)}"


def get_tomorrow_events():
    """Get tomorrow's events from Google Calendar API or fallback"""
    try:
        service, error = get_calendar_service()
        
        if service and not error:
            try:
                tomorrow = datetime.now() + timedelta(days=1)
                time_min = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
                time_max = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
                
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                if not events:
                    return True, "Yarın etkinlik bulunamadı."
                
                result = "Yarınki etkinlikleriniz:\n"
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    try:
                        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_str = start_time.strftime('%H:%M')
                    except:
                        time_str = "Tüm gün"
                    
                    result += f"- {time_str}: {event.get('summary', 'Etkinlik adı yok')}\n"
                
                return True, result
            except Exception as e:
                print(f"Google Calendar API error: {e}")
                # Fall through to web fallback
        
        # Fallback to web
        if WEB_FALLBACK:
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime('%Y-%m-%d')
            calendar_type = config.get('calendar.type', 'google')
            if calendar_type == 'google':
                webbrowser.open(f'https://calendar.google.com/calendar/r/day/{date_str}')
                return True, "Yarınki etkinlikler görüntüleniyor. Google Takvim açıldı."
            elif calendar_type == 'outlook':
                webbrowser.open(f'https://outlook.live.com/calendar/0/view/day/{date_str}')
                return True, "Yarınki etkinlikler görüntüleniyor. Outlook Takvim açıldı."
        
        return False, "Takvim servisine erişilemedi."
    except Exception as e:
        print(f"Error getting tomorrow events: {e}")
        return False, f"Yarınki etkinlikler alınırken hata oluştu: {str(e)}"


def delete_event(event_title):
    """Delete an event by title"""
    try:
        service, error = get_calendar_service()
        
        if service and not error:
            try:
                # Search for event
                now = datetime.now()
                time_min = (now - timedelta(days=30)).isoformat() + 'Z'
                time_max = (now + timedelta(days=365)).isoformat() + 'Z'
                
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=50,
                    singleEvents=True,
                    orderBy='startTime',
                    q=event_title
                ).execute()
                
                events = events_result.get('items', [])
                
                if not events:
                    return False, f"'{event_title}' adında etkinlik bulunamadı."
                
                # Delete first matching event
                event_id = events[0]['id']
                service.events().delete(calendarId='primary', eventId=event_id).execute()
                
                return True, f"Etkinlik silindi: {event_title}"
            except Exception as e:
                print(f"Google Calendar API error: {e}")
                return False, f"Etkinlik silinirken hata oluştu: {str(e)}"
        
        return False, "Takvim servisine erişilemedi."
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False, f"Etkinlik silinirken hata oluştu: {str(e)}"
