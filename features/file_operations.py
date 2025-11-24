"""
File operations features
"""
import os
import subprocess
import platform
from pathlib import Path
from datetime import datetime


def open_file(file_path):
    """Open a file with default application"""
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        return True, f"Dosya açılıyor: {file_path}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_folder(folder_path):
    """Open a folder in file explorer"""
    try:
        if platform.system() == 'Windows':
            subprocess.run(['explorer', folder_path])
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', folder_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
        return True, f"Klasör açılıyor: {folder_path}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def search_file(filename, search_path=None):
    """Search for a file"""
    try:
        if search_path is None:
            search_path = os.path.expanduser('~')
        
        found_files = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if filename.lower() in file.lower():
                    found_files.append(os.path.join(root, file))
                    if len(found_files) >= 10:  # Limit results
                        break
            if len(found_files) >= 10:
                break
        
        if found_files:
            result = f"{len(found_files)} dosya bulundu. İlk sonuç: {found_files[0]}"
            return True, result
        else:
            return False, "Dosya bulunamadı"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def read_file(file_path):
    """Read a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Limit content length for TTS
            if len(content) > 500:
                content = content[:500] + "..."
            return True, content
    except Exception as e:
        return False, f"Hata: {str(e)}"


def get_desktop_path():
    """Get desktop path"""
    try:
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    except:
        return None


def search_file_in_desktop(filename):
    """Search for a file on desktop"""
    desktop = get_desktop_path()
    if desktop:
        return search_file(filename, desktop)
    return False, "Masaüstü bulunamadı"


def get_recent_files(count=5):
    """Get recently accessed files (Windows)"""
    try:
        if platform.system() == 'Windows':
            recent_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Recent')
            if os.path.exists(recent_path):
                files = []
                for item in os.listdir(recent_path):
                    item_path = os.path.join(recent_path, item)
                    if os.path.isfile(item_path):
                        files.append((item, os.path.getmtime(item_path)))
                
                # Sort by modification time
                files.sort(key=lambda x: x[1], reverse=True)
                
                result = f"Son açılan {min(count, len(files))} dosya:\n"
                for i, (name, _) in enumerate(files[:count], 1):
                    result += f"{i}. {name}\n"
                
                return True, result
            else:
                return False, "Son dosyalar bulunamadı"
        else:
            return False, "Bu özellik şu an sadece Windows'ta destekleniyor"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_documents_folder():
    """Open Documents folder"""
    try:
        docs_path = os.path.join(os.path.expanduser('~'), 'Documents')
        return open_folder(docs_path)
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_downloads_folder():
    """Open Downloads folder"""
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        return open_folder(downloads_path)
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_pictures_folder():
    """Open Pictures folder"""
    try:
        if platform.system() == 'Windows':
            pictures_path = os.path.join(os.path.expanduser('~'), 'Pictures')
        else:
            pictures_path = os.path.join(os.path.expanduser('~'), 'Pictures')
        return open_folder(pictures_path)
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_videos_folder():
    """Open Videos folder"""
    try:
        if platform.system() == 'Windows':
            videos_path = os.path.join(os.path.expanduser('~'), 'Videos')
        else:
            videos_path = os.path.join(os.path.expanduser('~'), 'Videos')
        return open_folder(videos_path)
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_music_folder():
    """Open Music folder"""
    try:
        if platform.system() == 'Windows':
            music_path = os.path.join(os.path.expanduser('~'), 'Music')
        else:
            music_path = os.path.join(os.path.expanduser('~'), 'Music')
        return open_folder(music_path)
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_desktop_folder():
    """Open Desktop folder"""
    try:
        desktop_path = get_desktop_path()
        if desktop_path:
            return open_folder(desktop_path)
        else:
            return False, "Masaüstü bulunamadı"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_folder_by_name(folder_name):
    """Open a folder by name (Pictures, Videos, Music, Documents, Downloads, Desktop)"""
    folder_name_lower = folder_name.lower()
    
    # Turkish and English mappings
    folder_map = {
        'resimler': 'pictures',
        'pictures': 'pictures',
        'görseller': 'pictures',
        'videolar': 'videos',
        'videos': 'videos',
        'müzik': 'music',
        'music': 'music',
        'belgeler': 'documents',
        'documents': 'documents',
        'indirilenler': 'downloads',
        'downloads': 'downloads',
        'masaüstü': 'desktop',
        'desktop': 'desktop',
    }
    
    mapped_name = folder_map.get(folder_name_lower, folder_name_lower)
    
    if mapped_name == 'pictures':
        return open_pictures_folder()
    elif mapped_name == 'videos':
        return open_videos_folder()
    elif mapped_name == 'music':
        return open_music_folder()
    elif mapped_name == 'documents':
        return open_documents_folder()
    elif mapped_name == 'downloads':
        return open_downloads_folder()
    elif mapped_name == 'desktop':
        return open_desktop_folder()
    else:
        # Try to find folder in user directory
        folder_path = os.path.join(os.path.expanduser('~'), folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return open_folder(folder_path)
        else:
            return False, f"Klasör bulunamadı: {folder_name}"


def create_folder(folder_name, parent_path=None):
    """Create a new folder"""
    try:
        if parent_path is None:
            parent_path = get_desktop_path() or os.path.expanduser('~')
        
        folder_path = os.path.join(parent_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return True, f"Klasör oluşturuldu: {folder_path}"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def delete_file_safe(file_path):
    """Delete a file safely (move to recycle bin on Windows)"""
    try:
        if platform.system() == 'Windows':
            # Use send2trash if available, otherwise regular delete
            try:
                import send2trash
                send2trash.send2trash(file_path)
                return True, f"Dosya geri dönüşüm kutusuna taşındı: {file_path}"
            except ImportError:
                # Fallback to regular delete
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True, f"Dosya silindi: {file_path}"
                else:
                    return False, "Dosya bulunamadı"
        else:
            # Linux/Mac - regular delete
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, f"Dosya silindi: {file_path}"
            else:
                return False, "Dosya bulunamadı"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"

