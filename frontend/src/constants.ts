export const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json";

export const CONTINENT_MAP: Record<string, string> = {
  'Europe': 'Europa',
  'Asia': 'Azja',
  'Africa': 'Afryka',
  'North America': 'Ameryka Północna',
  'South America': 'Ameryka Południowa',
  'Oceania': 'Oceania',
  'Antarctica': 'Antarktyda'
};

export const DATA_SOURCES = {
  MSZ: { name: 'MSZ (gov.pl)', url: 'https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych' },
  REST: { name: 'REST Countries', url: 'https://restcountries.com/' },
  WIKI: { name: 'Wikipedia / Wikidata', url: 'https://www.wikipedia.org/' },
  UNESCO: { name: 'UNESCO', url: 'https://whc.unesco.org/' },
  CDC: { name: 'CDC Health', url: 'https://www.cdc.gov/' },
  OWM: { name: 'OpenWeatherMap', url: 'https://openweathermap.org/' },
  METEO: { name: 'Open-Meteo', url: 'https://open-meteo.com/' },
  NUMBEO: { name: 'Numbeo', url: 'https://www.numbeo.com/' },
  NAGER: { name: 'Nager.Date', url: 'https://date.nager.at/' }
};

export const SAFETY_LABELS: Record<string, string> = {
  'low': 'Bezpiecznie',
  'medium': 'Średnio bezpiecznie',
  'high': 'Niebezpiecznie',
  'critical': 'Bardzo niebezpiecznie',
  'unknown': 'Brak danych'
};

export const PLUG_IMAGES: Record<string, string> = {
    'A': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-A-100x100.jpg',
    'B': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-B-100x100.jpg',
    'C': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-C-100x100.jpg',
    'D': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-D-100x100.jpg',
    'E': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-E-100x100.jpg',
    'F': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-F-100x100.jpg',
    'G': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-G-100x100.jpg',
    'H': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-H-100x100.jpg',
    'I': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-I-100x100.jpg',
    'J': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-J-100x100.jpg',
    'K': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-K-100x100.jpg',
    'L': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-L-100x100.jpg',
    'M': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-M-100x100.jpg',
    'N': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-N-100x100.jpg',
    'O': 'https://www.worldstandards.eu/wp-content/uploads/electricity-tiles-type-O-100x100.jpg'
};

export const SECTIONS = [
  { id: 'summary', label: 'Podsumowanie', icon: '📝' },
  { id: 'discover', label: 'Poznaj kraj', icon: '✨' },
  { id: 'docs', label: 'Dokumenty', icon: '🛂' },
  { id: 'info', label: 'Informacje', icon: 'ℹ️' },
  { id: 'currency', label: 'Waluta', icon: '💰' },
  { id: 'plugs', label: 'Gniazdka', icon: '🔌' },
  { id: 'emergency', label: 'Telefony', icon: '🚨' },
  { id: 'costs', label: 'Ceny', icon: '📊' },
  { id: 'climate', label: 'Pogoda', icon: '🌤️' },
  { id: 'health', label: 'Zdrowie', icon: '💉' },
  { id: 'holidays', label: 'Święta', icon: '📅' },
  { id: 'embassies', label: 'Ambasady', icon: '🏢' },
  { id: 'attractions', label: 'Atrakcje', icon: '📍' },
  { id: 'unesco', label: 'Lista UNESCO', icon: '🏛️' },
  { id: 'safety', label: 'Bezpieczeństwo', icon: '🛡️' },
];
