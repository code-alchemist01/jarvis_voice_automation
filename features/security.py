"""
Security features for JARVIS
"""
import subprocess
import platform
import ctypes
from ctypes import wintypes


def lock_computer():
    """Lock the computer"""
    try:
        if platform.system() == 'Windows':
            # Windows lock screen
            ctypes.windll.user32.LockWorkStation()
            return True, "Bilgisayar kilitlendi"
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['pmset', 'displaysleepnow'], timeout=5, capture_output=True)
            return True, "Bilgisayar kilitlendi"
        elif platform.system() == 'Linux':
            subprocess.run(['gnome-screensaver-command', '--lock'], timeout=5, capture_output=True)
            return True, "Bilgisayar kilitlendi"
        else:
            return False, "Bu işletim sistemi desteklenmiyor"
    except Exception as e:
        print(f"Error locking computer: {e}")
        return False, f"Bilgisayar kilitlenirken hata oluştu: {str(e)}"


def sleep_display():
    """Turn off display (sleep)"""
    try:
        if platform.system() == 'Windows':
            # Turn off display
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
            return True, "Ekran kapatıldı"
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['pmset', 'displaysleepnow'], timeout=5, capture_output=True)
            return True, "Ekran kapatıldı"
        elif platform.system() == 'Linux':
            subprocess.run(['xset', 'dpms', 'force', 'off'], timeout=5, capture_output=True)
            return True, "Ekran kapatıldı"
        else:
            return False, "Bu işletim sistemi desteklenmiyor"
    except Exception as e:
        print(f"Error sleeping display: {e}")
        return False, f"Ekran kapatılırken hata oluştu: {str(e)}"


def shutdown_computer(delay_seconds=0):
    """Shutdown the computer"""
    try:
        if platform.system() == 'Windows':
            if delay_seconds > 0:
                subprocess.run(['shutdown', '/s', '/t', str(delay_seconds)], timeout=5, capture_output=True)
                return True, f"Bilgisayar {delay_seconds} saniye sonra kapatılacak"
            else:
                subprocess.run(['shutdown', '/s', '/t', '0'], timeout=5, capture_output=True)
                return True, "Bilgisayar kapatılıyor"
        elif platform.system() == 'Darwin':  # macOS
            if delay_seconds > 0:
                subprocess.run(['shutdown', '-h', f'+{delay_seconds // 60}'], timeout=5, capture_output=True)
                return True, f"Bilgisayar {delay_seconds} saniye sonra kapatılacak"
            else:
                subprocess.run(['shutdown', '-h', 'now'], timeout=5, capture_output=True)
                return True, "Bilgisayar kapatılıyor"
        elif platform.system() == 'Linux':
            if delay_seconds > 0:
                subprocess.run(['shutdown', f'+{delay_seconds // 60}'], timeout=5, capture_output=True)
                return True, f"Bilgisayar {delay_seconds} saniye sonra kapatılacak"
            else:
                subprocess.run(['shutdown', 'now'], timeout=5, capture_output=True)
                return True, "Bilgisayar kapatılıyor"
        else:
            return False, "Bu işletim sistemi desteklenmiyor"
    except Exception as e:
        print(f"Error shutting down: {e}")
        return False, f"Bilgisayar kapatılırken hata oluştu: {str(e)}"


def restart_computer(delay_seconds=0):
    """Restart the computer"""
    try:
        if platform.system() == 'Windows':
            if delay_seconds > 0:
                subprocess.run(['shutdown', '/r', '/t', str(delay_seconds)], timeout=5, capture_output=True)
                return True, f"Bilgisayar {delay_seconds} saniye sonra yeniden başlatılacak"
            else:
                subprocess.run(['shutdown', '/r', '/t', '0'], timeout=5, capture_output=True)
                return True, "Bilgisayar yeniden başlatılıyor"
        elif platform.system() == 'Darwin':  # macOS
            if delay_seconds > 0:
                subprocess.run(['shutdown', '-r', f'+{delay_seconds // 60}'], timeout=5, capture_output=True)
                return True, f"Bilgisayar {delay_seconds} saniye sonra yeniden başlatılacak"
            else:
                subprocess.run(['shutdown', '-r', 'now'], timeout=5, capture_output=True)
                return True, "Bilgisayar yeniden başlatılıyor"
        elif platform.system() == 'Linux':
            if delay_seconds > 0:
                subprocess.run(['shutdown', '-r', f'+{delay_seconds // 60}'], timeout=5, capture_output=True)
                return True, f"Bilgisayar {delay_seconds} saniye sonra yeniden başlatılacak"
            else:
                subprocess.run(['shutdown', '-r', 'now'], timeout=5, capture_output=True)
                return True, "Bilgisayar yeniden başlatılıyor"
        else:
            return False, "Bu işletim sistemi desteklenmiyor"
    except Exception as e:
        print(f"Error restarting: {e}")
        return False, f"Bilgisayar yeniden başlatılırken hata oluştu: {str(e)}"

