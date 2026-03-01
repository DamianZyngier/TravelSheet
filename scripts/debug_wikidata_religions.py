import httpx
import json
import asyncio

async def debug_religions(iso):
    query = f"""
    SELECT ?religionLabel ?religion ?percent WHERE {{
      ?country wdt:P297 "{iso.upper()}".
      OPTIONAL {{
        ?country p:P140 ?relStatement.
        ?relStatement ps:P140 ?religion.
        OPTIONAL {{ ?relStatement pq:P2107 ?percent. }}
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelSheet/1.1",
        "Accept": "application/sparql-results+json"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, data={'query': query}, headers=headers)
        print(f"--- Raw Results for {iso} ---")
        print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(debug_religions("AE"))
