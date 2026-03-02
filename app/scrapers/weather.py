import httpx
import os
import asyncio
import json
from sqlalchemy.orm import Session
from .. import models
from datetime import datetime
from sqlalchemy.sql import func
from .utils import async_get

# Weather code mapping to conditions and icons (WMO Weather interpretation codes)
# Based on https://open-meteo.com/en/docs
WMO_CODE_MAP = {
    0: ("Czyste niebo", "01d"),
    1: ("Głównie bezchmurnie", "02d"),
    2: ("Częściowe zachmurzenie", "03d"),
    3: ("Zachmurzenie", "04d"),
    45: ("Mgła", "50d"), 
    48: ("Mgła osadzająca szadź", "50d"),
    51: ("Lekka mżawka", "09d"),
    53: ("Mżawka", "09d"),
    55: ("Gęsta mżawka", "09d"),
    61: ("Lekki deszcz", "10d"),
    63: ("Deszcz", "10d"),
    65: ("Ulewny deszcz", "10d"),
    71: ("Lekki śnieg", "13d"),
    73: ("Śnieg", "13d"),
    75: ("Gęsty śnieg", "13d"),
    77: ("Grad", "13d"),
    80: ("Lekkie opady deszczu", "09d"),
    81: ("Opady deszczu", "09d"),
    82: ("Gwałtowne ulewy", "09d"),
    85: ("Lekkie opady śniegu", "13d"),
    86: ("Gęste opady śniegu", "13d"),
    95: ("Burza", "11d"),
    96: ("Burza z gradem", "11d"),
    99: ("Gwałtowna burza z gradem", "11d")
}

def get_weather_info(code):
    return WMO_CODE_MAP.get(code, ("Nieznana", "03d"))

async def update_weather(db: Session, country_iso2: str, client: httpx.AsyncClient = None):
    """Fetch current weather and 7-day forecast using Open-Meteo"""
    
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country or country.latitude is None or country.longitude is None:
        return {"error": "Country location not found"}

    # Open-Meteo API URL for forecast
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(country.latitude),
        "longitude": float(country.longitude),
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }

    try:
        if client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        else:
            async with httpx.AsyncClient() as c:
                response = await c.get(url, params=params)
                response.raise_for_status()
                data = response.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        cond_text, cond_icon = get_weather_info(current.get("weather_code", 0))
        
        # Prepare 7-day forecast list
        forecast = []
        for i in range(len(daily.get("time", []))):
            d_cond_text, d_cond_icon = get_weather_info(daily.get("weather_code", [])[i])
            forecast.append({
                "date": daily.get("time", [])[i],
                "temp_max": daily.get("temperature_2m_max", [])[i],
                "temp_min": daily.get("temperature_2m_min", [])[i],
                "condition": d_cond_text,
                "icon": d_cond_icon
            })

        weather_data = {
            'temp_c': current.get('temperature_2m', 0),
            'feels_like_c': current.get('apparent_temperature', 0),
            'condition': cond_text,
            'condition_icon': cond_icon,
            'humidity': current.get('relative_humidity_2m', 0),
            'wind_kph': current.get('wind_speed_10m', 0),
            'forecast_json': json.dumps(forecast),
            'last_updated': func.now()
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
        # print(f"Error updating weather for {country_iso2}: {e}")
        return {"error": str(e)}

async def update_all_weather(db: Session):
    """Update weather for all countries using Open-Meteo"""
    countries = db.query(models.Country).filter(models.Country.latitude != None, models.Country.longitude != None).all()
    
    success = 0
    errors = 0
    
    # Open-Meteo doesn't require API key and has very generous rate limits
    # We still do them sequentially but faster
    async with httpx.AsyncClient() as client:
        for i, country in enumerate(countries):
            if (i+1) % 50 == 0:
                print(f"Updating weather: {i+1}/{len(countries)}...")
            res = await update_weather(db, country.iso_alpha2, client)
            if "error" in res:
                errors += 1
            else:
                success += 1
            await asyncio.sleep(0.05) 
    
    return {"success": success, "errors": errors}
