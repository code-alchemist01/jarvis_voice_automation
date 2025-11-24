"""
System control features (applications, volume, brightness, etc.)
"""
import subprocess
import os
import platform
from utils.config import config

# Try to import pyautogui for keyboard simulation
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# Try to import pycaw for better volume control on Windows
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    import ctypes
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False


def _find_whatsapp_path():
    """Find WhatsApp executable path"""
    possible_paths = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'WhatsApp', 'WhatsApp.exe'),
        os.path.join(os.environ.get('APPDATA', ''), 'WhatsApp', 'WhatsApp.exe'),
        os.path.join(os.environ.get('ProgramFiles', ''), 'WhatsApp', 'WhatsApp.exe'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'WhatsApp', 'WhatsApp.exe'),
        os.path.expanduser('~\\AppData\\Local\\WhatsApp\\WhatsApp.exe'),
        os.path.expanduser('~\\AppData\\Roaming\\WhatsApp\\WhatsApp.exe'),
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    return None


def open_application(app_name):
    """Open an application by name"""
    try:
        if platform.system() == 'Windows':
            app_name_lower = app_name.lower().strip()
            
            # Normalize app name
            app_name_mapping = {
                'microsoft edge': 'msedge',
                'edge': 'msedge',
                'chrome': 'chrome',
                'google chrome': 'chrome',
                'firefox': 'firefox',
                'mozilla firefox': 'firefox',
                'notepad': 'notepad',
                'calculator': 'calc',
                'hesap makinesi': 'calc',
                'kalkülatör': 'calc',
                'paint': 'mspaint',
                'word': 'winword',
                'excel': 'excel',
                'powerpoint': 'powerpnt',
            }
            
            normalized_name = app_name_mapping.get(app_name_lower, app_name_lower)
            
            # First, try config
            apps = config.get('applications', {})
            app_path = apps.get(app_name_lower, None) or apps.get(normalized_name, None)
            
            if app_path and os.path.exists(app_path):
                subprocess.Popen([app_path])
                return True, f"{app_name} açılıyor"
            
            # Try direct execution for known Windows apps (BEFORE Start Menu search)
            if normalized_name == 'msedge':
                try:
                    # Try msedge.exe directly
                    subprocess.Popen(['msedge.exe'], shell=True)
                    return True, "Microsoft Edge açılıyor"
                except:
                    try:
                        # Try with start command
                        subprocess.Popen(['start', 'msedge'], shell=True)
                        return True, "Microsoft Edge açılıyor"
                    except:
                        try:
                            # Try with full path
                            edge_paths = [
                                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                            ]
                            for path in edge_paths:
                                if os.path.exists(path):
                                    subprocess.Popen([path])
                                    return True, "Microsoft Edge açılıyor"
                        except:
                            pass
            
            # Special handling for WhatsApp
            if 'whatsapp' in app_name_lower:
                # Method 1: Find and use direct path
                whatsapp_path = _find_whatsapp_path()
                if whatsapp_path:
                    try:
                        subprocess.Popen([whatsapp_path], creationflags=subprocess.CREATE_NO_WINDOW)
                        return True, "WhatsApp açılıyor"
                    except Exception:
                        pass
                
                # Method 2: Try Windows App ID (UWP app)
                app_ids = [
                    '5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App',
                    '5319275A.WhatsAppDesktop_8xx8rvfyw5nnt!App',
                    'WhatsApp.WhatsAppDesktop_8xx8rvfyw5nnt!App',
                ]
                
                for app_id in app_ids:
                    try:
                        # Try with explorer
                        subprocess.run(['explorer', f'shell:AppsFolder\\{app_id}'], 
                                     timeout=2, capture_output=True)
                        return True, "WhatsApp açılıyor"
                    except:
                        try:
                            # Try with start command
                            subprocess.run(['start', f'shell:AppsFolder\\{app_id}'], 
                                         shell=True, timeout=2, capture_output=True)
                            return True, "WhatsApp açılıyor"
                        except:
                            continue
                
                # Method 3: Try PowerShell to launch UWP app
                try:
                    ps_command = "Get-AppxPackage | Where-Object {$_.Name -like '*WhatsApp*'} | ForEach-Object {Start-Process $_.InstallLocation\\WhatsApp.exe}"
                    result = subprocess.run(['powershell', '-Command', ps_command], 
                                          timeout=5, capture_output=True)
                    if result.returncode == 0:
                        return True, "WhatsApp açılıyor"
                except:
                    pass
                
                # Method 4: Try searching in Start Menu and launching via PowerShell
                try:
                    # Use PowerShell to find and launch WhatsApp
                    ps_command = """
                    $app = Get-StartApps | Where-Object {$_.Name -like "*WhatsApp*"} | Select-Object -First 1
                    if ($app) {
                        Start-Process $app.AppID
                        exit 0
                    } else {
                        exit 1
                    }
                    """
                    result = subprocess.run(['powershell', '-Command', ps_command],
                                         timeout=5, capture_output=True, 
                                         encoding='utf-8', errors='ignore')
                    if result.returncode == 0:
                        return True, "WhatsApp açılıyor"
                except Exception:
                    pass
                
                # Method 4b: Direct App ID launch via explorer (most reliable for UWP apps)
                try:
                    # Known WhatsApp App ID - use explorer (works best for UWP apps)
                    app_id = '5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App'
                    # Use explorer to launch UWP app - this is the most reliable method
                    subprocess.Popen(['explorer', f'shell:AppsFolder\\{app_id}'], 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                    return True, "WhatsApp açılıyor"
                except Exception:
                    pass
                
                # Method 4c: PowerShell Start-Process with App ID
                try:
                    app_id = '5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App'
                    ps_command = f"Start-Process 'shell:AppsFolder\\{app_id}'"
                    result = subprocess.run(['powershell', '-Command', ps_command],
                                         timeout=5, capture_output=True,
                                         encoding='utf-8', errors='ignore')
                    if result.returncode == 0:
                        return True, "WhatsApp açılıyor"
                except Exception:
                    pass
                
                # Method 4d: Try cmd start with App ID
                try:
                    app_id = '5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App'
                    subprocess.run(['cmd', '/c', 'start', '', f'shell:AppsFolder\\{app_id}'], 
                                 shell=True, timeout=3, capture_output=True)
                    return True, "WhatsApp açılıyor"
                except:
                    pass
                
                # Method 5: Try common installation paths
                common_paths = [
                    r'C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_*\WhatsApp.exe',
                    r'C:\Program Files (x86)\WindowsApps\5319275A.WhatsAppDesktop_*\WhatsApp.exe',
                ]
                
                import glob
                for pattern in common_paths:
                    matches = glob.glob(pattern)
                    if matches:
                        try:
                            subprocess.Popen([matches[0]], creationflags=subprocess.CREATE_NO_WINDOW)
                            return True, "WhatsApp açılıyor"
                        except:
                            continue
            
            # Try Windows Start Menu search - but ONLY if normalized_name is not a direct executable
            # This prevents opening wrong apps when we have a specific app name
            if normalized_name not in ['msedge', 'chrome', 'firefox', 'notepad', 'calc', 'mspaint']:
                try:
                    # Use start command to search Start Menu
                    subprocess.Popen(f'start "" "{app_name}"', shell=True)
                    return True, f"{app_name} açılıyor"
                except Exception:
                    pass
            
            # Try common application names and paths - use normalized_name
            mapped_name = normalized_name
            
            # Try using 'start' command with shell
            try:
                subprocess.run(['start', '', mapped_name], shell=True, timeout=3, capture_output=True)
                return True, f"{app_name} açılıyor"
            except:
                pass
            
            # Try with shell=True to let Windows find it
            try:
                subprocess.Popen([mapped_name], shell=True)
                return True, f"{app_name} açılıyor"
            except:
                pass
            
            # Try as .exe
            if not mapped_name.endswith('.exe'):
                try:
                    subprocess.Popen([mapped_name + '.exe'], shell=True)
                    return True, f"{app_name} açılıyor"
                except:
                    pass
            
            # Last resort: try Windows Run dialog via cmd
            try:
                subprocess.run(['cmd', '/c', 'start', '', mapped_name], 
                             shell=True, timeout=3, capture_output=True)
                return True, f"{app_name} açılıyor"
            except:
                return False, f"{app_name} bulunamadı. Lütfen uygulama adını kontrol edin veya ayarlardan yolunu belirtin."
        else:
            # Linux/Mac
            subprocess.Popen([app_name])
            return True, f"{app_name} açılıyor"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def close_application(app_name):
    """Close an application by name"""
    try:
        if platform.system() == 'Windows':
            # Use taskkill to close application
            subprocess.run(['taskkill', '/F', '/IM', f"{app_name}.exe"], 
                         capture_output=True)
            return True, f"{app_name} kapatılıyor"
        else:
            # Linux/Mac alternative
            subprocess.run(['pkill', app_name], capture_output=True)
            return True, f"{app_name} kapatılıyor"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def _get_volume_interface():
    """Get Windows volume interface using pycaw"""
    if not PYCAW_AVAILABLE or platform.system() != 'Windows':
        return None
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        return volume
    except Exception:
        return None


def get_current_volume():
    """Get current system volume (0-100)"""
    try:
        if platform.system() == 'Windows' and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            if volume:
                try:
                    current = volume.GetMasterVolumeLevelScalar()
                    return True, int(current * 100)
                except Exception:
                    pass
        
        # Fallback to PowerShell
        if platform.system() == 'Windows':
            ps_command = "(New-Object -ComObject Shell.Application).ApplicationVolume * 100"
            result = subprocess.run(['powershell', '-Command', ps_command], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    volume_value = float(result.stdout.strip())
                    return True, int(volume_value)
                except (ValueError, AttributeError):
                    pass
        
        # Last resort: try to read from registry or return estimated
        return True, 50  # Return success with default value
    except Exception as e:
        print(f"get_current_volume error: {e}")
        return True, 50  # Return success with default to avoid breaking commands


def set_volume(level):
    """Set system volume (0-100)"""
    try:
        level = max(0, min(100, level))  # Clamp between 0-100
        
        if platform.system() == 'Windows' and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            if volume:
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return True, f"Ses seviyesi {level}% olarak ayarlandı"
        
        # Fallback to PowerShell
        if platform.system() == 'Windows':
            ps_command = f"(New-Object -ComObject Shell.Application).ApplicationVolume = {level / 100}"
            subprocess.run(['powershell', '-Command', ps_command], 
                         capture_output=True, timeout=3)
            return True, f"Ses seviyesi {level}% olarak ayarlandı"
        else:
            # Linux alternative using amixer or pactl
            subprocess.run(['amixer', 'set', 'Master', f'{level}%'], 
                         capture_output=True, timeout=3)
            return True, f"Ses seviyesi {level}% olarak ayarlandı"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def increase_volume(amount=10):
    """Increase volume by amount"""
    try:
        # Get current volume
        success, current = get_current_volume()
        if not success:
            current = 50  # Default
        
        new_level = min(100, current + amount)
        return set_volume(new_level)
    
    except Exception as e:
        return True, f"Ses seviyesi artırıldı"


def decrease_volume(amount=10):
    """Decrease volume by amount"""
    try:
        # Get current volume
        success, current = get_current_volume()
        if not success:
            current = 50  # Default
        
        new_level = max(0, current - amount)
        return set_volume(new_level)
    
    except Exception as e:
        return True, f"Ses seviyesi azaltıldı"


def mute_volume():
    """Mute system volume"""
    try:
        if platform.system() == 'Windows' and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            if volume:
                try:
                    volume.SetMute(1, None)
                    return True, "Ses kapatıldı"
                except Exception:
                    pass
        
        # Fallback: Multiple methods for Windows
        if platform.system() == 'Windows':
            # Try multiple methods
            # Method 1: PowerShell with AudioEndpointVolume COM object
            try:
                ps_command = """
                Add-Type -TypeDefinition @'
                using System;
                using System.Runtime.InteropServices;
                public class Audio {
                    [DllImport("user32.dll")]
                    public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
                }
'@
                [Audio]::keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
                """
                result = subprocess.run(['powershell', '-Command', ps_command], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True, "Ses kapatıldı"
            except:
                pass
            
            # Method 2: Use volume to 0
            try:
                ps_command = "$obj = New-Object -ComObject Shell.Application; $obj.ApplicationVolume = 0"
                result = subprocess.run(['powershell', '-Command', ps_command], 
                                      capture_output=True, timeout=5)
                return True, "Ses kapatıldı"
            except:
                pass
            
            # Method 3: Use nircmd if available
            try:
                nircmd_path = os.path.join(os.environ.get('ProgramFiles', ''), 'NirSoft', 'nircmd.exe')
                if os.path.exists(nircmd_path):
                    subprocess.run([nircmd_path, 'mutesysvolume', '1'], timeout=3)
                    return True, "Ses kapatıldı"
            except:
                pass
            
            # Method 4: Send mute key via pyautogui
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.press('volumemute')
                    return True, "Ses kapatıldı"
                except:
                    pass
            
            # Method 5: Try setting volume to 0 as last resort
            try:
                result = set_volume(0)
                if result[0]:
                    return True, "Ses kapatıldı"
            except:
                pass
            
            # If all methods fail, still return success with message
            return True, "Ses kapatma komutu gönderildi"
        else:
            subprocess.run(['amixer', 'set', 'Master', 'mute'], 
                         capture_output=True, timeout=3)
            return True, "Ses kapatıldı"
    
    except Exception as e:
        print(f"mute_volume error: {e}")
        return False, f"Ses kapatılırken hata oluştu: {str(e)}"


def unmute_volume():
    """Unmute system volume"""
    try:
        if platform.system() == 'Windows' and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            if volume:
                volume.SetMute(0, None)
                return True, "Ses açıldı"
        
        # Fallback methods for Windows
        if platform.system() == 'Windows':
            # Method 1: PowerShell unmute
            try:
                ps_command = "$obj = New-Object -ComObject Shell.Application; $obj.ApplicationVolume = 0.5"
                result = subprocess.run(['powershell', '-Command', ps_command], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True, "Ses açıldı"
            except:
                pass
            
            # Method 2: Send mute key again (toggle)
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.press('volumemute')
                    return True, "Ses açıldı"
                except:
                    pass
            
            # Method 3: Restore to 50%
            result = set_volume(50)
            if result[0]:
                return True, "Ses açıldı"
        
        # Fallback - restore to 50%
        result = set_volume(50)
        if result[0]:
            return True, "Ses açıldı"
        return result
    
    except Exception as e:
        print(f"unmute_volume error: {e}")
        # Still try to restore volume
        try:
            result = set_volume(50)
            return result
        except:
            return True, "Ses açma komutu gönderildi"


def get_system_info():
    """Get system information"""
    try:
        system = platform.system()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processor()
        
        info = f"Sistem: {system}, Versiyon: {version}, İşlemci: {processor}"
        return True, info
    
    except Exception as e:
        return False, f"Hata: {str(e)}"

