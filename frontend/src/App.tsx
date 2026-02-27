import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps"
import logoNoText from './assets/logo-no-text.png'
import './App.css'

// URL do topologii świata
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"

const CONTINENT_MAP: Record<string, string> = {
  'Europe': 'Europa',
  'Asia': 'Azja',
  'Africa': 'Afryka',
  'North America': 'Ameryka Północna',
  'South America': 'Ameryka Południowa',
  'Oceania': 'Oceania',
  'Antarctica': 'Antarktyda'
};

const DATA_SOURCES = {
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

function DataSource({ sources }: { sources: (keyof typeof DATA_SOURCES)[] }) {
  return (
    <div className="data-source-footer">
      <span>Źródło: </span>
      {sources.map((s, i) => (
        <span key={s}>
          <a href={DATA_SOURCES[s].url} target="_blank" rel="noopener noreferrer" className="data-source-link">
            {DATA_SOURCES[s].name}
          </a>
          {i < sources.length - 1 ? ', ' : ''}
        </span>
      ))}
    </div>
  );
}

interface CountryData {
  name: string;
  name_pl: string;
  iso2: string;
  iso3: string;
  capital: string;
  continent: string;
  flag_emoji: string;
  flag_url: string;
  latitude: number | null;
  longitude: number | null;
  unesco_count: number;
  timezone: string | null;
  national_dish: string | null;
  wiki_summary: string | null;
  national_symbols: string | null;
  population: number | null;
  area: number | null;
  phone_code: string | null;
  largest_cities: string | null;
  ethnic_groups: string | null;
  religions: { name: string; percentage: number }[];
  languages: { name: string; is_official: boolean }[];
  safety: {
    risk_level: string;
    risk_text: string;
    risk_details: string;
    url: string;
  };
  currency: {
    code: string;
    name: string;
    rate_pln: number | null;
  };
  practical: {
    plug_types: string;
    driving_side: string;
    water_safe: boolean | null;
    emergency?: {
      police: string | null;
      ambulance: string | null;
      fire: string | null;
      dispatch: string | null;
      member_112?: boolean;
    } | null;
    vaccinations_required: string;
    vaccinations_suggested: string;
    health_info: string;
    roaming_info: string;
    license_type: string;
  };
  costs?: {
    index: number | null;
    restaurants: number | null;
    groceries: number | null;
    transport: number | null;
    accommodation: number | null;
    ratio_to_pl: number | null;
  };
  embassies?: {
    type: string;
    city: string;
    address: string;
    phone: string;
    email: string;
    website: string;
  }[];
  entry?: {
    visa_required: boolean | null;
    visa_status: string;
    passport_required: boolean | null;
    temp_passport_allowed: boolean | null;
    id_card_allowed: boolean | null;
    visa_notes: string;
  };
  holidays?: {
    name: string;
    date: string;
  }[];
  attractions?: {
    name: string;
    category: string;
    description?: string;
  }[];
  unesco_places?: {
    name: string;
    category: string;
    is_danger?: boolean;
    is_transnational?: boolean;
    unesco_id?: string;
    image_url?: string;
    description?: string;
  }[];
  climate?: {
    month: number;
    temp_day: number;
    temp_night: number;
    rain: number;
  }[];
  weather?: {
    temp: number | null;
    condition: string;
    icon: string;
  };
}

const getLongNameClass = (name: string, type: 'h3' | 'h2') => {
  if (type === 'h3') {
    if (name.length > 25) return 'font-very-small';
    if (name.length > 18) return 'font-small';
  } else {
    if (name.length > 30) return 'font-very-small';
    if (name.length > 20) return 'font-small';
  }
  return '';
};

function LinkifyOdyseusz({ text }: { text: string }) {
  if (!text) return null;
  
  // Regex to find "systemie Odyseusz" (ignoring case and potential non-breaking spaces)
  const parts = text.split(/(systemie\s+Odyseusz|systemie Odyseusz)/gi);
  
  return (
    <>
      {parts.map((part, i) => {
        if (part.toLowerCase().includes('systemie') && part.toLowerCase().includes('odyseusz')) {
          return (
            <a 
              key={i} 
              href="https://odyseusz.msz.gov.pl" 
              target="_blank" 
              rel="noopener noreferrer"
              className="odyseusz-link"
              style={{ color: 'inherit', textDecoration: 'underline', fontWeight: 'bold' }}
            >
              {part}
            </a>
          );
        }
        return part;
      })}
    </>
  );
}

function ExpandableText({ text }: { text: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (textRef.current) {
      const { scrollHeight, clientHeight } = textRef.current;
      setHasMore(scrollHeight > clientHeight);
    }
  }, [text]);

  if (!text) return null;

  return (
    <div className={`expandable-text-container ${isExpanded ? 'expanded' : ''}`}>
      <div 
        ref={textRef}
        className="risk-details-text line-clamp"
      >
        <LinkifyOdyseusz text={text} />
      </div>
      {hasMore && (
        <button 
          className="show-more-btn" 
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? 'Pokaż mniej' : 'Pokaż więcej'}
        </button>
      )}
    </div>
  );
}

function App() {
  const [countries, setCountries] = useState<Record<string, CountryData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<CountryData | null>(null);
  
  const [filterSafety, setFilterSafety] = useState<string>('all');
  const [filterContinent, setFilterContinent] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  const [mapPosition, setMapPosition] = useState({ coordinates: [0, 0] as [number, number], zoom: 1 });
  const [chartTooltip, setChartTooltip] = useState<{ x: number, y: number, text: string, visible: boolean }>({ x: 0, y: 0, text: '', visible: false });
  const [activeSection, setActiveSection] = useState('summary');
  const [isUnescoExpanded, setIsUnescoExpanded] = useState(false);
  const [isEmbassiesExpanded, setIsEmbassiesExpanded] = useState(false);
  
  const searchInputRef = useRef<HTMLInputElement>(null);

  const SECTIONS = [
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

  // Intersection Observer for ScrollSpy
  useEffect(() => {
    if (!selectedCountry) return;

    const sectionStates = new Map<string, IntersectionObserverEntry>();

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        sectionStates.set(entry.target.id, entry);
      });

      const intersecting = Array.from(sectionStates.values())
        .filter(e => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

      if (intersecting.length > 0) {
        const bestCandidate = intersecting.find(e => e.boundingClientRect.top < 300) || intersecting[0];
        setActiveSection(bestCandidate.target.id);
      }
    }, { 
      threshold: [0, 0.1, 0.2, 0.5], 
      rootMargin: '-80px 0px -60% 0px' 
    });

    SECTIONS.forEach(section => {
      const el = document.getElementById(section.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [selectedCountry]);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Update URL hash without jumping
      window.history.replaceState(null, '', `#${id}`);
    }
  };

  // Handle initial anchor on load or country change
  useEffect(() => {
    if (selectedCountry && window.location.hash) {
      const id = window.location.hash.substring(1);
      // Small delay to ensure DOM is fully rendered
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) {
          el.scrollIntoView({ behavior: 'auto', block: 'start' });
          setActiveSection(id);
        }
      }, 100);
    }
  }, [selectedCountry]);

  const SAFETY_LABELS: Record<string, string> = {
    'low': 'Bezpiecznie',
    'medium': 'Średnio bezpiecznie',
    'high': 'Niebezpiecznie',
    'critical': 'Bardzo niebezpiecznie',
    'unknown': 'Brak danych'
  };

  const formatPLN = (value: number | null) => {
    if (value === null) return 'brak danych';
    return value.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 4 }) + ' PLN';
  };

  const getCurrencyExample = (country: CountryData) => {
    const rate = country.currency.rate_pln;
    if (!rate) return null;
    if (rate < 0.1) {
      const exampleValue = 1000;
      const plnValue = exampleValue * rate;
      return `(1000 ${country.currency.code} ≈ ${formatPLN(plnValue)})`;
    }
    return null;
  };

  const checkPlugs = (types: string | null) => {
    if (!types) return { text: 'Brak danych o gniazdkach', class: 'plugs-none', warning: false };
    const plugList = types.split(',').map(t => t.trim().toUpperCase());
    const isSameAsPoland = plugList.every(t => ['C', 'E', 'F'].includes(t));
    const hasPolishCompatible = plugList.some(t => ['C', 'E', 'F'].includes(t));
    
    if (isSameAsPoland) return { text: 'Takie same jak w Polsce', class: 'plugs-ok', warning: false };
    if (hasPolishCompatible) return { text: 'Podobne / częściowo zgodne', class: 'plugs-warn', warning: false };
    return { text: 'Inne - wymagany adapter', class: 'plugs-err', warning: true };
  };

  const PLUG_IMAGES: Record<string, string> = {
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

  const getEnlargedPlugUrl = (url: string) => url.replace('100x100', '500x500');

  useEffect(() => {
    fetch('./data.json')
      .then(res => {
        if (!res.ok) throw new Error('Błąd pobierania danych');
        return res.json();
      })
      .then(data => {
        setCountries(data);
        setLoading(false);
        
        const params = new URLSearchParams(window.location.search);
        const countryCode = params.get('kraj');
        if (countryCode && data[countryCode.toUpperCase()]) {
          const country = data[countryCode.toUpperCase()];
          setSelectedCountry(country);
          
          if (country.longitude !== null && country.latitude !== null) {
            const { zoom } = getMapSettings(country);
            setMapPosition({ 
              coordinates: [country.longitude, country.latitude], 
              zoom: zoom
            });
          }
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Sync state with URL on back/forward
  useEffect(() => {
    if (Object.keys(countries).length === 0) return;

    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const countryCode = params.get('kraj');
      
      if (countryCode && countries[countryCode.toUpperCase()]) {
        handleSelectCountry(countries[countryCode.toUpperCase()], true);
      } else {
        handleSelectCountry(null, true);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [countries]);

  // Reset scroll to top and update document title when country selection changes
  useEffect(() => {
    if (selectedCountry) {
      window.scrollTo(0, 0);
      document.title = `TripSheet - ${selectedCountry.name_pl}`;
    } else {
      document.title = 'TripSheet';
    }
  }, [selectedCountry]);

  const getMapSettings = (country: CountryData) => {
    const huge = ['RU', 'CA', 'US', 'CN', 'BR', 'AU', 'IN', 'AR', 'KZ', 'DZ'];
    const large = ['SA', 'MX', 'ID', 'SD', 'LY', 'MN', 'TD', 'PE', 'NE', 'AO', 'CO', 'ZA', 'ML', 'ET', 'BO', 'MR', 'EG', 'TR', 'PL', 'UA', 'FR', 'DE', 'ES', 'SE', 'NO'];
    const tiny = [
      'AD', 'MO', 'SM', 'LI', 'VA', 'MT', 'SG', 'HK', 'LU', 'MC', 'MS', 'GI', 'TC', 'VG', 'AI', 'BM', 'AW', 'SX', 'BQ', 'CW', 'PF', 'NC', 'WF', 'YT', 'RE', 'BL', 'MF', 'PM', 'FK', 'SH', 'PN', 'GS', 'IO', 'TF', 'HM', 'BV', 'CV', 'ST', 'SC', 'MU', 'KM', 'MV', 'LS', 'SZ', 'BH', 'BB', 'DM', 'GD', 'KN', 'LC', 'VC', 'AG', 'BS', 'PW', 'MH', 'FM', 'NR', 'KI', 'TO', 'WS', 'TV', 'VU'
    ];

    let zoom = 10;
    let showDot = false;

    if (country.iso2 === 'AU') {
      zoom = 2.5; // Australia needs wider view
    } else if (country.iso2 === 'NZ') {
      zoom = 8; // NZ needs slightly more context
    } else if (huge.includes(country.iso2)) {
      zoom = 2.5;
    } else if (large.includes(country.iso2)) {
      zoom = 5;
    } else if (tiny.includes(country.iso2)) {
      zoom = 25;
      showDot = true;
    }

    return { zoom, showDot };
  };

  const handleSelectCountry = useCallback((country: CountryData | null, skipHistory: boolean = false) => {
    setSelectedCountry(country);
    setIsUnescoExpanded(false);
    
    if (country && country.longitude !== null && country.latitude !== null) {
      const { zoom } = getMapSettings(country);
      setMapPosition({ 
        coordinates: [country.longitude, country.latitude], 
        zoom: zoom
      });
    } else {
      setMapPosition({ coordinates: [0, 0], zoom: 1 });
    }

    if (!skipHistory) {
      const url = new URL(window.location.href);
      if (country) {
        url.searchParams.set('kraj', country.iso2);
      } else {
        url.searchParams.delete('kraj');
        url.hash = ''; // Clear hash when returning to list
      }
      window.history.pushState({}, '', url.toString());
    }
  }, [countries]); // Dependencies for callback

  const continents = useMemo(() => {
    const set = new Set(Object.values(countries).map(c => c.continent).filter(Boolean));
    return Array.from(set).sort();
  }, [countries]);

  const countryList = useMemo(() => {
    const ALIASES: Record<string, string[]> = {
      'US': ['usa', 'stany', 'ameryka'],
      'GB': ['uk', 'anglia', 'wielka brytania', 'brytania'],
      'DE': ['niemcy', 'deutschland'],
      'PL': ['polska', 'poland'],
      'AE': ['zea', 'emiraty'],
      'NL': ['holandia'],
    };

    return Object.values(countries)
      .filter(c => {
        const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
        const matchContinent = filterContinent === 'all' || c.continent === filterContinent;
        
        const searchLower = searchQuery.toLowerCase();
        const countryAliases = ALIASES[c.iso2] || [];
        
        const matchSearch = c.name_pl.toLowerCase().includes(searchLower) || 
                            c.name.toLowerCase().includes(searchLower) ||
                            c.iso2.toLowerCase().includes(searchLower) ||
                            c.iso3.toLowerCase().includes(searchLower) ||
                            countryAliases.some(alias => alias.includes(searchLower));
        
        return matchSafety && matchContinent && matchSearch;
      })
      .sort((a, b) => a.name_pl.localeCompare(b.name_pl, 'pl'));
  }, [countries, filterSafety, filterContinent, searchQuery]);

  const sortedFullList = useMemo(() => {
    return Object.values(countries).sort((a, b) => a.name_pl.localeCompare(b.name_pl, 'pl'));
  }, [countries]);

  const navigateCountry = (direction: 'prev' | 'next') => {
    const list = sortedFullList;
    const currentIndex = list.findIndex(c => c.iso2 === selectedCountry?.iso2);
    if (currentIndex === -1) return;

    let nextIndex;
    if (direction === 'prev') {
      nextIndex = currentIndex > 0 ? currentIndex - 1 : list.length - 1;
    } else {
      nextIndex = currentIndex < list.length - 1 ? currentIndex + 1 : 0;
    }

    handleSelectCountry(list[nextIndex]);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }

      if (e.key === 'Backspace' && selectedCountry) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          handleSelectCountry(null);
        }
      }

      if (e.key === 'Enter' && !selectedCountry && countryList.length === 1) {
        handleSelectCountry(countryList[0]);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedCountry, countryList, handleSelectCountry]);

  if (loading) return <div className="loader">Ładowanie danych podróżniczych...</div>;

  return (
    <div className="app-container" onContextMenu={() => true}>
      {error && <div className="error-toast">{error}</div>}
      
      {!selectedCountry ? (
        <>
          <header className="main-header">
            <div className="header-content">
              <div className="logo-section" onClick={() => handleSelectCountry(null)} style={{ cursor: 'pointer' }}>
                <img src={logoNoText} alt="TripSheet" className="app-logo" />
                <div className="logo-text">
                  <span className="logo-brand">TripSheet</span>
                  <p>Twoje centrum bezpiecznych podróży</p>
                </div>
              </div>
              
              <div className="controls-section">
                <div className="search-container">
                  <input 
                    ref={searchInputRef}
                    type="text" 
                    placeholder="Szukaj kraju..." 
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                  {searchQuery && (
                    <button 
                      className="clear-input-btn" 
                      onClick={() => setSearchQuery('')}
                      title="Wyczyść szukanie"
                    >
                      ✕
                    </button>
                  )}
                </div>
                
                <div className="filter-group">
                  <select value={filterContinent} onChange={e => setFilterContinent(e.target.value)}>
                    <option value="all">Wszystkie kontynenty</option>
                    {continents.map(c => <option key={c} value={c}>{CONTINENT_MAP[c] || c}</option>)}
                  </select>
                </div>

                <div className="filter-group">
                  <select value={filterSafety} onChange={e => setFilterSafety(e.target.value)}>
                    <option value="all">Wszystkie poziomy bezpieczeństwa</option>
                    <option value="low">Bezpiecznie</option>
                    <option value="medium">Średnio bezpiecznie</option>
                    <option value="high">Niebezpiecznie</option>
                    <option value="critical">Bardzo niebezpiecznie</option>
                  </select>
                </div>
              </div>
            </div>
          </header>

          <main className="content-area">
            <div className="country-grid">
              {countryList.length > 0 ? (
                countryList.map(country => (
                  <div 
                    key={country.iso2} 
                    className={`country-card risk-border-${country.safety.risk_level}`}
                    onClick={() => handleSelectCountry(country)}
                  >
                    <div className="card-content">
                      <img 
                        src={country.flag_url} 
                        alt={`Flaga ${country.name_pl}`} 
                        className="main-flag-img" 
                        style={{ objectFit: 'contain' }}
                      />
                      <h3 className={getLongNameClass(country.name_pl, 'h3')}>{country.name_pl}</h3>
                      <p className="card-continent">{CONTINENT_MAP[country.continent] || country.continent}</p>
                      <span className={`risk-badge risk-${country.safety.risk_level}`}>
                        {SAFETY_LABELS[country.safety.risk_level] || country.safety.risk_level}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-results">Nie znaleziono krajów spełniających kryteria.</div>
              )}
            </div>
          </main>
        </>
      ) : (
        <div className="detail-view-layout">
          <aside className="side-menu">
            <button className="side-back-button" onClick={() => handleSelectCountry(null)}>
              ← Powrót do listy
            </button>

            {(() => {
              const list = sortedFullList;
              const currentIndex = list.findIndex(c => c.iso2 === selectedCountry?.iso2);
              const prevCountry = currentIndex > 0 ? list[currentIndex - 1] : list[list.length - 1];
              const nextCountry = currentIndex < list.length - 1 ? list[currentIndex + 1] : list[0];

              return (
                <div className="country-navigation">
                  <button className="nav-button prev" onClick={() => navigateCountry('prev')}>
                    <img src={prevCountry?.flag_url} alt="" className="nav-flag" />
                    <div className="nav-info">
                      <span className="nav-label">Poprzedni</span>
                      <span className={`nav-name ${getLongNameClass(prevCountry?.name_pl || '', 'h3')}`}>{prevCountry?.name_pl}</span>
                    </div>
                    <span className="nav-arrow">←</span>
                  </button>
                  <button className="nav-button next" onClick={() => navigateCountry('next')}>
                    <span className="nav-arrow">→</span>
                    <div className="nav-info">
                      <span className="nav-label">Następny</span>
                      <span className={`nav-name ${getLongNameClass(nextCountry?.name_pl || '', 'h3')}`}>{nextCountry?.name_pl}</span>
                    </div>
                    <img src={nextCountry?.flag_url} alt="" className="nav-flag" />
                  </button>
                </div>
              );
            })()}

            <div className="side-menu-list">
              {SECTIONS.map(s => {
                return (
                  <button 
                    key={s.id}
                    className={`side-menu-item ${activeSection === s.id ? 'active' : ''}`}
                    onClick={() => scrollToSection(s.id)}
                  >
                    <span className="side-menu-icon">{s.icon}</span>
                    <span className="side-menu-label">{s.label}</span>
                  </button>
                )
              })}
            </div>
          </aside>

          <div className="detail-view-content">
            <div className="detail-card">
              <div id="summary" className="detail-header scroll-mt">
                <img 
                  src={selectedCountry.flag_url} 
                  alt={`Flaga ${selectedCountry.name_pl}`} 
                  className="detail-flag-img" 
                  style={{ objectFit: 'contain' }}
                />
                <div className="detail-titles">
                  <h2 className={getLongNameClass(selectedCountry.name_pl, 'h2')}>{selectedCountry.name_pl}</h2>
                  <p>{selectedCountry.name} ({selectedCountry.iso2})</p>
                </div>
                
                <div className="detail-map-container">
                  <ComposableMap 
                    key={selectedCountry.iso2}
                    projection="geoMercator"
                    projectionConfig={{ 
                      scale: 100
                    }}
                    style={{ width: "100%", height: "100%" }}
                  >
                    <ZoomableGroup
                      center={mapPosition.coordinates}
                      zoom={mapPosition.zoom}
                      maxZoom={40}
                      onMoveEnd={(pos) => setMapPosition(pos)}
                    >
                      <Geographies geography={geoUrl}>
                        {({ geographies }) =>
                          geographies.map((geo: any) => {
                            const isSelected = 
                              geo.id === selectedCountry.iso3 || 
                              geo.properties?.iso_a3 === selectedCountry.iso3 ||
                              geo.properties?.ADM0_A3 === selectedCountry.iso3 ||
                              geo.properties?.GU_A3 === selectedCountry.iso3 ||
                              geo.properties?.name === selectedCountry.name ||
                              (selectedCountry.iso3 === "CIV" && (geo.properties?.name === "Côte d'Ivoire" || geo.properties?.name === "Cote d'Ivoire")) ||
                              (selectedCountry.iso3 === "USA" && (geo.id === "USA" || geo.properties?.name === "United States of America"));
                            
                            return (
                              <Geography
                                key={geo.rsmKey}
                                geography={geo}
                                fill={isSelected ? "#2b6cb0" : "#EAEAEC"}
                                stroke={isSelected ? "#2b6cb0" : "#D6D6DA"}
                                strokeWidth={0.5}
                                style={{
                                  default: { outline: "none" },
                                  hover: { outline: "none" },
                                  pressed: { outline: "none" },
                                }}
                              />
                            );
                          })
                        }
                      </Geographies>
                      
                      {selectedCountry.longitude !== null && selectedCountry.latitude !== null && getMapSettings(selectedCountry).showDot && (
                        <Marker coordinates={[selectedCountry.longitude, selectedCountry.latitude]}>
                          <circle r={0.1} fill="none" stroke="#fff" strokeWidth={20} vectorEffect="non-scaling-stroke" />
                          <circle r={0.1} fill="none" stroke="#F56565" strokeWidth={14} vectorEffect="non-scaling-stroke" />
                        </Marker>
                      )}
                    </ZoomableGroup>
                  </ComposableMap>
                  
                  <div className="map-controls">
                    <button onClick={() => setMapPosition(prev => ({ ...prev, zoom: Math.min(prev.zoom * 1.5, 40) }))}>+</button>
                    <button onClick={() => setMapPosition(prev => ({ ...prev, zoom: Math.max(prev.zoom / 1.5, 1) }))}>-</button>
                    <button onClick={() => setMapPosition({ coordinates: [selectedCountry.longitude || 0, selectedCountry.latitude || 0], zoom: getMapSettings(selectedCountry).zoom })}>🎯</button>
                  </div>
                </div>
              </div>

                                                  <div className="detail-body">
                                                    <div id="discover" className="info-block full-width scroll-mt">
                                                      <div className="section-header">
                                                        <span className="section-header-icon">✨</span>
                                                        <label>Odkryj i poznaj {selectedCountry.name_pl}</label>
                                                      </div>
                                                      
                                                                            <div className="discover-section">
                                                                              <div className="discover-container">
                                                                                {selectedCountry.wiki_summary ? (
                                                                                  <div className="wiki-summary-text">
                                                                                    <ExpandableText text={selectedCountry.wiki_summary} />
                                                                                  </div>
                                                                                ) : (
                                                                                  <p className="no-data-text">Brak dostępnego opisu dla tego kraju.</p>
                                                                                )}
                                                                                {selectedCountry.national_symbols && (
                                                      
                                                            <div className="national-symbols-bar">
                                                              <span className="symbols-label">Symbole narodowe:</span>
                                                              <span className="symbols-value">{selectedCountry.national_symbols}</span>
                                                            </div>
                                                          )}
                                                          <DataSource sources={['WIKI', 'UNESCO']} />
                                                        </div>
                                                      </div>
                                                    </div>
                                      
              
                            <div className="info-grid">
              
                  <div className="info-block">
                    <label>Kontynent</label>
                    <span>{CONTINENT_MAP[selectedCountry.continent] || selectedCountry.continent}</span>
                  </div>
                  <div className="info-block">
                    <label>Stolica</label>
                    <span>{selectedCountry.capital || 'Brak danych'}</span>
                  </div>
                  
                  {selectedCountry.weather?.temp !== null && (
                    <div className="info-block weather-top-block">
                      <label>Pogoda teraz</label>
                      <div className="weather-brief">
                        {selectedCountry.weather?.icon && (
                          <img 
                            src={`https://openweathermap.org/img/wn/${selectedCountry.weather.icon}.png`} 
                            alt={selectedCountry.weather.condition} 
                            className="weather-mini-icon"
                          />
                        )}
                        <span className="weather-temp-main">{Math.round(selectedCountry.weather?.temp || 0)}°C</span>
                      </div>
                    </div>
                  )}

                  {selectedCountry.timezone && (
                    <div className="info-block">
                      <label>Strefa czasowa</label>
                      <span>{selectedCountry.timezone}</span>
                    </div>
                  )}

                  {selectedCountry.national_dish && (
                    <div className="info-block">
                      <label>Potrawa narodowa</label>
                      <span>🍽️ {selectedCountry.national_dish}</span>
                    </div>
                  )}

                  <div className="info-block">
                    <label>Ruch drogowy</label>
                    <div className="driving-info-box">
                      <span>{selectedCountry.practical.driving_side === 'right' ? '➡️ Prawostronny' : '⬅️ Lewostronny'}</span>
                      <span className="license-info">🚗 {selectedCountry.practical.license_type || 'Polskie / IDP'}</span>
                    </div>
                  </div>
                  
                  <div id="docs" className="info-block full-width docs-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">🛂</span>
                      <label>Wymagane dokumenty (dla Polaków)</label>
                    </div>
                    <div className="docs-grid">
                      <div className={`doc-item ${selectedCountry.entry?.passport_required ? 'doc-yes' : 'doc-no'}`}>
                        <strong>Paszport</strong>
                        <span>{selectedCountry.entry?.passport_required ? '✅ TAK' : '❌ NIE'}</span>
                      </div>
                      <div className={`doc-item ${selectedCountry.entry?.temp_passport_allowed ? 'doc-yes' : 'doc-no'}`}>
                        <strong>Paszport tymczasowy</strong>
                        <span>{selectedCountry.entry?.temp_passport_allowed ? '✅ TAK' : '❌ NIE'}</span>
                      </div>
                      <div className={`doc-item ${selectedCountry.entry?.id_card_allowed ? 'doc-yes' : 'doc-no'}`}>
                        <strong>Dowód osobisty</strong>
                        <span>{selectedCountry.entry?.id_card_allowed ? '✅ TAK' : '❌ NIE'}</span>
                      </div>
                                          <div className={`doc-item ${selectedCountry.entry?.visa_required ? 'doc-no' : 'doc-yes'}`}>
                                            <strong>Wiza turystyczna</strong>
                                            <span>
                                              {selectedCountry.entry?.visa_status === 'Wiza niepotrzebna' ? '✅ NIEPOTRZEBNA' : 
                                               selectedCountry.entry?.visa_status ? `🛂 ${selectedCountry.entry.visa_status.toUpperCase()}` : 
                                               selectedCountry.entry?.visa_required ? '🛂 WYMAGANA' : '🆓 NIEPOTRZEBNA'}
                                            </span>
                                          </div>
                      
                    </div>
                    <DataSource sources={['MSZ', 'WIKI']} />
                  </div>

                  <div id="info" className="info-block full-width basic-info-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">ℹ️</span>
                      <label>Podstawowe informacje</label>
                    </div>
                    <div className="basic-info-grid">
                      <div className="info-item-box">
                        <strong>Ludność:</strong>
                        <span>{selectedCountry.population?.toLocaleString() || 'Brak danych'}</span>
                      </div>
                      <div className="info-item-box">
                        <strong>Gęstość zaludnienia:</strong>
                        <span>
                          {selectedCountry.population && selectedCountry.area ? (
                            <>
                              {(selectedCountry.population / selectedCountry.area).toFixed(1)} os./km²
                              {(() => {
                                const density = selectedCountry.population / selectedCountry.area;
                                const polandDensity = 120; 
                                const ratio = density / polandDensity;
                                if (ratio > 1.1) {
                                  return <span style={{ color: '#f56565', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                                    ({ratio.toFixed(1)}x gęściej)
                                  </span>;
                                } else if (ratio < 0.9) {
                                  return <span style={{ color: '#48bb78', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                                    ({(1/ratio).toFixed(1)}x rzadziej)
                                  </span>;
                                } else {
                                  return <span style={{ color: '#4299e1', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                                    (podobnie)
                                  </span>;
                                }
                              })()}
                            </>
                          ) : 'Brak danych'}
                        </span>
                      </div>
                      <div className="info-item-box">
                        <strong>Języki:</strong>
                        <span>{selectedCountry.languages?.length > 0 ? selectedCountry.languages.map(l => l.name + (l.is_official ? ' (ofic.)' : '')).join(', ') : 'Brak danych'}</span>
                      </div>
                      <div className="info-item-box">
                        <strong>Nr kierunkowy:</strong>
                        <span>{selectedCountry.phone_code ? `+${selectedCountry.phone_code.replace('+', '')}` : 'Brak danych'}</span>
                      </div>
                      {selectedCountry.largest_cities && (
                        <div className="info-item-box full">
                          <strong>Największe miasta:</strong>
                          <span>{selectedCountry.largest_cities}</span>
                        </div>
                      )}
                      {selectedCountry.ethnic_groups && (
                        <div className="info-item-box full">
                          <strong>Grupy etniczne:</strong>
                          <span>{selectedCountry.ethnic_groups}</span>
                        </div>
                      )}
                      {selectedCountry.religions?.length > 0 && (
                        <div className="info-item-box full">
                          <strong>Religie:</strong>
                          <div className="religion-badges">
                            {selectedCountry.religions.sort((a,b) => b.percentage - a.percentage).map((r, i) => (
                              <span key={i} className="religion-badge">
                                {r.name}: <strong>{r.percentage.toFixed(1)}%</strong>
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="info-item-box full" style={{ backgroundColor: '#ebf8ff', border: '1px solid #bee3f8' }}>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                          <span style={{ fontSize: '1.25rem' }}>🛡️</span>
                          <div>
                            <strong style={{ color: '#2b6cb0', fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>System Odyseusz:</strong>
                            <span style={{ fontSize: '0.85rem', color: '#2c5282', lineHeight: '1.4' }}>
                              MSZ zaleca rejestrację podróży w <a href="https://odyseusz.msz.gov.pl" target="_blank" rel="noopener noreferrer" style={{ fontWeight: '700', textDecoration: 'underline' }}>systemie Odyseusz</a>. Pozwoli to służbom konsularnym na kontakt i pomoc w sytuacjach kryzysowych.
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <DataSource sources={['REST', 'WIKI', 'CDC']} />
                  </div>

                  <div id="currency" className="info-block full-width scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">💰</span>
                      <label>Waluta</label>
                    </div>
                    <span>
                                                        {selectedCountry.currency.name || 'Brak danych'} {selectedCountry.currency.code && `(${selectedCountry.currency.code})`} <br/>
                                                        {selectedCountry.currency.rate_pln ? (
                                                          <>
                                                            1 {selectedCountry.currency.code} = {formatPLN(selectedCountry.currency.rate_pln)}
                                                            <br/>
                                                            <small style={{ color: '#718096' }}>{getCurrencyExample(selectedCountry)}</small>
                                                          </>
                                                        ) : 'brak danych o kursie'}
                                                      </span>
                                                      <DataSource sources={['REST', 'WIKI']} />
                                                    </div>
                  <div id="plugs" className="info-block full-width scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">🔌</span>
                      <label>Gniazdka elektryczne</label>
                    </div>
                    <div className="plugs-container">
                      <div className="plug-types-list">
                        {selectedCountry.practical.plug_types ? selectedCountry.practical.plug_types.split(',').map(type => (
                          <div key={type} className="plug-icon-box">
                            <span className="plug-letter">Typ {type.trim()}</span>
                            {PLUG_IMAGES[type.trim().toUpperCase()] && (
                              <div className="plug-img-wrapper">
                                <img src={PLUG_IMAGES[type.trim().toUpperCase()]} alt={`Typ ${type}`} className="plug-img" referrerPolicy="no-referrer" />
                                <div className="plug-img-enlarged">
                                  <img src={getEnlargedPlugUrl(PLUG_IMAGES[type.trim().toUpperCase()])} alt={`Typ ${type} powiększony`} referrerPolicy="no-referrer" />
                                </div>
                              </div>
                            )}
                          </div>
                        )) : <div className="no-data-msg">Brak danych o typach gniazdek</div>}
                      </div>
                      <div className={`plug-comparison ${checkPlugs(selectedCountry.practical.plug_types).class}`}>
                        {checkPlugs(selectedCountry.practical.plug_types).warning && '⚠️ '}
                        {checkPlugs(selectedCountry.practical.plug_types).text}
                      </div>
                    </div>
                    <DataSource sources={['REST', 'WIKI']} />
                  </div>

                  <div id="emergency" className="info-block full-width emergency-section-box scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">🚨</span>
                      <label>Telefony i Łączność</label>
                    </div>
                    <div className="emergency-container">
                      <div className="connectivity-badges">
                        {selectedCountry.practical.emergency?.member_112 && (
                          <div className="emergency-112-hero mini">
                            <span className="hero-112-badge">🇪🇺 112</span>
                            <div className="hero-112-text">
                              <strong>Europejski Numer Alarmowy</strong>
                            </div>
                          </div>
                        )}
                        {selectedCountry.practical.roaming_info && (
                          <div className="roaming-badge-hero">
                            <span className="roaming-icon">📱</span>
                            <div className="roaming-text">
                              <strong>Roam Like at Home</strong>
                              <p>Rozmowy i internet jak w Polsce (UE/EOG)</p>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="emergency-grid">
                        <div className="emergency-item-box">
                          <span className="emergency-icon">🚓</span>
                          <span className="emergency-label">Policja</span>
                          <span className="emergency-num">{selectedCountry.practical.emergency?.police || (selectedCountry.practical.emergency?.member_112 ? '112' : 'Brak')}</span>
                        </div>
                        <div className="emergency-item-box">
                          <span className="emergency-icon">🚑</span>
                          <span className="emergency-label">Pogotowie</span>
                          <span className="emergency-num">{selectedCountry.practical.emergency?.ambulance || (selectedCountry.practical.emergency?.member_112 ? '112' : 'Brak')}</span>
                        </div>
                        <div className="emergency-item-box">
                          <span className="emergency-icon">🚒</span>
                          <span className="emergency-label">Straż</span>
                          <span className="emergency-num">{selectedCountry.practical.emergency?.fire || (selectedCountry.practical.emergency?.member_112 ? '112' : 'Brak')}</span>
                        </div>
                      </div>
                    </div>
                    <DataSource sources={['MSZ', 'WIKI']} />
                  </div>

                  <div id="costs" className="info-block full-width costs-section-box scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">📊</span>
                      <label>Ceny w porównaniu do Polski</label>
                    </div>
                    <div className="costs-container">
                      {selectedCountry.costs?.ratio_to_pl ? (
                        <>
                          <div className="costs-main-info">
                            <span className={`costs-badge ${
                              selectedCountry.costs.ratio_to_pl < 0.7 ? 'much-cheaper' :
                              selectedCountry.costs.ratio_to_pl < 0.9 ? 'cheaper' :
                              selectedCountry.costs.ratio_to_pl < 1.1 ? 'similar' :
                              selectedCountry.costs.ratio_to_pl < 1.5 ? 'expensive' : 'much-expensive'
                            }`}>
                              {selectedCountry.costs.ratio_to_pl < 0.7 ? 'Znacznie taniej niż w PL' :
                               selectedCountry.costs.ratio_to_pl < 0.9 ? 'Taniej niż w PL' :
                               selectedCountry.costs.ratio_to_pl < 1.1 ? 'Ceny zbliżone do PL' :
                               selectedCountry.costs.ratio_to_pl < 1.5 ? 'Drożej niż w PL' : 'Znacznie drożej niż w PL'}
                            </span>
                            <span className="costs-ratio">
                              Średnio: <strong>{(selectedCountry.costs.ratio_to_pl * 100).toFixed(0)}%</strong> cen w PL
                            </span>
                          </div>

                          <div className="costs-visual-chart">
                            <div className="costs-markers">
                              {[0, 50, 100, 150, 200].map(p => (
                                <div key={p} className="marker-line-group" style={{ left: `${(p / 200) * 100}%` }}>
                                  <span className="marker-label">{p}%</span>
                                  <div className={`marker-line ${p === 100 ? 'base' : ''}`}></div>
                                </div>
                              ))}
                            </div>

                            <div className="costs-bars-list">
                              {[
                                { label: 'Restauracje', icon: '🍔', val: selectedCountry.costs.restaurants ? selectedCountry.costs.restaurants / 0.42 : null },
                                { label: 'Zakupy', icon: '🛒', val: selectedCountry.costs.groceries ? selectedCountry.costs.groceries / 0.42 : null },
                                { label: 'Transport', icon: '🚌', val: selectedCountry.costs.transport ? selectedCountry.costs.transport / 0.42 : null },
                                { label: 'Nocleg', icon: '🏨', val: selectedCountry.costs.accommodation ? selectedCountry.costs.accommodation / 0.42 : null },
                              ].map((item, idx) => {
                                const isOverflow = (item.val || 0) > 200;
                                return (
                                  <div key={idx} className="cost-bar-row">
                                    <div className="cost-bar-label-box">
                                      <span className="cost-bar-icon">{item.icon}</span>
                                      <span className="cost-bar-name">{item.label}</span>
                                    </div>
                                    <div className="cost-bar-wrapper">
                                      {item.val !== null ? (
                                        <div 
                                          className={`cost-bar-fill-v2 ${isOverflow ? 'overflow' : ''}`} 
                                          style={{ 
                                            width: `${Math.min(100, (item.val / 200) * 100)}%`,
                                            backgroundColor: item.val < 90 ? '#48bb78' : item.val < 110 ? '#4299e1' : isOverflow ? '#9b2c2c' : '#f56565'
                                          }}
                                        >
                                          <span className="cost-bar-value">
                                            {item.val.toFixed(0)}%{isOverflow ? '+' : ''}
                                          </span>
                                        </div>
                                      ) : (
                                        <div className="cost-bar-no-data">Brak danych</div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                          <p className="costs-disclaimer">* Wartości przybliżone w oparciu o koszty w Polsce (100%)</p>
                        </>
                      ) : (
                        <div className="costs-no-data-placeholder">
                          <span className="no-data-icon">📉</span>
                          <p>Brak dostępnych danych statystycznych o kosztach życia dla tego kraju.</p>
                        </div>
                      )}
                    </div>
                    <DataSource sources={['NUMBEO']} />
                  </div>

                  <div id="climate" className="info-block full-width climate-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">🌤️</span>
                      <label>Typowa pogoda (średnie miesięczne)</label>
                    </div>
                    {selectedCountry.climate && selectedCountry.climate.length > 0 ? (
                      <div className="combined-chart-container" onMouseLeave={() => setChartTooltip(prev => ({ ...prev, visible: false }))}>
                        <div className="chart-y-axis-label left">Temperatura (°C)</div>
                        <div className="chart-y-axis-label right">Opady (mm)</div>
                        
                        {chartTooltip.visible && (
                          <div className="chart-custom-tooltip" style={{ left: chartTooltip.x, top: chartTooltip.y }}>
                            {chartTooltip.text}
                          </div>
                        )}

                        <svg viewBox="0 0 600 260" className="combined-svg-chart">
                          {/* Grid lines & Y-Axis Labels */}
                          {[-20, -10, 0, 10, 20, 30, 40].map(temp => {
                            const y = 200 - (temp + 20) * 3.5; // Offset 20, scale 3.5
                            return (
                              <g key={temp}>
                                <line x1="40" y1={y} x2="560" y2={y} className={`chart-grid-line ${temp === 0 ? 'zero-line' : ''}`} />
                                <text x="35" y={y + 4} textAnchor="end" className="chart-axis-text temp">{temp}°</text>
                              </g>
                            );
                          })}

                          {/* Rain Axis Labels */}
                          {(() => {
                            const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);
                            return [0, 0.5, 1].map(p => (
                              <text key={p} x="565" y={200 - p * 180 + 4} textAnchor="start" className="chart-axis-text rain">
                                {Math.round(p * maxRain)}
                              </text>
                            ));
                          })()}

                          {/* Rain Bars */}
                          {selectedCountry.climate?.map((cl, i) => {
                            const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);
                            const barHeight = (cl.rain / maxRain) * 180;
                            return (
                              <rect
                                key={`rain-${i}`}
                                x={50 + i * 43}
                                y={200 - barHeight}
                                width="24"
                                height={barHeight}
                                className="chart-bar-rain"
                                onMouseEnter={(e) => setChartTooltip({
                                  visible: true,
                                  text: `${cl.rain} mm`,
                                  x: e.nativeEvent.offsetX,
                                  y: e.nativeEvent.offsetY - 30
                                })}
                                onMouseMove={(e) => setChartTooltip(prev => ({
                                  ...prev,
                                  x: e.nativeEvent.offsetX,
                                  y: e.nativeEvent.offsetY - 30
                                }))}
                              />
                            );
                          })}

                          {/* Temperature Lines */}
                          {(() => {
                            const getX = (i: number) => 62 + i * 43;
                            const getY = (temp: number) => 200 - (temp + 20) * 3.5;
                            const dayPath = selectedCountry.climate?.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_day)}`).join(' ') || '';
                            const nightPath = selectedCountry.climate?.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_night)}`).join(' ') || '';
                            return (
                              <>
                                <path d={dayPath} className="chart-line-day" fill="none" />
                                <path d={nightPath} className="chart-line-night" fill="none" />
                                {selectedCountry.climate?.map((cl, i) => (
                                  <g key={`dots-${i}`}>
                                    <circle cx={getX(i)} cy={getY(cl.temp_day)} r="4" className="chart-dot-day"
                                      onMouseEnter={(e) => setChartTooltip({ visible: true, text: `Dzień: ${cl.temp_day}°C`, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 })}
                                      onMouseMove={(e) => setChartTooltip(prev => ({ ...prev, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 }))}
                                    />
                                    <circle cx={getX(i)} cy={getY(cl.temp_night)} r="4" className="chart-dot-night"
                                      onMouseEnter={(e) => setChartTooltip({ visible: true, text: `Noc: ${cl.temp_night}°C`, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 })}
                                      onMouseMove={(e) => setChartTooltip(prev => ({ ...prev, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 }))}
                                    />
                                  </g>
                                ))}
                              </>
                            );
                          })()}

                          {selectedCountry.climate?.map((cl, i) => (
                            <text key={`label-${i}`} x={62 + i * 43} y="240" textAnchor="middle" className="chart-month-text">
                              {new Date(2024, cl.month - 1).toLocaleDateString('pl-PL', { month: 'narrow' })}
                            </text>
                          ))}
                        </svg>

                        <div className="chart-legend-combined">
                          <span className="legend-item"><i className="legend-line day"></i> Dzień</span>
                          <span className="legend-item"><i className="legend-line night"></i> Noc</span>
                          <span className="legend-item"><i className="legend-rect rain"></i> Opady (mm)</span>
                        </div>
                      </div>
                    ) : (
                      <p className="no-data-text">Brak danych klimatycznych dla tego kraju.</p>
                    )}
                    <DataSource sources={['METEO', 'OWM']} />
                  </div>

                  <div id="health" className="info-block full-width health-section-box scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">💉</span>
                      <label>Zdrowie i szczepienia</label>
                    </div>
                    <div className="health-container">
                      {selectedCountry.practical.health_info && (
                        <div className="health-full-info">
                          <strong>Oficjalne zalecenia MSZ:</strong>
                          <ExpandableText text={selectedCountry.practical.health_info} />
                        </div>
                      )}
                      
                      {(selectedCountry.practical.vaccinations_required || selectedCountry.practical.vaccinations_suggested) && (
                        <div className="health-summary-vax">
                          {selectedCountry.practical.vaccinations_required && (
                            <div className="health-item mandatory" style={{ backgroundColor: '#fed7d7', borderLeft: '5px solid #f56565' }}>
                              <span className="health-icon">🚨</span>
                              <div className="health-text">
                                <strong style={{ color: '#822727' }}>Obowiązkowe:</strong>
                                <p>{selectedCountry.practical.vaccinations_required.replace(/szczepienie przeciw /gi, '').replace(/szczepienie przeciwko /gi, '').replace(/Obowiązkowe: /gi, '')}</p>
                              </div>
                            </div>
                          )}
                          {selectedCountry.practical.vaccinations_suggested && (
                            <div className="health-item suggested" style={{ backgroundColor: '#fefcbf', borderLeft: '5px solid #ecc94b' }}>
                              <span className="health-icon">💉</span>
                              <div className="health-text">
                                <strong style={{ color: '#744210' }}>Zalecane:</strong>
                                <p>{selectedCountry.practical.vaccinations_suggested.replace(/Zalecane: /gi, '')}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {!selectedCountry.practical.health_info && !selectedCountry.practical.vaccinations_required && !selectedCountry.practical.vaccinations_suggested && (
                                                <div className="no-data-msg">Brak szczegółowych informacji o zdrowiu (sprawdź aktualny komunikat MSZ).</div>

                      )}

                      {selectedCountry.safety.url && (
                        <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="health-msz-link">
                          Pełny raport zdrowotny na gov.pl →
                        </a>
                      )}
                    </div>
                    <DataSource sources={['CDC', 'MSZ']} />
                  </div>

                  <div id="holidays" className="info-block full-width holiday-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">📅</span>
                      <label>Święta i dni wolne</label>
                    </div>
                    
                    {selectedCountry.holidays && selectedCountry.holidays.length > 0 ? (
                      <div className="holiday-container">
                        <div className="expanded-holiday-list">
                          {Object.entries(
                            ([...selectedCountry.holidays])
                              .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                              .reduce((acc, h) => {
                                const month = new Date(h.date).toLocaleDateString('pl-PL', { month: 'long' });
                                if (!acc[month]) acc[month] = [];
                                acc[month].push(h);
                                return acc;
                              }, {} as Record<string, any[]>)
                          ).map(([month, monthHolidays]) => (
                            <div key={month} className="holiday-month-group">
                              <h5 className="holiday-month-header">{month}</h5>
                              <div className="holiday-month-items">
                                {(monthHolidays as any[]).map((h, idx) => (
                                  <div key={idx} className="holiday-item">
                                    <span className="holiday-date">{new Date(h.date).toLocaleDateString('pl-PL', { day: 'numeric' })}</span>
                                    <span className="holiday-name">{h.name}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="no-data-msg">Brak informacji o świętach dla tego kraju.</div>
                    )}
                    <DataSource sources={['NAGER']} />
                  </div>

                  <div id="embassies" className="info-block full-width embassy-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">🏢</span>
                      <label>Polskie placówki dyplomatyczne</label>
                    </div>
                    {selectedCountry.embassies && selectedCountry.embassies.length > 0 ? (
                      <div className="embassy-container">
                        {(() => {
                          const order = ['Ambasada', 'Wydział Konsularny', 'Konsulat Generalny', 'Konsulat', 'Konsulat Honorowy', 'Placówka'];
                          const sortedAll = [...selectedCountry.embassies].sort((a, b) => {
                            let idxA = order.indexOf(a.type);
                            let idxB = order.indexOf(b.type);
                            if (idxA === -1) idxA = 99;
                            if (idxB === -1) idxB = 99;
                            return idxA - idxB;
                          });

                          const embassiesGroup = sortedAll.filter(e => e.type === 'Ambasada');
                          const consulatesAll = sortedAll.filter(e => e.type !== 'Ambasada');
                          
                          const displayedConsulates = isEmbassiesExpanded ? consulatesAll : consulatesAll.slice(0, 2);
                          const hasHiddenConsulates = consulatesAll.length > 2;

                          const renderEmbassy = (emb: any, idx: number) => (
                            <div key={idx} className="embassy-item">
                              <strong>{emb.type} {emb.city ? `w ${emb.city}` : ''}</strong>
                              {emb.address && <p>📍 {emb.address}</p>}
                              {emb.phone && <p>📞 {emb.phone}</p>}
                              {emb.email && <p>✉️ <a href={`mailto:${emb.email}`}>{emb.email}</a></p>}
                              {emb.website && <p>🌐 <a href={emb.website} target="_blank" rel="noreferrer">Strona WWW</a></p>}
                            </div>
                          );

                          return (
                            <>
                              {embassiesGroup.length > 0 && (
                                <div className="embassy-group">
                                  <h4 className="embassy-group-title">Ambasada</h4>
                                  <div className="embassy-grid">
                                    {embassiesGroup.map(renderEmbassy)}
                                  </div>
                                </div>
                              )}
                              
                              {consulatesAll.length > 0 && (
                                <div className="embassy-group">
                                  <h4 className="embassy-group-title">Konsulaty i pozostałe placówki</h4>
                                  <div className="embassy-grid">
                                    {displayedConsulates.map(renderEmbassy)}
                                  </div>
                                </div>
                              )}
                              
                              {hasHiddenConsulates && (
                                <button 
                                  className="section-expand-btn" 
                                  style={{ marginTop: '1rem', width: '100%' }}
                                  onClick={() => setIsEmbassiesExpanded(!isEmbassiesExpanded)}
                                >
                                  {isEmbassiesExpanded ? 'Pokaż mniej' : `Pokaż pozostałe placówki (${consulatesAll.length - 2})`}
                                </button>
                              )}
                            </>
                          );
                        })()}
                      </div>
                    ) : (
                      <div className="no-data-msg">Brak danych o polskich placówkach w tym kraju.</div>
                    )}
                    <DataSource sources={['MSZ']} />
                  </div>

                  <div id="attractions" className="info-block full-width unesco-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">📍</span>
                      <label>Najciekawsze miejsca i atrakcje</label>
                    </div>
                    {selectedCountry.attractions && selectedCountry.attractions.length > 0 ? (
                      <div className="unesco-grid">
                        {selectedCountry.attractions.map((attr, idx) => (
                          <div key={idx} className="unesco-item-v2">
                            <div className="unesco-item-content">
                              <div className="unesco-item-header">
                                <span className="unesco-icon">✨</span>
                                <span className="unesco-name">{attr.name}</span>
                              </div>
                              {attr.description && (
                                <div className="unesco-description">
                                  <ExpandableText text={attr.description} />
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="no-data-msg">Nie znaleziono szczegółowych informacji o atrakcjach turystycznych.</div>
                    )}
                    <DataSource sources={['WIKI']} />
                  </div>

                  <div id="unesco" className="info-block full-width unesco-section scroll-mt">
                    <div className="section-header">
                      <span className="section-header-icon">🏛️</span>
                      <label>Lista UNESCO ({selectedCountry.unesco_count || 0})</label>
                    </div>
                    {selectedCountry.unesco_places && selectedCountry.unesco_places.length > 0 ? (
                      <>
                        <div className="unesco-grid">
                          {(isUnescoExpanded ? selectedCountry.unesco_places : selectedCountry.unesco_places.slice(0, 10)).map((place, idx) => (
                            <div key={idx} className="unesco-item-v2 has-link" onClick={() => {
                              if (place.unesco_id) window.open(`https://whc.unesco.org/en/list/${place.unesco_id}`, '_blank');
                            }}>
                              {place.image_url && (
                                <div className="unesco-item-image">
                                  <img src={place.image_url} alt={place.name} loading="lazy" />
                                </div>
                              )}
                              <div className="unesco-item-content">
                                <div className="unesco-item-header">
                                  <span className="unesco-icon">
                                    {place.category === 'Cultural' ? '🏛️' : 
                                    place.category === 'Natural' ? '🌳' : 
                                    place.category === 'Mixed' ? '🏔️' : '📍'}
                                  </span>
                                  <div className="unesco-name">{place.name}</div>
                                </div>
                                <div className="unesco-badges-container" style={{ display: 'flex', gap: '8px', marginLeft: '32px' }}>
                                  <div className={`unesco-type-badge ${place.category?.toLowerCase() || ''}`}>{place.category}</div>
                                  {!!place.is_transnational && <div className="unesco-type-badge transnational">MIĘDZYNARODOWE</div>}
                                  {!!place.is_danger && <div className="unesco-type-badge danger">ZAGROŻONE</div>}
                                </div>
                                
                                {place.description && (
                                  <div className="unesco-description" onClick={(e) => e.stopPropagation()}>
                                    <ExpandableText text={place.description} />
                                  </div>
                                )}

                                {place.unesco_id && (
                                  <div className="unesco-official-link">
                                    Zobacz oficjalną stronę UNESCO →
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                        {selectedCountry.unesco_places.length > 10 && (
                          <button 
                            className="section-expand-btn" 
                            style={{ 
                              marginTop: '0.5rem', 
                              width: '100%', 
                              padding: '0.4rem', 
                              fontSize: '0.75rem', 
                              backgroundColor: 'transparent', 
                              border: '1px solid #e2e8f0',
                              color: '#718096'
                            }}
                            onClick={() => setIsUnescoExpanded(!isUnescoExpanded)}
                          >
                            {isUnescoExpanded ? 'Pokaż mniej' : `Pokaż pozostałe (${selectedCountry.unesco_places.length - 10})`}
                          </button>
                        )}
                      </>
                    ) : (
                      <div className="no-data-msg">Brak wpisów na liście UNESCO dla tego kraju.</div>
                    )}
                    <DataSource sources={['UNESCO']} />
                  </div>
                  
                </div>

                    <div className="section-header">
                      <span className="section-header-icon">🛡️</span>
                      <label>Bezpieczeństwo (MSZ)</label>
                    </div>
                  <div id="safety" className={`info-block full-width safety-info risk-${selectedCountry.safety.risk_level} scroll-mt`}>
                    <p className="risk-desc">{SAFETY_LABELS[selectedCountry.safety.risk_level] || selectedCountry.safety.risk_level}</p>
                    <p className="risk-summary-text"><LinkifyOdyseusz text={selectedCountry.safety.risk_text} /></p>
                    {selectedCountry.safety.risk_details && (
                      <div className="risk-details-box">
                        <ExpandableText text={selectedCountry.safety.risk_details} />
                      </div>
                    )}
                    {selectedCountry.safety.url && (
                      <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="msz-link">
                        Zobacz pełny komunikat MSZ na gov.pl →
                      </a>
                    )}
                  </div>
                  <DataSource sources={['MSZ']} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
