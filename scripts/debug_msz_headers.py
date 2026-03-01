import asyncio
import httpx
import sys
import os
from bs4 import BeautifulSoup
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.utils import get_headers

async def debug_headers(iso):
    urls = {
        'TT': 'https://www.gov.pl/web/wenezuela/trynidad-i-tobago-idp',
        'TH': 'https://www.gov.pl/web/tajlandia/idp',
        'AE': 'https://www.gov.pl/web/zea/informacje-dla-podrozujacych'
    }
    url = urls.get(iso)
    print(f"\n--- Checking {iso}: {url} ---")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=get_headers())
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            headers = soup.find_all(['h2', 'h3', 'strong'])
            print("HEADERS FOUND:")
            for h in headers:
                txt = h.get_text().strip()
                if txt:
                    print(f"[{h.name}] {txt}")
                    
            pattern = re.compile(r'Miejscowe prawo i zwyczaje|Prawo i obyczaje|Miejscowe prawo|Zwyczaje', re.I)
            print("\nSEARCH RESULTS:")
            for h in headers:
                if pattern.search(h.get_text()):
                    print(f"✅ MATCH: [{h.name}] {h.get_text().strip()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    for iso in ['TT', 'TH', 'AE']:
        asyncio.run(debug_headers(iso))
