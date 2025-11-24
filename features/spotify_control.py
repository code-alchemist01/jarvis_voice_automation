"""
Spotify control features
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils.config import config

# Global Spotify client
_spotify_client = None


def _get_spotify_client():
    """Get or create Spotify client"""
    if not SPOTIPY_AVAILABLE:
        return None, "spotipy kütüphanesi yüklü değil. Lütfen yükleyin: pip install spotipy"
    
    global _spotify_client
    
    if _spotify_client:
        return _spotify_client, None
    
    try:
        client_id = config.get('spotify.client_id', '')
        client_secret = config.get('spotify.client_secret', '')
        redirect_uri = config.get('spotify.redirect_uri', 'http://localhost:8888/callback')
        
        if not client_id or not client_secret:
            return None, "Spotify Client ID ve Secret ayarlanmamış. Lütfen ayarlardan yapılandırın."
        
        scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-read-private"
        
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=str(config.get('spotify.token_cache', 'tokens/spotify_token.json'))
        )
        
        _spotify_client = spotipy.Spotify(auth_manager=auth_manager)
        return _spotify_client, None
    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        return None, f"Spotify bağlantısı kurulamadı: {str(e)}"


def play_song(song_name):
    """Play a song on Spotify"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        # Search for song
        results = sp.search(q=song_name, type='track', limit=1)
        
        if not results['tracks']['items']:
            return False, f"'{song_name}' şarkısı bulunamadı."
        
        track_uri = results['tracks']['items'][0]['uri']
        
        # Play song
        sp.start_playback(uris=[track_uri])
        
        track_name = results['tracks']['items'][0]['name']
        artist = results['tracks']['items'][0]['artists'][0]['name']
        
        return True, f"Çalıyor: {track_name} - {artist}"
    except Exception as e:
        print(f"Error playing song: {e}")
        return False, f"Şarkı çalınırken hata oluştu: {str(e)}"


def pause_playback():
    """Pause Spotify playback"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        sp.pause_playback()
        return True, "Müzik duraklatıldı"
    except Exception as e:
        print(f"Error pausing: {e}")
        return False, f"Müzik duraklatılırken hata oluştu: {str(e)}"


def resume_playback():
    """Resume Spotify playback"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        sp.start_playback()
        return True, "Müzik devam ediyor"
    except Exception as e:
        print(f"Error resuming: {e}")
        return False, f"Müzik devam ettirilirken hata oluştu: {str(e)}"


def next_track():
    """Skip to next track"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        sp.next_track()
        return True, "Sonraki şarkı"
    except Exception as e:
        print(f"Error skipping track: {e}")
        return False, f"Şarkı değiştirilirken hata oluştu: {str(e)}"


def previous_track():
    """Skip to previous track"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        sp.previous_track()
        return True, "Önceki şarkı"
    except Exception as e:
        print(f"Error going to previous track: {e}")
        return False, f"Şarkı değiştirilirken hata oluştu: {str(e)}"


def get_current_track():
    """Get currently playing track"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        current = sp.current_playback()
        
        if not current or not current['is_playing']:
            return True, "Şu an müzik çalmıyor"
        
        track = current['item']
        track_name = track['name']
        artist = track['artists'][0]['name']
        
        return True, f"Şu an çalıyor: {track_name} - {artist}"
    except Exception as e:
        print(f"Error getting current track: {e}")
        return False, f"Şu an çalan şarkı bilgisi alınamadı: {str(e)}"


def set_volume(volume_percent):
    """Set Spotify volume (0-100)"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        volume_percent = max(0, min(100, volume_percent))
        sp.volume(volume_percent)
        
        return True, f"Spotify ses seviyesi {volume_percent}% olarak ayarlandı"
    except Exception as e:
        print(f"Error setting volume: {e}")
        return False, f"Ses seviyesi ayarlanırken hata oluştu: {str(e)}"


def get_playlists():
    """Get user's playlists"""
    try:
        sp, error = _get_spotify_client()
        if error:
            return False, error
        
        playlists = sp.current_user_playlists(limit=10)
        
        if not playlists['items']:
            return True, "Çalma listeniz bulunamadı"
        
        result = "Çalma listeleriniz:\n"
        for playlist in playlists['items']:
            result += f"- {playlist['name']} ({playlist['tracks']['total']} şarkı)\n"
        
        return True, result
    except Exception as e:
        print(f"Error getting playlists: {e}")
        return False, f"Çalma listeleri alınırken hata oluştu: {str(e)}"

