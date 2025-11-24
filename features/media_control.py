"""
Media control and screenshot features
"""
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Try to import PIL for screenshots
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def take_screenshot(save_path=None, save_to_pictures=False):
    """Take a screenshot - safe version that won't crash the program
    
    Args:
        save_path: Custom path to save screenshot (optional)
        save_to_pictures: If True, save to Pictures folder instead of Desktop
    """
    try:
        if save_path is None:
            # Choose save location
            if save_to_pictures:
                # Save to Pictures folder
                pictures = Path.home() / "Pictures"
                if not pictures.exists():
                    pictures = Path.home() / "Resimler"
                if not pictures.exists():
                    pictures = Path.home()
                save_dir = pictures
            else:
                # Default to Desktop
                desktop = Path.home() / "Desktop"
                if not desktop.exists():
                    # Try alternative desktop path
                    desktop = Path.home() / "Masaüstü"
                if not desktop.exists():
                    desktop = Path.home()
                save_dir = desktop
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = save_dir / f"ekran_goruntusu_{timestamp}.png"
        else:
            save_path = Path(save_path)
        
        # Ensure parent directory exists
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Could not create directory: {e}")
            return False, f"Klasör oluşturulamadı: {str(e)}"
        
        # Try pyautogui first (most reliable and safe)
        try:
            import pyautogui
            # Disable failsafe to prevent crashes
            original_failsafe = pyautogui.FAILSAFE
            pyautogui.FAILSAFE = False
            
            try:
                screenshot = pyautogui.screenshot()
                if screenshot:
                    # Save and verify file was created
                    screenshot.save(str(save_path))
                    # Verify file exists and has content
                    if save_path.exists() and save_path.stat().st_size > 0:
                        pyautogui.FAILSAFE = original_failsafe  # Restore
                        folder_name = save_path.parent.name
                        return True, f"Ekran görüntüsü {folder_name} klasörüne kaydedildi: {save_path.name}"
                    else:
                        print(f"File was not created or is empty: {save_path}")
                        # Try again with explicit format
                        screenshot.save(str(save_path), 'PNG')
                        if save_path.exists() and save_path.stat().st_size > 0:
                            pyautogui.FAILSAFE = original_failsafe
                            folder_name = save_path.parent.name
                            return True, f"Ekran görüntüsü {folder_name} klasörüne kaydedildi: {save_path.name}"
            finally:
                pyautogui.FAILSAFE = original_failsafe  # Always restore
        except ImportError:
            pass  # pyautogui not available, try next method
        except Exception as e:
            print(f"pyautogui screenshot failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Try PIL if available
        if PIL_AVAILABLE:
            try:
                # Use all_screens=False to avoid multi-monitor issues
                screenshot = ImageGrab.grab(all_screens=False)
                if screenshot:
                    screenshot.save(str(save_path), 'PNG')
                    # Verify file was created
                    if save_path.exists() and save_path.stat().st_size > 0:
                        folder_name = save_path.parent.name
                        return True, f"Ekran görüntüsü {folder_name} klasörüne kaydedildi: {save_path.name}"
                    else:
                        print(f"PIL: File was not created or is empty: {save_path}")
            except Exception as e:
                print(f"PIL screenshot failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to other methods
        result = _take_screenshot_fallback(save_path)
        
        # Final verification - check if file exists
        if result[0] and save_path.exists() and save_path.stat().st_size > 0:
            return result
        elif result[0]:
            # Said success but file doesn't exist
            print(f"Warning: Screenshot reported success but file not found: {save_path}")
            return False, f"Ekran görüntüsü kaydedilemedi. Dosya yolu: {save_path}"
        else:
            return result
    
    except Exception as e:
        import traceback
        print(f"Screenshot error: {e}")
        print(traceback.format_exc())
        return False, f"Ekran görüntüsü alınamadı: Lütfen PrintScreen tuşunu kullanın."


def _take_screenshot_fallback(save_path):
    """Fallback screenshot method - safe and simple"""
    try:
        if platform.system() == 'Windows':
            # Try using mss library if available (very reliable)
            try:
                import mss
                with mss.mss() as sct:
                    if len(sct.monitors) > 1:
                        screenshot = sct.grab(sct.monitors[1])  # Primary monitor
                        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(save_path))
                        # Verify file was created
                        if save_path.exists() and save_path.stat().st_size > 0:
                            folder_name = save_path.parent.name
                            return True, f"Ekran görüntüsü {folder_name} klasörüne kaydedildi: {save_path.name}"
            except (ImportError, Exception) as e:
                print(f"mss screenshot failed: {e}")
            
            # Try Windows Snipping Tool via subprocess (saves to clipboard, then we can save)
            try:
                # Use Windows API to save from clipboard
                import win32clipboard
                import win32con
                import win32gui
                import win32ui
                from PIL import Image
                
                # Simulate PrintScreen
                import pyautogui
                pyautogui.press('printscreen')
                import time
                time.sleep(0.3)  # Wait for clipboard
                
                # Get image from clipboard
                win32clipboard.OpenClipboard()
                try:
                    if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
                        data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                        win32clipboard.CloseClipboard()
                        
                        # Convert DIB to image
                        from io import BytesIO
                        import struct
                        
                        # Parse DIB header
                        width = struct.unpack('<L', data[4:8])[0]
                        height = struct.unpack('<L', data[8:12])[0]
                        
                        # Create PIL image from clipboard data
                        image = Image.frombytes('RGB', (width, abs(height)), data[14:])
                        image.save(str(save_path), 'PNG')
                        
                        if save_path.exists() and save_path.stat().st_size > 0:
                            folder_name = save_path.parent.name
                            return True, f"Ekran görüntüsü {folder_name} klasörüne kaydedildi: {save_path.name}"
                except Exception as clip_error:
                    print(f"Clipboard method error: {clip_error}")
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
            except ImportError:
                pass  # win32clipboard not available
            except Exception as e:
                print(f"Clipboard method failed: {e}")
            
            # Final fallback: inform user
            return False, "Ekran görüntüsü alınamadı. Lütfen PrintScreen tuşunu kullanın veya Snipping Tool'u açın."
            
        elif platform.system() == 'Darwin':  # macOS
            result = subprocess.run(['screencapture', str(save_path)], timeout=5, capture_output=True)
            if result.returncode == 0 and save_path.exists():
                return True, f"Ekran görüntüsü kaydedildi: {save_path}"
            else:
                return False, "Ekran görüntüsü alınamadı"
        else:  # Linux
            result = subprocess.run(['gnome-screenshot', '-f', str(save_path)], timeout=5, capture_output=True)
            if result.returncode == 0 and save_path.exists():
                return True, f"Ekran görüntüsü kaydedildi: {save_path}"
            else:
                return False, "Ekran görüntüsü alınamadı"
    except Exception as e:
        print(f"Screenshot fallback error: {e}")
        import traceback
        traceback.print_exc()
        return False, "Ekran görüntüsü alınamadı. Lütfen PrintScreen tuşunu kullanın."


def play_media():
    """Play media (if media player is open)"""
    try:
        if platform.system() == 'Windows':
            # Send space key to play/pause (works with most media players)
            import pyautogui
            try:
                pyautogui.press('space')
                return True, "Medya oynatıldı/durduruldu"
            except:
                return False, "Medya oynatıcı bulunamadı"
        else:
            return False, "Bu özellik şu an sadece Windows'ta destekleniyor"
    
    except ImportError:
        return False, "pyautogui kütüphanesi gerekli"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def pause_media():
    """Pause media"""
    return play_media()  # Same as play (toggle)


def next_track():
    """Skip to next track"""
    try:
        if platform.system() == 'Windows':
            import pyautogui
            try:
                pyautogui.press('nexttrack')
                return True, "Sonraki şarkı"
            except:
                return False, "Medya oynatıcı bulunamadı"
        else:
            return False, "Bu özellik şu an sadece Windows'ta destekleniyor"
    
    except ImportError:
        return False, "pyautogui kütüphanesi gerekli"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def previous_track():
    """Go to previous track"""
    try:
        if platform.system() == 'Windows':
            import pyautogui
            try:
                pyautogui.press('prevtrack')
                return True, "Önceki şarkı"
            except:
                return False, "Medya oynatıcı bulunamadı"
        else:
            return False, "Bu özellik şu an sadece Windows'ta destekleniyor"
    
    except ImportError:
        return False, "pyautogui kütüphanesi gerekli"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def volume_up_media():
    """Increase media volume"""
    try:
        if platform.system() == 'Windows':
            import pyautogui
            try:
                pyautogui.press('volumeup')
                return True, "Medya sesi artırıldı"
            except:
                return False, "Medya oynatıcı bulunamadı"
        else:
            return False, "Bu özellik şu an sadece Windows'ta destekleniyor"
    
    except ImportError:
        return False, "pyautogui kütüphanesi gerekli"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def volume_down_media():
    """Decrease media volume"""
    try:
        if platform.system() == 'Windows':
            import pyautogui
            try:
                pyautogui.press('volumedown')
                return True, "Medya sesi azaltıldı"
            except:
                return False, "Medya oynatıcı bulunamadı"
        else:
            return False, "Bu özellik şu an sadece Windows'ta destekleniyor"
    
    except ImportError:
        return False, "pyautogui kütüphanesi gerekli"
    except Exception as e:
        return False, f"Hata: {str(e)}"

