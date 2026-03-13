import requests
from bs4 import BeautifulSoup

url = "https://seriesbiblicas.net/peliculas/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.select('div.content a, main a, .post-item a, article a')
print(f"Total links en items: {len(items)}")

for a in items[:20]:
    href = a.get('href', '')
    if 'seriesbiblicas.net/p' in href or 'seriesbiblicas.net/serie' in href:
        title = a.get('title')
        if not title:
            # Maybe inside an img alt
            img = a.find('img')
            if img:
                title = img.get('alt') or img.get('title')
        
        if not title:
            title = a.text.strip()
            
        print(f"URL: {href} | TITLE: {title}")
