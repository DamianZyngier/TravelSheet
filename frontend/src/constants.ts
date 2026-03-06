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
  NBP: { name: 'Narodowy Bank Polski', url: 'https://nbp.pl/' },
  NAGER: { name: 'Nager.Date', url: 'https://date.nager.at/' }
};

export const SAFETY_LABELS: Record<string, string> = {
  'low': 'Zachowaj zwykłą ostrożność',
  'medium': 'Zachowaj szczególną ostrożność',
  'high': 'Odradzane podróże (niekonieczne)',
  'critical': 'Odradzane wszelkie podróże',
  'unknown': 'Brak danych'
};

export const TRAVEL_TYPES: Record<string, { label: string; icon: string; desc: string }> = {
  "city_break": { "label": "City Break", "icon": "🏙️", "desc": "Krótkie wypady miejskie, zabytki i atmosfera." },
  "beaches": { "label": "Plaże i Relaks", "icon": "🏖️", "desc": "Słońce, morze i odpoczynek w resortach." },
  "nature": { "label": "Przyroda i Aventura", "icon": "🌋", "desc": "Dzikie krajobrazy, wędrówki i parki narodowe." },
  "food": { "label": "Świetne Jedzenie", "icon": "🍜", "desc": "Wyjazdy kulinarne, lokalne smaki i festiwale." },
  "history": { "label": "Historia i Kultura", "icon": "🏛️", "desc": "Odkrywanie zabytków i tradycji UNESCO." },
  "luxury": { "label": "Luksus i Wellness", "icon": "💎", "desc": "Podróże premium, spa i luksusowe hotele." },
  "events": { "label": "Festiwale i Eventy", "icon": "🎭", "desc": "Koncerty, karnawały i widowiska sportowe." },
  "eco": { "label": "Ekoturystyka", "icon": "🌿", "desc": "Zrównoważone podróże po rezerwatach." },
  "family": { "label": "Rodzina i Dzieci", "icon": "👨‍👩‍👧‍👦", "desc": "Atrakcje dla najmłodszych i parki rozrywki." }
};

export const PLUG_NAMES: Record<string, string> = {
    'A': 'Standard USA / Japonia',
    'B': 'Standard USA (z uziemieniem)',
    'C': 'Standard Europejski (płaska)',
    'D': 'Standard Indyjski',
    'E': 'Standard PL / Francuski',
    'F': 'Standard Niemiecki (Schuko)',
    'G': 'Standard Brytyjski (UK)',
    'H': 'Standard Izraelski',
    'I': 'Standard Australijski',
    'J': 'Standard Szwajcarski',
    'K': 'Standard Duński',
    'L': 'Standard Włoski',
    'M': 'Standard Afrykański',
    'N': 'Standard Brazylijski',
    'O': 'Standard Tajlandzki'
};

export const PLUG_IMAGES: Record<string, string> = {
    'A': 'https://upload.wikimedia.org/wikipedia/commons/5/5d/Socket_Type_A.jpg',
    'B': 'https://upload.wikimedia.org/wikipedia/commons/d/df/Socket_Type_B.jpg',
    'C': 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Socket_Type_C.jpg',
    'D': 'https://upload.wikimedia.org/wikipedia/commons/d/d4/Socket_Type_D.jpg',
    'E': 'https://upload.wikimedia.org/wikipedia/commons/5/5d/Socket_Type_E.jpg',
    'F': 'https://upload.wikimedia.org/wikipedia/commons/6/69/Socket_Type_F.jpg',
    'G': 'https://upload.wikimedia.org/wikipedia/commons/a/ad/Socket_Type_G.jpg',
    'H': 'https://upload.wikimedia.org/wikipedia/commons/2/28/Socket_Type_H.jpg',
    'I': 'https://upload.wikimedia.org/wikipedia/commons/8/84/Socket_Type_I.jpg',
    'J': 'https://upload.wikimedia.org/wikipedia/commons/1/13/Socket_Type_J.jpg',
    'K': 'https://upload.wikimedia.org/wikipedia/commons/5/5c/Socket_Type_K.jpg',
    'L': 'https://upload.wikimedia.org/wikipedia/commons/1/10/Socket_Type_L.jpg',
    'M': 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Socket_Type_M.jpg',
    'N': 'https://upload.wikimedia.org/wikipedia/commons/1/11/Socket_Type_N.jpg',
    'O': 'https://upload.wikimedia.org/wikipedia/commons/1/19/Socket_Type_O.jpg'
};

export const SECTIONS = [
  // 1. Przygotowanie i Formalności
  { id: 'docs', label: 'Dokumenty wjazdowe', icon: '🛂', category: 'Przygotowanie i Formalności' },
  { id: 'currency', label: 'Waluta i płatności', icon: '💰', category: 'Przygotowanie i Formalności' },
  { id: 'embassies', label: 'Ambasady i konsulaty', icon: '🏢', category: 'Przygotowanie i Formalności' },

  // 2. Zdrowie i Bezpieczeństwo
  { id: 'health', label: 'Zdrowie i szczepienia', icon: '💉', category: 'Zdrowie i Bezpieczeństwo' },
  { id: 'safety', label: 'Bezpieczeństwo MSZ', icon: '🛡️', category: 'Zdrowie i Bezpieczeństwo' },
  { id: 'water', label: 'Woda i higiena', icon: '🚰', category: 'Zdrowie i Bezpieczeństwo' },

  // 3. Praktyczne Codzienne
  { id: 'weather-forecast', label: 'Pogoda i prognoza', icon: '🌦️', category: 'Informacje Praktyczne' },
  { id: 'plugs', label: 'Prąd i gniazdka', icon: '🔌', category: 'Informacje Praktyczne' },
  { id: 'emergency', label: 'Numery alarmowe', icon: '🚨', category: 'Informacje Praktyczne' },
  { id: 'costs', label: 'Koszty i ceny', icon: '📊', category: 'Informacje Praktyczne' },

  // 4. Warunki Środowiskowe
  { id: 'climate', label: 'Klimat i pogoda', icon: '🌤️', category: 'Warunki Środowiskowe' },
  { id: 'holidays', label: 'Święta i dni wolne', icon: '📅', category: 'Warunki Środowiskowe' },

  // 5. Kultura i Atrakcje
  { id: 'law', label: 'Prawo i zwyczaje', icon: '⚖️', category: 'Kultura i Atrakcje' },
  { id: 'unesco', label: 'Zabytki UNESCO', icon: '🏛️', category: 'Kultura i Atrakcje' },

  // 0. Podsumowanie (Merged category)
  { id: 'summary', label: 'Podsumowanie kraju', icon: '📝', category: 'Podsumowanie' },
  { id: 'discover', label: 'Atrakcje i klimat', icon: '✨', category: 'Podsumowanie' },
  { id: 'info', label: 'Podstawowe fakty', icon: 'ℹ️', category: 'Podsumowanie' },
];

export const ALIASES: Record<string, string[]> = {
  'GB': ['wielka brytania', 'anglia', 'szkocja', 'uk', 'united kingdom'],
  'US': ['usa', 'stany zjednoczone', 'america', 'united states'],
  'PL': ['polska', 'poland'],
  'DE': ['niemcy', 'germany'],
  'FR': ['francja', 'france'],
  'IT': ['włochy', 'italy'],
  'ES': ['hiszpania', 'spain'],
  'TR': ['turcja', 'turkey'],
  'EG': ['egipt', 'egypt'],
  'TH': ['tajlandia', 'thailand'],
  'AE': ['dubaj', 'zjednoczone emiraty arabskie', 'emiraty', 'uae'],
  'LK': ['cejlon', 'sri lanka'],
  'MV': ['malediwy', 'maldives'],
  'SC': ['seszele', 'seychelles'],
  'MU': ['mauritius'],
  'TZ': ['zanzibar', 'tanzania'],
  'KE': ['kenia', 'kenya'],
  'DO': ['dominikana', 'dominican republic'],
  'MX': ['meksyk', 'mexico'],
  'CU': ['kuba', 'cuba'],
  'CV': ['wyspy zielonego przylądka', 'cape verde'],
  'PT': ['portugalia', 'madeira', 'madera', 'azory'],
  'GR': ['grecja', 'kreta', 'rodos', 'zakynthos', 'corfu'],
  'CY': ['cypr', 'cyprus'],
  'HR': ['chorwacja', 'croatia'],
  'ME': ['czarnogóra', 'montenegro'],
  'AL': ['albania'],
  'BG': ['bułgaria', 'bulgaria'],
  'RO': ['rumunia', 'romania'],
  'GE': ['gruzja', 'georgia'],
  'AM': ['armenia'],
  'JO': ['jordania', 'jordan'],
  'IL': ['izrael', 'israel'],
  'QA': ['katar', 'qatar'],
  'SA': ['arabia saudyjska', 'saudi arabia'],
  'OM': ['oman'],
  'MA': ['maroko', 'morocco'],
  'TN': ['tunezja', 'tunisia'],
  'ZA': ['rpa', 'south africa'],
  'IS': ['islandia', 'iceland'],
  'NO': ['norwegia', 'norway'],
  'SE': ['szwecja', 'sweden'],
  'FI': ['finlandia', 'finland'],
  'DK': ['dania', 'denmark'],
  'CH': ['szwajcaria', 'switzerland'],
  'AT': ['austria'],
  'NL': ['holandia', 'netherlands'],
  'BE': ['belgia', 'belgium'],
  'IE': ['irlandia', 'ireland'],
  'CZ': ['czechy', 'czech republic'],
  'SK': ['słowacja', 'slovakia'],
  'HU': ['węgry', 'hungary'],
  'UA': ['ukraina', 'ukraine'],
  'JP': ['japonia', 'japan'],
  'CN': ['chiny', 'china'],
  'KR': ['korea południowa', 'korea'],
  'VN': ['wietnam', 'vietnam'],
  'KH': ['kambodża', 'cambodia'],
  'LA': ['laos'],
  'ID': ['indonezja', 'bali', 'indonesia'],
  'MY': ['malezja', 'malaysia'],
  'SG': ['singapur', 'singapore'],
  'PH': ['filipiny', 'philippines'],
  'AU': ['australia'],
  'NZ': ['nowa zelandia', 'new zealand'],
  'CA': ['kanada', 'canada'],
  'BR': ['brazylia', 'brazil'],
  'AR': ['argentyna', 'argentina'],
  'CL': ['czile', 'chile'],
  'PE': ['peru'],
  'CO': ['kolumbia', 'colombia'],
  'CR': ['kostaryka', 'costa rica'],
  'PA': ['panama']
};
