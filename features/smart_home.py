"""
Smart home integration features (Home Assistant)
"""
import requests
from utils.config import config


def _get_home_assistant_config():
    """Get Home Assistant configuration"""
    url = config.get('smart_home.home_assistant_url', '')
    token = config.get('smart_home.home_assistant_token', '')
    
    if not url or not token:
        return None, None, "Home Assistant URL ve Token ayarlanmamış. Lütfen ayarlardan yapılandırın."
    
    return url, token, None


def _call_home_assistant_api(endpoint, method='GET', data=None):
    """Call Home Assistant API"""
    url, token, error = _get_home_assistant_config()
    if error:
        return None, error
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        full_url = f"{url.rstrip('/')}/api/{endpoint}"
        
        if method == 'GET':
            response = requests.get(full_url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(full_url, headers=headers, json=data, timeout=5)
        else:
            return None, f"Desteklenmeyen HTTP metodu: {method}"
        
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Home Assistant API hatası: {str(e)}"


def control_light(light_name, state='on', brightness=None, color=None):
    """Control a light"""
    try:
        # Get entity ID from mapping
        device_mapping = config.get('smart_home.device_mapping', {})
        entity_id = device_mapping.get(light_name.lower(), light_name)
        
        # If entity_id doesn't start with domain, assume it's a light
        if '.' not in entity_id:
            entity_id = f"light.{entity_id}"
        
        service_data = {
            'entity_id': entity_id
        }
        
        if state == 'on':
            if brightness:
                service_data['brightness'] = int(brightness * 255 / 100)
            if color:
                service_data['rgb_color'] = color
            service = 'turn_on'
        else:
            service = 'turn_off'
        
        result, error = _call_home_assistant_api(
            f'services/light/{service}',
            method='POST',
            data=service_data
        )
        
        if error:
            return False, error
        
        return True, f"Işık {state} yapıldı: {light_name}"
    except Exception as e:
        print(f"Error controlling light: {e}")
        return False, f"Işık kontrol edilirken hata oluştu: {str(e)}"


def set_thermostat(temperature, entity_name='climate'):
    """Set thermostat temperature"""
    try:
        device_mapping = config.get('smart_home.device_mapping', {})
        entity_id = device_mapping.get(entity_name.lower(), entity_name)
        
        if '.' not in entity_id:
            entity_id = f"climate.{entity_id}"
        
        service_data = {
            'entity_id': entity_id,
            'temperature': float(temperature)
        }
        
        result, error = _call_home_assistant_api(
            'services/climate/set_temperature',
            method='POST',
            data=service_data
        )
        
        if error:
            return False, error
        
        return True, f"Termostat {temperature} dereceye ayarlandı"
    except Exception as e:
        print(f"Error setting thermostat: {e}")
        return False, f"Termostat ayarlanırken hata oluştu: {str(e)}"


def get_temperature(entity_name='climate'):
    """Get current temperature"""
    try:
        device_mapping = config.get('smart_home.device_mapping', {})
        entity_id = device_mapping.get(entity_name.lower(), entity_name)
        
        if '.' not in entity_id:
            entity_id = f"climate.{entity_id}"
        
        result, error = _call_home_assistant_api(f'states/{entity_id}')
        
        if error:
            return False, error
        
        if result:
            temp = result.get('state', 'Bilinmiyor')
            return True, f"Oda sıcaklığı: {temp}°C"
        
        return False, "Sıcaklık bilgisi alınamadı"
    except Exception as e:
        print(f"Error getting temperature: {e}")
        return False, f"Sıcaklık bilgisi alınırken hata oluştu: {str(e)}"


def run_scenario(scenario_name):
    """Run a Home Assistant scenario/script"""
    try:
        device_mapping = config.get('smart_home.device_mapping', {})
        entity_id = device_mapping.get(scenario_name.lower(), scenario_name)
        
        if '.' not in entity_id:
            entity_id = f"script.{entity_id}"
        
        service_data = {
            'entity_id': entity_id
        }
        
        result, error = _call_home_assistant_api(
            'services/script/turn_on',
            method='POST',
            data=service_data
        )
        
        if error:
            return False, error
        
        return True, f"Senaryo çalıştırıldı: {scenario_name}"
    except Exception as e:
        print(f"Error running scenario: {e}")
        return False, f"Senaryo çalıştırılırken hata oluştu: {str(e)}"


def get_device_state(device_name):
    """Get device state"""
    try:
        device_mapping = config.get('smart_home.device_mapping', {})
        entity_id = device_mapping.get(device_name.lower(), device_name)
        
        result, error = _call_home_assistant_api(f'states/{entity_id}')
        
        if error:
            return False, error
        
        if result:
            state = result.get('state', 'Bilinmiyor')
            return True, f"{device_name} durumu: {state}"
        
        return False, "Cihaz durumu alınamadı"
    except Exception as e:
        print(f"Error getting device state: {e}")
        return False, f"Cihaz durumu alınırken hata oluştu: {str(e)}"

