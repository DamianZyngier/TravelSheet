import { useState, useEffect, useMemo } from 'react'
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps"
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
  };
  entry?: {
    visa_required: boolean | null;
    passport_required: boolean | null;
    temp_passport_allowed: boolean | null;
    id_card_allowed: boolean | null;
    visa_notes: string;
  };
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
          setSelectedCountry(data[countryCode.toUpperCase()]);
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

  // Aktualizuj URL gdy zmienia się wybrany kraj
  const handleSelectCountry = (country: CountryData | null) => {
    setSelectedCountry(country);
    
    if (country && country.longitude !== null && country.latitude !== null) {
      setMapPosition({ 
        coordinates: [country.longitude, country.latitude], 
        zoom: 4 
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
    return Object.values(countries)
      .filter(c => {
        const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
        const matchContinent = filterContinent === 'all' || c.continent === filterContinent;
        const matchSearch = c.name_pl.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            c.iso2.toLowerCase().includes(searchQuery.toLowerCase());
        
        return matchSafety && matchContinent && matchSearch;
      })
      .sort((a, b) => a.name_pl.localeCompare(b.name_pl, 'pl'));
  }, [countries, filterSafety, filterContinent, searchQuery]);

  if (loading) return <div className="loader">Ładowanie danych podróżniczych...</div>;

  return (
    <div className="app-container">
      {error && <div className="error-toast">{error}</div>}
      
      {!selectedCountry ? (
        <>
          <header className="main-header">
            <div className="header-content">
              <div className="logo-section">
                <h1>🌍 TravelSheet</h1>
                <p>Twoje centrum bezpiecznych podróży</p>
              </div>
              
              <div className="controls-section">
                <input 
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
                  projectionConfig={{ scale: 140 }}
                  style={{ width: "100%", height: "100%" }}
                >
                  <ZoomableGroup
                    center={mapPosition.coordinates}
                    zoom={mapPosition.zoom}
                    onMoveEnd={(pos) => setMapPosition(pos)}
                  >
                    <Geographies geography={geoUrl}>
                      {({ geographies }) =>
                        geographies.map((geo: any) => {
                          const isSelected = 
                            geo.id === selectedCountry.iso3 || 
                            geo.properties?.iso_a3 === selectedCountry.iso3 ||
                            geo.properties?.name === selectedCountry.name;
                          
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
                    
                    {selectedCountry.longitude !== null && selectedCountry.latitude !== null && (
                      <Marker coordinates={[selectedCountry.longitude, selectedCountry.latitude]}>
                        <circle r={4} fill="#F56565" stroke="#fff" strokeWidth={1} />
                        <text
                          textAnchor="middle"
                          y={-10}
                          style={{ fontFamily: "system-ui", fill: "#E53E3E", fontSize: "10px", fontWeight: "bold" }}
                        >
                          📍
                        </text>
                      </Marker>
                    )}
                  </ZoomableGroup>
                </ComposableMap>
                
                <div className="map-controls">
                  <button onClick={() => setMapPosition(prev => ({ ...prev, zoom: prev.zoom * 1.5 }))}>+</button>
                  <button onClick={() => setMapPosition(prev => ({ ...prev, zoom: prev.zoom / 1.5 }))}>-</button>
                  <button onClick={() => setMapPosition({ coordinates: [selectedCountry.longitude || 0, selectedCountry.latitude || 0], zoom: 4 })}>🎯</button>
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
                          <span className="plug-letter">{type.trim()}</span>
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

                <div className="info-block">
                  <label>Ruch drogowy</label>
                  <span>
                    {selectedCountry.practical.driving_side === 'right' ? 'Prawostronny' : 'Lewostronny'}
                  </span>
                </div>
              </div>

              <div className={`safety-info risk-${selectedCountry.safety.risk_level}`}>
                <h4>🛡️ Bezpieczeństwo (MSZ)</h4>
                <p className="risk-desc">{SAFETY_LABELS[selectedCountry.safety.risk_level] || selectedCountry.safety.risk_level}</p>
                <p className="risk-summary-text">{selectedCountry.safety.risk_text}</p>
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
