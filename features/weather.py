"""
Weather features using OpenWeatherMap API
"""
import requests
from utils.config import config


def get_weather(city=None):
    """Get weather information for a city"""
    try:
        api_key = config.get('weather.api_key', '')
        if not api_key:
            return False, "Hava durumu API anahtarı ayarlanmamış. Lütfen config.json dosyasına API anahtarınızı ekleyin."
        
        if city is None:
            city = config.get('weather.city', 'Istanbul')
        
        units = config.get('weather.units', 'metric')
        lang = 'tr' if config.get('language', 'tr') == 'tr' else 'en'
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': units,
            'lang': lang
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            if lang == 'tr':
                result = f"{city} için hava durumu: {description}, sıcaklık {temp} derece, nem %{humidity}, rüzgar hızı {wind_speed} metre/saniye"
            else:
                result = f"Weather for {city}: {description}, temperature {temp} degrees, humidity {humidity}%, wind speed {wind_speed} m/s"
            
            return True, result
        else:
            return False, f"Hava durumu bilgisi alınamadı. Hata kodu: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Bağlantı hatası: {str(e)}"
    except Exception as e:
        return False, f"Hata: {str(e)}"

