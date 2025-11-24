"""
Web search features
"""
import webbrowser
import urllib.parse
import requests
import subprocess
import re
from utils.config import config

# Try to import Wikipedia
WIKIPEDIA_AVAILABLE = False
try:
    import wikipedia
    wikipedia.set_lang("tr")  # Set Turkish as default
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    pass  # Wikipedia library not available

# Try to import BeautifulSoup
BS4_AVAILABLE = False
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    pass

# Common website mappings
WEBSITE_MAPPINGS = {
    'youtube': 'https://www.youtube.com',
    'reddit': 'https://www.reddit.com',
    'facebook': 'https://www.facebook.com',
    'twitter': 'https://www.twitter.com',
    'instagram': 'https://www.instagram.com',
    'linkedin': 'https://www.linkedin.com',
    'github': 'https://www.github.com',
    'stackoverflow': 'https://stackoverflow.com',
    'wikipedia': 'https://tr.wikipedia.org',
    'google': 'https://www.google.com',
    'gmail': 'https://mail.google.com',
    'outlook': 'https://outlook.live.com',
    'netflix': 'https://www.netflix.com',
    'spotify': 'https://open.spotify.com',
    'discord': 'https://discord.com',
    'telegram': 'https://web.telegram.org',
    'whatsapp': 'https://web.whatsapp.com',
}

# Browser mappings
BROWSER_MAPPINGS = {
    'chrome': 'chrome.exe',
    'google chrome': 'chrome.exe',
    'microsoft edge': 'msedge.exe',
    'edge': 'msedge.exe',
    'firefox': 'firefox.exe',
    'opera': 'opera.exe',
    'brave': 'brave.exe',
}


def search_google(query):
    """Search Google and open in browser"""
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return True, f"Google'da aranıyor: {query}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def _search_website_url(site_name):
    """Search for website URL using Google search"""
    try:
        # Search Google for the site
        search_query = f"{site_name} site"
        encoded_query = urllib.parse.quote_plus(search_query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        # Get search results page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=5)
        
        if response.status_code == 200 and BS4_AVAILABLE:
            # Parse HTML to find first result
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find first search result link
            # Google search results are in <a> tags with href starting with /url?q=
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('/url?q='):
                    # Extract actual URL
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    actual_url = urllib.parse.unquote(actual_url)
                    
                    # Verify it's a valid URL
                    if actual_url.startswith(('http://', 'https://')):
                        # Check if it's not a Google service page
                        if 'google.com' not in actual_url.lower() or 'webcache' not in actual_url.lower():
                            return actual_url
            
            # Alternative: look for cite tags (Google's new structure)
            for cite in soup.find_all('cite'):
                parent = cite.find_parent('a')
                if parent and parent.get('href'):
                    href = parent.get('href')
                    if href.startswith('/url?q='):
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        actual_url = urllib.parse.unquote(actual_url)
                        if actual_url.startswith(('http://', 'https://')):
                            if 'google.com' not in actual_url.lower() or 'webcache' not in actual_url.lower():
                                return actual_url
        
        # Fallback: return None to use Google search page
        return None
    except Exception:
        return None


def open_website(url, browser=None):
    """Open a website in browser - intelligently finds website URLs"""
    try:
        original_url = url
        url_lower = url.lower().strip()
        found_url = None
        
        # Step 1: Check if it's a known website name
        if url_lower in WEBSITE_MAPPINGS:
            found_url = WEBSITE_MAPPINGS[url_lower]
        elif not url.startswith(('http://', 'https://')):
            # Step 2: Try to find partial match in known websites
            for site_name, site_url in WEBSITE_MAPPINGS.items():
                if site_name in url_lower or url_lower in site_name:
                    found_url = site_url
                    break
            
            # Step 3: If not found, try to search Google for the website
            if not found_url:
                # Check if it looks like a domain name (has dots)
                if '.' in url and not any(char in url for char in [' ', '\t', '\n']):
                    # Looks like a domain, try adding https://
                    found_url = 'https://' + url
                else:
                    # It's a site name, search for it
                    found_url = _search_website_url(url)
                    
                    if not found_url:
                        # If search failed, open Google search for the site name
                        search_query = f"{url} site"
                        encoded_query = urllib.parse.quote_plus(search_query)
                        found_url = f"https://www.google.com/search?q={encoded_query}"
                        # Return early with search page
                        if browser:
                            browser_lower = browser.lower().strip()
                            browser_exe = BROWSER_MAPPINGS.get(browser_lower)
                            if browser_exe:
                                try:
                                    subprocess.Popen([browser_exe, found_url], shell=True)
                                    return True, f"{browser} ile '{url}' için arama yapılıyor"
                                except:
                                    webbrowser.open(found_url)
                                    return True, f"'{url}' için arama yapılıyor"
                            else:
                                webbrowser.open(found_url)
                                return True, f"'{url}' için arama yapılıyor"
                        else:
                            webbrowser.open(found_url)
                            return True, f"'{url}' için arama yapılıyor"
        else:
            # Already a full URL
            found_url = url
        
        # Handle browser specification
        if browser:
            browser_lower = browser.lower().strip()
            browser_exe = BROWSER_MAPPINGS.get(browser_lower)
            
            if browser_exe:
                try:
                    # Try to open with specific browser
                    subprocess.Popen([browser_exe, found_url], shell=True)
                    return True, f"{browser} ile {found_url} açılıyor"
                except Exception:
                    # Fallback to default browser
                    webbrowser.open(found_url)
                    return True, f"Web sitesi açılıyor: {found_url}"
            else:
                # Unknown browser, use default
                webbrowser.open(found_url)
                return True, f"Web sitesi açılıyor: {found_url}"
        else:
            # Use default browser
            webbrowser.open(found_url)
            return True, f"Web sitesi açılıyor: {found_url}"
    except Exception as e:
        return False, f"Hata: {str(e)}"


def search_youtube(query=None):
    """Search YouTube or open YouTube homepage"""
    try:
        if query and query.strip():
            # Search YouTube
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(url)
            return True, f"YouTube'da aranıyor: {query}"
        else:
            # Just open YouTube
            url = "https://www.youtube.com"
            webbrowser.open(url)
            return True, "YouTube açılıyor"
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


def get_news(country='tr', category='general', limit=10):
    """Get news headlines from RSS feeds or web scraping"""
    try:
        # Try NewsAPI first if API key is available
        api_key = config.get('news.api_key', '')
        
        if api_key:
            url = f"https://newsapi.org/v2/top-headlines"
            params = {
                'country': country,
                'category': category,
                'apiKey': api_key,
                'pageSize': limit
            }
            
            try:
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    if articles:
                        news_text = "📰 Son Haberler:\n\n"
                        for i, article in enumerate(articles[:limit], 1):
                            title = article.get('title', 'Başlık yok')
                            source = article.get('source', {}).get('name', '')
                            news_text += f"{i}. {title}"
                            if source:
                                news_text += f" ({source})"
                            news_text += "\n"
                        
                        return True, news_text
            except Exception:
                pass  # Fall through to RSS/web scraping
        
        # Fallback: Use RSS feeds or web scraping
        news_text = "📰 Son Haberler:\n\n"
        news_found = False
        
        if country == 'tr':
            # Try to get news from Turkish news sites
            news_sources = [
                ('https://www.haberturk.com/rss', 'Habertürk'),
                ('https://www.hurriyet.com.tr/rss/gundem', 'Hürriyet'),
                ('https://www.ntv.com.tr/gundem.rss', 'NTV'),
            ]
        else:
            # English news sources
            news_sources = [
                ('https://feeds.bbci.co.uk/news/rss.xml', 'BBC'),
                ('https://rss.cnn.com/rss/edition.rss', 'CNN'),
                ('https://feeds.npr.org/1001/rss.xml', 'NPR'),
            ]
        
        for rss_url, source_name in news_sources[:2]:  # Try first 2 sources
            try:
                response = requests.get(rss_url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200:
                    if BS4_AVAILABLE:
                        # Parse RSS with BeautifulSoup
                        soup = BeautifulSoup(response.content, 'xml')
                        items = soup.find_all('item')[:limit//2]  # Get half from each source
                        
                        for i, item in enumerate(items, start=len([x for x in news_text.split('\n') if x.strip()]) + 1):
                            title_tag = item.find('title')
                            if title_tag:
                                title = title_tag.get_text().strip()
                                news_text += f"{i}. {title} ({source_name})\n"
                                news_found = True
                    else:
                        # Simple regex parsing if BeautifulSoup not available
                        import re
                        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', response.text)
                        if not titles:
                            titles = re.findall(r'<title>(.*?)</title>', response.text)
                        
                        for i, title in enumerate(titles[1:limit//2+1], start=len([x for x in news_text.split('\n') if x.strip()]) + 1):  # Skip first title (usually site name)
                            news_text += f"{i}. {title.strip()} ({source_name})\n"
                            news_found = True
                    
                    if news_found and len([x for x in news_text.split('\n') if x.strip()]) >= limit:
                        break
            except Exception:
                continue
        
        if news_found:
            return True, news_text
        else:
            # Last resort: open news website
            if country == 'tr':
                webbrowser.open('https://www.haberturk.com/')
                return True, "Haberler açılıyor (web sitesinden kontrol edebilirsiniz)"
            else:
                webbrowser.open('https://www.bbc.com/news')
                return True, "News opened (check the website)"
            
    except Exception as e:
        # Final fallback: open news website
        try:
            if country == 'tr':
                webbrowser.open('https://www.haberturk.com/')
                return True, "Haberler açılıyor"
            else:
                webbrowser.open('https://www.bbc.com/news')
                return True, "News opened"
        except:
            return False, f"Haberler alınırken hata oluştu: {str(e)}"

