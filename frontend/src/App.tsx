import { useState, useEffect, useMemo, useRef } from 'react'
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps"
import logoNoText from './assets/logo-no-text.png'
import './App.css'

// URL do topologii świata (lekkie 110m)
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

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
    passport_required: boolean | null;
    temp_passport_allowed: boolean | null;
    id_card_allowed: boolean | null;
    visa_notes: string;
  };
  holidays?: {
    name: string;
    date: string;
  }[];
  climate?: {
    month: number;
    temp_day: number;
    temp_night: number;
    rain: number;
  }[];
}

function ExpandableText({ text }: { text: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  if (!text) return null;

  const paragraphs = text.split('\n\n');
  // Lower threshold to 150 characters or multiple paragraphs
  const hasMore = text.length > 150 || paragraphs.length > 1;

  if (!hasMore) return <div className="risk-details-text">{text}</div>;

  return (
    <div className={`expandable-text-container ${isExpanded ? 'expanded' : ''}`}>
      <div className="risk-details-text">
        {isExpanded ? text : (text.slice(0, 150) + '...')}
      </div>
      {!isExpanded && <div className="text-gradient"></div>}
      <button 
        className="show-more-btn" 
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? 'Pokaż mniej' : 'Pokaż więcej'}
      </button>
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
  const searchInputRef = useRef<HTMLInputElement>(null);

  const SAFETY_LABELS: Record<string, string> = {
    'low': 'Bezpiecznie',
    'medium': 'Średnio bezpiecznie',
    'high': 'Niebezpiecznie',
    'critical': 'Bardzo niebezpiecznie',
    'unknown': 'Brak danych'
  };

  const CONTINENT_MAP: Record<string, string> = {
    'Africa': 'Afryka',
    'Antarctica': 'Antarktyda',
    'Asia': 'Azja',
    'Europe': 'Europa',
    'North America': 'Ameryka Północna',
    'Oceania': 'Oceania',
    'South America': 'Ameryka Południowa'
  };

  const formatPLN = (value: number | null) => {
    if (value === null) return 'brak danych';
    return value.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' PLN';
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

  const checkPlugs = (types: string) => {
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
        
        // Deep linking: sprawdź parametr w URL po załadowaniu danych
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

    // Obsługa przycisku wstecz w przeglądarce
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const countryCode = params.get('kraj');
      if (!countryCode) {
        setSelectedCountry(null);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Dynamiczne obliczanie przybliżenia i widoczności kropki
  const getMapSettings = (country: CountryData) => {
    const huge = ['RU', 'CA', 'US', 'CN', 'BR', 'AU', 'IN', 'AR', 'KZ', 'DZ'];
    const large = ['SA', 'MX', 'ID', 'SD', 'LY', 'MN', 'TD', 'PE', 'NE', 'AO', 'CO', 'ZA', 'ML', 'ET', 'BO', 'MR', 'EG', 'TR', 'PL', 'UA', 'FR', 'DE', 'ES', 'SE', 'NO'];
    const tiny = [
      'AD', 'MO', 'SM', 'LI', 'VA', 'MT', 'SG', 'HK', 'LU', 'MC', 'MS', 'GI', 'TC', 'VG', 'AI', 'BM', 'AW', 'SX', 'BQ', 'CW', 'PF', 'NC', 'WF', 'YT', 'RE', 'BL', 'MF', 'PM', 'FK', 'SH', 'PN', 'GS', 'IO', 'TF', 'HM', 'BV', 'CV', 'ST', 'SC', 'MU', 'KM', 'MV', 'LS', 'SZ', 'BH', 'BB', 'DM', 'GD', 'KN', 'LC', 'VC', 'AG', 'BS', 'PW', 'MH', 'FM', 'NR', 'KI', 'TO', 'WS', 'TV', 'VU'
    ];

    let zoom = 10;
    let showDot = false; // Domyślnie ukryta

    if (huge.includes(country.iso2)) {
      zoom = 2.5;
    } else if (large.includes(country.iso2)) {
      zoom = 5;
    } else if (tiny.includes(country.iso2)) {
      zoom = 25;
      showDot = true; // Tylko dla mikro-krajów
    }

    return { zoom, showDot };
  };

  // Aktualizuj URL gdy zmienia się wybrany kraj
  const handleSelectCountry = (country: CountryData | null) => {
    setSelectedCountry(country);
    
    if (country && country.longitude !== null && country.latitude !== null) {
      const { zoom } = getMapSettings(country);
      setMapPosition({ 
        coordinates: [country.longitude, country.latitude], 
        zoom: zoom
      });
    } else {
      setMapPosition({ coordinates: [0, 0], zoom: 1 });
    }

    const url = new URL(window.location.href);
    if (country) {
      url.searchParams.set('kraj', country.iso2);
    } else {
      url.searchParams.delete('kraj');
    }
    window.history.pushState({}, '', url.toString());
  };

  const continents = useMemo(() => {
    const set = new Set(Object.values(countries).map(c => c.continent).filter(Boolean));
    return Array.from(set).sort();
  }, [countries]);

  const countryList = useMemo(() => {
    // Słownik aliasów dla wyszukiwania
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

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl + F: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }

      // Backspace: Return to list (only if not in an input and a country is selected)
      if (e.key === 'Backspace' && selectedCountry) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          handleSelectCountry(null);
        }
      }

      // Enter: Select single result
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
                <input 
                  ref={searchInputRef}
                  type="text" 
                  placeholder="Szukaj kraju..." 
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="search-input"
                />
                
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
                      <h3>{country.name_pl}</h3>
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
        <div className="detail-view-container">
          <button className="back-button" onClick={() => handleSelectCountry(null)}>
            ← Powrót do listy
          </button>
          
          <div className="detail-card">
            <div className="detail-header">
              <img 
                src={selectedCountry.flag_url} 
                alt={`Flaga ${selectedCountry.name_pl}`} 
                className="detail-flag-img" 
                style={{ objectFit: 'contain' }}
              />
              <div className="detail-titles">
                <h2>{selectedCountry.name_pl}</h2>
                <p>{selectedCountry.name} ({selectedCountry.iso2})</p>
              </div>
              
              <div className="detail-map-container">
                <ComposableMap 
                  key={selectedCountry.iso2}
                  projectionConfig={{ scale: 140 }}
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
                            geo.properties?.name === selectedCountry.name ||
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
                        {/* Outer white glow/border - constant screen size */}
                        <circle 
                          r={0.1} 
                          fill="none" 
                          stroke="#fff" 
                          strokeWidth={20} 
                          vectorEffect="non-scaling-stroke" 
                        />
                        {/* Inner red dot - constant screen size */}
                        <circle 
                          r={0.1} 
                          fill="none" 
                          stroke="#F56565" 
                          strokeWidth={14} 
                          vectorEffect="non-scaling-stroke" 
                        />
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
              <div className="info-grid">
                <div className="info-block">
                  <label>Kontynent</label>
                  <span>{CONTINENT_MAP[selectedCountry.continent] || selectedCountry.continent}</span>
                </div>
                <div className="info-block">
                  <label>Stolica</label>
                  <span>{selectedCountry.capital || 'Brak danych'}</span>
                </div>
                
                <div className="info-block full-width docs-section">
                  <label>Wymagane dokumenty (dla Polaków)</label>
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
                      <span>{selectedCountry.entry?.visa_required ? '🛂 WYMAGANA' : '🆓 NIEPOTRZEBNA'}</span>
                    </div>
                  </div>
                </div>

                <div className="info-block full-width">
                  <label>Waluta</label>
                  <span>
                    {selectedCountry.currency.name} ({selectedCountry.currency.code}) <br/>
                    {selectedCountry.currency.rate_pln ? (
                      <>
                        1 {selectedCountry.currency.code} = {formatPLN(selectedCountry.currency.rate_pln)}
                        <br/>
                        <small style={{ color: '#718096' }}>{getCurrencyExample(selectedCountry)}</small>
                      </>
                    ) : 'brak danych o kursie'}
                  </span>
                </div>

                <div className="info-block full-width">
                  <label>Gniazdka elektryczne</label>
                  <div className="plugs-container">
                    <div className="plug-types-list">
                      {selectedCountry.practical.plug_types.split(',').map(type => (
                        <div key={type} className="plug-icon-box">
                          <span className="plug-letter">Typ {type.trim()}</span>
                          {PLUG_IMAGES[type.trim().toUpperCase()] && (
                            <div className="plug-img-wrapper">
                              <img 
                                src={PLUG_IMAGES[type.trim().toUpperCase()]} 
                                alt={`Typ ${type}`}
                                className="plug-img"
                                referrerPolicy="no-referrer"
                              />
                              <div className="plug-img-enlarged">
                                <img 
                                  src={getEnlargedPlugUrl(PLUG_IMAGES[type.trim().toUpperCase()])} 
                                  alt={`Typ ${type} powiększony`}
                                  referrerPolicy="no-referrer"
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className={`plug-comparison ${checkPlugs(selectedCountry.practical.plug_types).class}`}>
                      {checkPlugs(selectedCountry.practical.plug_types).warning && '⚠️ '}
                      {checkPlugs(selectedCountry.practical.plug_types).text}
                    </div>
                  </div>
                </div>

                <div className="info-block full-width emergency-section-box">
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <label>Telefony alarmowe</label>
                    {selectedCountry.practical.emergency?.member_112 && (
                      <span className="emergency-112-badge" title="Europejski numer alarmowy 112 działa w tym kraju">
                        🇪🇺 112
                      </span>
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

                <div className="info-block full-width costs-section-box">
                  <label>Ceny w porównaniu do Polski</label>
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
                          {/* Percent markers */}
                          <div className="costs-markers">
                            {[50, 75, 100, 125, 150, 175, 200].map(p => (
                              <div key={p} className="marker-line-group" style={{ left: `${(p / 200) * 100}%` }}>
                                <span className="marker-label">{p}%</span>
                                <div className={`marker-line ${p === 100 ? 'base' : ''}`}></div>
                              </div>
                            ))}
                          </div>

                          <div className="costs-bars-list">
                            {[
                              { label: 'Restauracje', icon: '🍔', val: (selectedCountry.costs.restaurants || 0) / 0.42 },
                              { label: 'Zakupy', icon: '🛒', val: (selectedCountry.costs.groceries || 0) / 0.42 },
                              { label: 'Transport', icon: '🚌', val: (selectedCountry.costs.transport || 0) / 0.42 },
                              { label: 'Nocleg', icon: '🏨', val: (selectedCountry.costs.accommodation || 0) / 0.42 },
                            ].map((item, idx) => (
                              <div key={idx} className="cost-bar-row">
                                <div className="cost-bar-label-box">
                                  <span className="cost-bar-icon">{item.icon}</span>
                                  <span className="cost-bar-name">{item.label}</span>
                                </div>
                                <div className="cost-bar-wrapper">
                                  <div 
                                    className="cost-bar-fill-v2" 
                                    style={{ 
                                      width: `${Math.min(100, (item.val / 200) * 100)}%`,
                                      backgroundColor: item.val < 90 ? '#48bb78' : item.val < 110 ? '#4299e1' : '#f56565'
                                    }}
                                  >
                                    <span className="cost-bar-value">{item.val.toFixed(0)}%</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                        <p className="costs-disclaimer">* Wartości przybliżone w oparciu o koszty w Polsce (100%)</p>
                      </>
                    ) : 'Brak danych o kosztach'}
                  </div>
                </div>

                <div className="info-block">
                  <label>Ruch drogowy</label>
                  <span>
                    {selectedCountry.practical.driving_side === 'right' ? 'Prawostronny' : 'Lewostronny'}
                  </span>
                </div>

                {selectedCountry.climate && selectedCountry.climate.length > 0 && (
                  <div className="info-block full-width climate-section">
                    <label>Typowa pogoda (średnie miesięczne)</label>
                    <div className="combined-chart-container" onMouseLeave={() => setChartTooltip(prev => ({ ...prev, visible: false }))}>
                      <div className="chart-y-axis-label left">Temperatura (°C)</div>
                      <div className="chart-y-axis-label right">Opady (mm)</div>
                      
                      {chartTooltip.visible && (
                        <div 
                          className="chart-custom-tooltip" 
                          style={{ left: chartTooltip.x, top: chartTooltip.y }}
                        >
                          {chartTooltip.text}
                        </div>
                      )}

                      <svg viewBox="0 0 600 240" className="combined-svg-chart">
                        {/* Grid lines & Y-Axis Labels */}
                        {[0, 10, 20, 30, 40].map(temp => {
                          const y = 200 - (temp + 10) * 3;
                          return (
                            <g key={temp}>
                              <line x1="40" y1={y} x2="560" y2={y} className="chart-grid-line" />
                              <text x="35" y={y + 4} textAnchor="end" className="chart-axis-text temp">{temp}°</text>
                            </g>
                          );
                        })}

                        {/* Rain Axis Labels */}
                        {(() => {
                          const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);
                          return [0, 0.5, 1].map(p => (
                            <text 
                              key={p} 
                              x="565" 
                              y={200 - p * 160 + 4} 
                              textAnchor="start" 
                              className="chart-axis-text rain"
                            >
                              {Math.round(p * maxRain)}
                            </text>
                          ));
                        })()}

                        {/* Rain Bars */}
                        {selectedCountry.climate.map((cl, i) => {
                          const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);
                          const barHeight = (cl.rain / maxRain) * 160;
                          const x = 50 + i * 43;
                          const y = 200 - barHeight;
                          return (
                            <rect
                              key={`rain-${i}`}
                              x={x}
                              y={y}
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
                          const getY = (temp: number) => 200 - (temp + 10) * 3;
                          
                          const dayPath = selectedCountry.climate.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_day)}`).join(' ');
                          const nightPath = selectedCountry.climate.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_night)}`).join(' ');
                          
                          return (
                            <>
                              <path d={dayPath} className="chart-line-day" fill="none" />
                              <path d={nightPath} className="chart-line-night" fill="none" />
                              
                              {selectedCountry.climate.map((cl, i) => (
                                <g key={`dots-${i}`}>
                                  <circle 
                                    cx={getX(i)} cy={getY(cl.temp_day)} r="4" className="chart-dot-day"
                                    onMouseEnter={(e) => setChartTooltip({
                                      visible: true,
                                      text: `Dzień: ${cl.temp_day}°C`,
                                      x: e.nativeEvent.offsetX,
                                      y: e.nativeEvent.offsetY - 30
                                    })}
                                    onMouseMove={(e) => setChartTooltip(prev => ({
                                      ...prev,
                                      x: e.nativeEvent.offsetX,
                                      y: e.nativeEvent.offsetY - 30
                                    }))}
                                  />
                                  <circle 
                                    cx={getX(i)} cy={getY(cl.temp_night)} r="4" className="chart-dot-night"
                                    onMouseEnter={(e) => setChartTooltip({
                                      visible: true,
                                      text: `Noc: ${cl.temp_night}°C`,
                                      x: e.nativeEvent.offsetX,
                                      y: e.nativeEvent.offsetY - 30
                                    })}
                                    onMouseMove={(e) => setChartTooltip(prev => ({
                                      ...prev,
                                      x: e.nativeEvent.offsetX,
                                      y: e.nativeEvent.offsetY - 30
                                    }))}
                                  />
                                </g>
                              ))}
                            </>
                          );
                        })()}

                        {/* Month Labels */}
                        {selectedCountry.climate.map((cl, i) => (
                          <text
                            key={`label-${i}`}
                            x={62 + i * 43}
                            y="225"
                            textAnchor="middle"
                            className="chart-month-text"
                          >
                            {new Date(2024, cl.month - 1).toLocaleDateString('pl-PL', { month: 'narrow' })}
                          </text>
                        ))}
                      </svg>

                      <div className="chart-legend-combined">
                        <span className="legend-item"><i className="legend-line day"></i> Temperatura dzień</span>
                        <span className="legend-item"><i className="legend-line night"></i> Temperatura noc</span>
                        <span className="legend-item"><i className="legend-rect rain"></i> Opady (mm)</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="info-block full-width health-section-box">
                  <label>Zdrowie i szczepienia</label>
                  <div className="health-container">
                    {(selectedCountry.practical.vaccinations_required || selectedCountry.practical.vaccinations_suggested) ? (
                      <>
                        {selectedCountry.practical.vaccinations_required && (
                          <div className="health-item mandatory">
                            <span className="health-icon">🚨</span>
                            <div className="health-text">
                              <strong>Obowiązkowe:</strong>
                              <p>{selectedCountry.practical.vaccinations_required}</p>
                            </div>
                          </div>
                        )}
                        {selectedCountry.practical.vaccinations_suggested && (
                          <div className="health-item suggested">
                            <span className="health-icon">💉</span>
                            <div className="health-text">
                              <strong>Zalecane:</strong>
                              <p>{selectedCountry.practical.vaccinations_suggested}</p>
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="health-item neutral">
                        <span className="health-icon">✅</span>
                        <p>Brak szczególnych wymogów dotyczących szczepień (sprawdź aktualny komunikat MSZ).</p>
                      </div>
                    )}
                  </div>
                </div>

                {selectedCountry.embassies && selectedCountry.embassies.length > 0 && (
                  <div className="info-block full-width embassy-section">
                    <label>Polskie placówki dyplomatyczne</label>
                    <div className="embassy-list">
                      {selectedCountry.embassies.map((emb, idx) => (
                        <div key={idx} className="embassy-item">
                          <strong>{emb.type} {emb.city ? `w ${emb.city}` : ''}</strong>
                          {emb.address && <p>📍 {emb.address}</p>}
                          {emb.phone && <p>📞 {emb.phone}</p>}
                          {emb.email && <p>✉️ <a href={`mailto:${emb.email}`}>{emb.email}</a></p>}
                          {emb.website && <p>🌐 <a href={emb.website} target="_blank" rel="noreferrer">Strona WWW</a></p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCountry.holidays && selectedCountry.holidays.length > 0 && (
                  <div className="info-block full-width holiday-section">
                    <label>Święta i dni wolne</label>
                    <div className="holiday-list">
                      {Object.entries(
                        [...selectedCountry.holidays]
                          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                          .reduce((acc, h) => {
                            const month = new Date(h.date).toLocaleDateString('pl-PL', { month: 'long' });
                            if (!acc[month]) acc[month] = [];
                            acc[month].push(h);
                            return acc;
                          }, {} as Record<string, typeof selectedCountry.holidays>)
                      ).map(([month, monthHolidays]) => (
                        <div key={month} className="holiday-month-group">
                          <h5 className="holiday-month-header">{month}</h5>
                          {monthHolidays.map((h, idx) => (
                            <div key={idx} className="holiday-item">
                              <span className="holiday-date">{new Date(h.date).toLocaleDateString('pl-PL', { day: 'numeric' })}</span>
                              <span className="holiday-name">{h.name}</span>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className={`safety-info risk-${selectedCountry.safety.risk_level}`}>
                <h4>🛡️ Bezpieczeństwo (MSZ)</h4>
                <p className="risk-desc">{SAFETY_LABELS[selectedCountry.safety.risk_level] || selectedCountry.safety.risk_level}</p>
                <p className="risk-summary-text">{selectedCountry.safety.risk_text}</p>
                
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
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
