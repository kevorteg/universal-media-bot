import requests, re
from bs4 import BeautifulSoup
from src.database import get_connection

url = "https://seriesbiblicas.net/peliculas/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

links = [a.get('href', '') for a in soup.find_all('a')]
p_links = [l for l in links if 'seriesbiblicas.net/p' in l][:5]
print("Ejemplo enlaces p*:")
for l in p_links:
    print(l)
    print(" Match regex /p\d+: ", bool(re.search(r"seriesbiblicas\.net/p\d+", l)))
    
# Debuguear por que salen 0 items nuevos
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT count(*) as c FROM multimedia")
print(f"Total en DB: {cursor.fetchone()['c']}")
conn.close()
