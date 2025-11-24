"""
Web search features
"""
import webbrowser
import urllib.parse
import requests
from utils.config import config

# Try to import Wikipedia
WIKIPEDIA_AVAILABLE = False
try:
    import wikipedia
    wikipedia.set_lang("tr")  # Set Turkish as default
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    pass  # Wikipedia library not available


def search_google(query):
    """Search Google and open in browser"""
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return True, f"Google'da aranıyor: {query}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def open_website(url):
    """Open a website in browser"""
    try:
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        return True, f"Web sitesi açılıyor: {url}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def search_youtube(query):
    """Search YouTube and open in browser"""
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return True, f"YouTube'da aranıyor: {query}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def search_wikipedia(query):
    """Search Wikipedia and return summary"""
    try:
        if not WIKIPEDIA_AVAILABLE:
            # Fallback: open Wikipedia in browser
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://tr.wikipedia.org/wiki/{encoded_query}"
            webbrowser.open(url)
            return True, f"Wikipedia'da aranıyor: {query}"
        
        # Try to get page summary
        try:
            page = wikipedia.page(query, auto_suggest=True)
            summary = page.summary[:500]  # First 500 characters
            url = page.url
            
            # Open in browser
            webbrowser.open(url)
            
            return True, f"Wikipedia: {summary}... Daha fazlası için tarayıcıda açıldı."
        except wikipedia.DisambiguationError as e:
            # If disambiguation, open the first option
            page = wikipedia.page(e.options[0])
            webbrowser.open(page.url)
            return True, f"Wikipedia'da '{e.options[0]}' bulundu ve açıldı."
        except wikipedia.PageError:
            # Page not found, search instead
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://tr.wikipedia.org/wiki/Special:Search/{encoded_query}"
            webbrowser.open(url)
            return True, f"Wikipedia'da '{query}' için arama yapıldı."
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        return False, f"Wikipedia araması sırasında hata oluştu: {str(e)}"


def get_news(country='tr', category='general', limit=5):
    """Get news headlines"""
    try:
        # Using NewsAPI (requires API key)
        api_key = config.get('news.api_key', '')
        
        if not api_key:
            # Fallback: open news website
            if country == 'tr':
                webbrowser.open('https://www.haberturk.com/')
                return True, "Haberler açılıyor"
            else:
                webbrowser.open('https://www.bbc.com/news')
                return True, "News opened"
        
        # Try to fetch from NewsAPI
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            'country': country,
            'category': category,
            'apiKey': api_key,
            'pageSize': limit
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            if articles:
                news_text = "Son haberler:\n"
                for i, article in enumerate(articles[:limit], 1):
                    title = article.get('title', 'Başlık yok')
                    news_text += f"{i}. {title}\n"
                
                return True, news_text
            else:
                return True, "Haber bulunamadı"
        else:
            # Fallback to opening news website
            if country == 'tr':
                webbrowser.open('https://www.haberturk.com/')
            else:
                webbrowser.open('https://www.bbc.com/news')
            return True, "Haberler açılıyor"
            
    except Exception as e:
        print(f"Error getting news: {e}")
        # Fallback: open news website
        try:
            if country == 'tr':
                webbrowser.open('https://www.haberturk.com/')
            else:
                webbrowser.open('https://www.bbc.com/news')
            return True, "Haberler açılıyor"
        except:
            return False, f"Haberler alınırken hata oluştu: {str(e)}"

