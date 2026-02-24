from sqlalchemy.orm import Session
from .. import models
import logging

logger = logging.getLogger("uvicorn")

# Static UNESCO Data for major countries (Fallback since API is often blocking)
UNESCO_DATA = {
    'PL': [('Kraków Historic Centre', 'Cultural'), ('Wieliczka Salt Mine', 'Cultural'), ('Auschwitz Birkenau', 'Cultural'), ('Białowieża Forest', 'Natural'), ('Warsaw Historic Centre', 'Cultural')],
    'IT': [('Historic Centre of Rome', 'Cultural'), ('Pompeii', 'Cultural'), ('Venice and its Lagoon', 'Cultural'), ('Amalfi Coast', 'Cultural'), ('The Dolomites', 'Natural')],
    'FR': [('Palace of Versailles', 'Cultural'), ('Mont-Saint-Michel', 'Cultural'), ('Paris, Banks of the Seine', 'Cultural'), ('Chartres Cathedral', 'Cultural')],
    'ES': [('Alhambra, Generalife and Albayzín', 'Cultural'), ('Works of Antoni Gaudí', 'Cultural'), ('Historic Centre of Cordoba', 'Cultural')],
    'JP': [('Historic Monuments of Ancient Kyoto', 'Cultural'), ('Itsukushima Shinto Shrine', 'Cultural'), ('Himeji-jo', 'Cultural'), ('Yakushima', 'Natural'), ('Mount Fuji', 'Cultural')],
    'EG': [('Pyramids of Giza', 'Cultural'), ('Ancient Thebes with its Necropolis', 'Cultural'), ('Abu Simbel', 'Cultural')],
    'US': [('Grand Canyon National Park', 'Natural'), ('Statue of Liberty', 'Cultural'), ('Yellowstone National Park', 'Natural'), ('Yosemite', 'Natural')],
    'CN': [('The Great Wall', 'Cultural'), ('Imperial Palaces of the Ming and Qing Dynasties', 'Cultural'), ('Mausoleum of the First Qin Emperor', 'Cultural')],
    'GR': [('Acropolis, Athens', 'Cultural'), ('Meteora', 'Mixed'), ('Delphi', 'Cultural'), ('Mount Athos', 'Mixed')],
    'TR': [('Historic Areas of Istanbul', 'Cultural'), ('Göreme National Park', 'Mixed'), ('Ephesus', 'Cultural')],
    'IN': [('Taj Mahal', 'Cultural'), ('Agra Fort', 'Cultural'), ('Jaipur City', 'Cultural'), ('Hampi', 'Cultural')],
    'KE': [('Mount Kenya National Park', 'Natural'), ('Lake Turkana National Parks', 'Natural'), ('Lamu Old Town', 'Cultural')],
    'TZ': [('Serengeti National Park', 'Natural'), ('Kilimanjaro National Park', 'Natural'), ('Stone Town of Zanzibar', 'Cultural')],
    'PE': [('Historic Sanctuary of Machu Picchu', 'Mixed'), ('City of Cuzco', 'Cultural')],
    'BR': [('Iguaçu National Park', 'Natural'), ('Historic Town of Ouro Preto', 'Cultural'), ('Rio de Janeiro', 'Cultural')],
    'DE': [('Cologne Cathedral', 'Cultural'), ('Museum Island, Berlin', 'Cultural'), ('Wartburg Castle', 'Cultural')]
}

async def sync_unesco_sites(db: Session):
    """Sync UNESCO sites using static data fallback"""
    synced = 0
    
    # Process static data
    for iso, sites in UNESCO_DATA.items():
        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso).first()
        if not country: continue
        
        for name, category in sites:
            existing = db.query(models.Attraction).filter(
                models.Attraction.country_id == country.id,
                models.Attraction.name == name
            ).first()
            
            if not existing:
                db.add(models.Attraction(
                    country_id=country.id,
                    name=name,
                    category=category,
                    is_must_see=True,
                    is_unique=True
                ))
                synced += 1
    
    db.commit()
    logger.info(f"Synced {synced} UNESCO sites from static data")
    return {"status": "success", "synced": synced}
