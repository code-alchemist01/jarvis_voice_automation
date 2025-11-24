"""
System monitoring features
"""
import platform
from datetime import datetime

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_system_status():
    """Get overall system status"""
    try:
        if not PSUTIL_AVAILABLE:
            return False, "psutil kütüphanesi gerekli. 'pip install psutil' ile yükleyin."
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = f"Sistem Durumu:\n"
        status += f"CPU Kullanımı: %{cpu_percent:.1f}\n"
        status += f"Bellek Kullanımı: %{memory.percent:.1f} ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)\n"
        status += f"Disk Kullanımı: %{disk.percent:.1f} ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
        
        return True, status
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def get_memory_usage():
    """Get memory usage information"""
    try:
        if not PSUTIL_AVAILABLE:
            return False, "psutil kütüphanesi gerekli"
        
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024**3)
        total_gb = memory.total / (1024**3)
        percent = memory.percent
        
        result = f"Bellek kullanımı: %{percent:.1f} ({used_gb:.1f}GB / {total_gb:.1f}GB)"
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def get_cpu_usage():
    """Get CPU usage information"""
    try:
        if not PSUTIL_AVAILABLE:
            return False, "psutil kütüphanesi gerekli"
        
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        result = f"CPU kullanımı: %{cpu_percent:.1f} ({cpu_count} çekirdek)"
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def get_disk_usage():
    """Get disk usage information"""
    try:
        if not PSUTIL_AVAILABLE:
            return False, "psutil kütüphanesi gerekli"
        
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024**3)
        total_gb = disk.total / (1024**3)
        free_gb = disk.free / (1024**3)
        percent = disk.percent
        
        result = f"Disk kullanımı: %{percent:.1f} (Kullanılan: {used_gb:.1f}GB, Boş: {free_gb:.1f}GB, Toplam: {total_gb:.1f}GB)"
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def get_battery_status():
    """Get battery status (if available)"""
    try:
        if not PSUTIL_AVAILABLE:
            return False, "psutil kütüphanesi gerekli"
        
        battery = psutil.sensors_battery()
        if battery is None:
            return False, "Pil bilgisi mevcut değil (masaüstü bilgisayar)"
        
        percent = battery.percent
        plugged = battery.power_plugged
        
        status = "Şarj oluyor" if plugged else "Şarj olmuyor"
        result = f"Pil: %{percent:.0f} - {status}"
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def get_running_processes(count=5):
    """Get top running processes by CPU usage"""
    try:
        if not PSUTIL_AVAILABLE:
            return False, "psutil kütüphanesi gerekli"
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        result = f"En çok CPU kullanan {count} işlem:\n"
        for i, proc in enumerate(processes[:count], 1):
            cpu = proc['cpu_percent'] or 0
            name = proc['name'] or 'Bilinmeyen'
            result += f"{i}. {name}: %{cpu:.1f}\n"
        
        return True, result
    
    except Exception as e:
        return False, f"Hata: {str(e)}"

