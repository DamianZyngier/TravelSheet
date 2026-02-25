import httpx
import os
import asyncio
from sqlalchemy.orm import Session
from .. import models
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def update_weather(db: Session, country_iso2: str, client: httpx.AsyncClient = None):
    """Fetch current weather for country capital using OpenWeatherMap"""
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OPENWEATHER_API_KEY not set"}
    
    api_key = api_key.strip() # Clean potential whitespace

    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country or not country.capital:
        return {"error": "Country or capital not found"}

    # Use params dict for safer encoding
    params = {
        "q": f"{country.capital},{country_iso2}",
        "appid": api_key,
        "units": "metric"
    }
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Use provided client or create new one
    close_client = False
    if client is None:
        client = httpx.AsyncClient()
        close_client = True

    try:
        response = await client.get(url, params=params)
        if response.status_code == 401:
            return {"error": f"Invalid API Key (401). Body: {response.text}"}
        if response.status_code == 429:
            return {"error": "Rate limit exceeded"}
        
        response.raise_for_status()
        data = response.json()
        
        weather_data = {
            'temp_c': data['main']['temp'],
            'feels_like_c': data['main']['feels_like'],
            'condition': data['weather'][0]['main'],
            'condition_icon': data['weather'][0]['icon'],
            'humidity': data['main']['humidity'],
            'wind_kph': data['wind']['speed'] * 3.6,
            'last_updated': datetime.now()
        }

        weather = db.query(models.Weather).filter(models.Weather.country_id == country.id).first()
        if weather:
            for key, value in weather_data.items():
                setattr(weather, key, value)
        else:
            weather = models.Weather(country_id=country.id, **weather_data)
            db.add(weather)
        
        db.commit()
        return {"status": "success", "temp": weather_data['temp_c']}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if close_client:
            await client.aclose()

async def update_all_weather(db: Session):
    """Update weather for all countries with rate limiting (max 45 calls/min)"""
    countries = db.query(models.Country).filter(models.Country.capital != None).all()
    
    async with httpx.AsyncClient() as client:
        for country in countries:
            print(f"Updating weather for {country.name}...")
            await update_weather(db, country.iso_alpha2, client)
            # 60s / 45 calls = 1.33s. Let's wait 1.5s to be safe.
            await asyncio.sleep(1.5)
    
    return {"status": "completed", "count": len(countries)}
