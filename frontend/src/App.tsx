import { useState, useEffect, useMemo, useRef } from 'react'
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps"
import logoNoText from './assets/logo-no-text.png'
import './App.css'

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
  unesco_count: number;
  timezone: string | null;
  national_dish: string | null;
  wiki_summary: string | null;
  national_symbols: string | null;
  population: number | null;
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
    vaccinations_required: string | null;
    vaccinations_suggested: string | null;
    health_info: string | null;
    roaming_info: string | null;
    license_type: string | null;
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
}

const CONTINENT_MAP: Record<string, string> = {
  'Africa': 'Afryka', 'Antarctica': 'Antarktyda', 'Asia': 'Azja', 'Europe': 'Europa',
  'North America': 'Ameryka Północna', 'Oceania': 'Oceania', 'South America': 'Ameryka Południowa'
};

const SAFETY_LABELS: Record<string, string> = {
  'low': 'Bezpiecznie',
  'medium': 'Zachowaj szczególną ostrożność',
  'high': 'Odradzane podróże, które nie są konieczne',
  'critical': 'Odradzane wszelkie podróże',
  'unknown': 'Brak danych MSZ'
};

function ExpandableText({ text, maxHeight = 150 }: { text: string, maxHeight?: number }) {
  const [isExpanded, setIsExpanded] = useState(false);
  if (!text) return null;
  
  const hasMore = text.length > maxHeight;
  
  return (
    <div className={`expandable-text-container ${isExpanded ? 'expanded' : ''}`}>
      <div className="risk-details-text" style={!isExpanded ? { maxHeight: `${maxHeight}px`, overflow: 'hidden' } : {}}>
        {text}
      </div>
      {!isExpanded && hasMore && <div className="text-gradient"></div>}
      {hasMore && (
        <button className="show-more-btn" onClick={() => setIsExpanded(!isExpanded)}>
          {isExpanded ? 'Pokaż mniej ▲' : 'Pokaż więcej ▼'}
        </button>
      )}
    </div>
  );
}

function LicensePage({ onBack }: { onBack: () => void }) {
  return (
    <div className="license-page">
      <button className="side-back-button" onClick={onBack} style={{ marginBottom: '2rem' }}>← Powrót do aplikacji</button>
      <h1>Licencje i Źródła Danych</h1>
      <section>
        <h2>Źródła Danych (APIs)</h2>
        <ul>
          <li><strong>MSZ (gov.pl):</strong> Oficjalne informacje o bezpieczeństwie, wizach i placówkach. Dane pobierane bezpośrednio z serwisu gov.pl.</li>
          <li><strong>Wikipedia (REST API):</strong> Opisy krajów i podsumowania geograficzne. Licencja: CC BY-SA 3.0.</li>
          <li><strong>Wikidata:</strong> Symbole narodowe, atrakcje i dane statystyczne. Licencja: CC0.</li>
          <li><strong>REST Countries:</strong> Podstawowe informacje o państwach (kody ISO, flagi, współrzędne).</li>
          <li><strong>NBP (Narodowy Bank Polski):</strong> Kursy walut w odniesieniu do złotego (PLN).</li>
          <li><strong>OpenWeatherMap:</strong> Aktualna pogoda w stolicach świata.</li>
          <li><strong>UNESCO:</strong> Lista Światowego Dziedzictwa UNESCO.</li>
        </ul>
      </section>
    </div>
  );
}

function App() {
  const [countries, setCountries] = useState<Record<string, CountryData>>({});
  const [loading, setLoading] = useState(true);
  const [selectedCountry, setSelectedCountry] = useState<CountryData | null>(null);
  const [showLicense, setShowLicense] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleToggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light');

  const [filterSafety, setFilterSafety] = useState('all');
  const [filterContinent, setFilterContinent] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeSection, setActiveSection] = useState('summary');
  const [mapPosition, setMapPosition] = useState({ coordinates: [0, 0] as [number, number], zoom: 1 });
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
    { id: 'health', label: 'Zdrowie', icon: '💉' },
    { id: 'safety', label: 'Bezpieczeństwo', icon: '🛡️' },
  ];

  useEffect(() => {
    fetch('./data.json').then(res => res.json()).then(data => {
      setCountries(data);
      setLoading(false);
      const code = new URLSearchParams(window.location.search).get('kraj');
      if (code && data[code.toUpperCase()]) handleSelectCountry(data[code.toUpperCase()]);
    }).catch(() => setLoading(false));
  }, []);

  const handleSelectCountry = (country: CountryData | null) => {
    setSelectedCountry(country);
    setShowLicense(false);
    setActiveSection('summary');
    if (country && country.longitude !== null && country.latitude !== null) {
      setMapPosition({ coordinates: [country.longitude, country.latitude], zoom: 5 });
    }
    const url = new URL(window.location.href);
    if (country) url.searchParams.set('kraj', country.iso2); else url.searchParams.delete('kraj');
    window.history.pushState({}, '', url.toString());
  };

  const countryList = useMemo(() => {
    return Object.values(countries).filter(c => {
      const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
      const matchContinent = filterContinent === 'all' || c.continent === filterContinent;
      const s = searchQuery.toLowerCase();
      return matchSafety && matchContinent && (c.name_pl.toLowerCase().includes(s) || c.iso2.toLowerCase().includes(s));
    }).sort((a, b) => a.name_pl.localeCompare(b.name_pl, 'pl'));
  }, [countries, filterSafety, filterContinent, searchQuery]);

  const scrollToSection = (id: string) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) return <div className="loader">Ładowanie TripSheet...</div>;

  return (
    <div className="app-container">
      {!selectedCountry ? (
        <>
          <header className="main-header">
            <div className="header-content">
              <div className="logo-section" onClick={() => handleSelectCountry(null)} style={{ cursor: 'pointer' }}>
                <img src={logoNoText} alt="Logo" className="app-logo" />
                <span className="logo-brand">TripSheet</span>
              </div>
              <div className="controls-section">
                <input ref={searchInputRef} type="text" placeholder="Szukaj kraju..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="search-input" />
                <button className="theme-toggle-btn" onClick={handleToggleTheme}>{theme === 'light' ? '🌙' : '☀️'}</button>
                <select value={filterSafety} onChange={e => setFilterSafety(e.target.value)} className="filter-select">
                  <option value="all">Wszystkie ryzyka</option>
                  <option value="low">🟢 Bezpiecznie</option>
                  <option value="medium">🟡 Szczególna ostrożność</option>
                  <option value="high">🟠 Odradzane</option>
                  <option value="critical">🔴 Niebezpiecznie</option>
                </select>
                <select value={filterContinent} onChange={e => setFilterContinent(e.target.value)} className="filter-select">
                  <option value="all">Wszystkie kontynenty</option>
                  {Object.entries(CONTINENT_MAP).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </div>
            </div>
          </header>
          <main className="content-area">
            {showLicense ? <LicensePage onBack={() => setShowLicense(false)} /> : (
              <>
                <div className="country-grid">
                  {countryList.map(c => (
                    <div key={c.iso2} className={`country-card risk-border-${c.safety.risk_level}`} onClick={() => handleSelectCountry(c)}>
                      <div className="card-content">
                        <img src={c.flag_url} alt={c.name_pl} className="main-flag-img" />
                        <h3>{c.name_pl}</h3>
                        <p className="card-continent">{CONTINENT_MAP[c.continent] || c.continent}</p>
                        <span className={`risk-badge risk-${c.safety.risk_level}`}>{SAFETY_LABELS[c.safety.risk_level]}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <footer className="footer-nav">
                  <a href="#license" onClick={e => { e.preventDefault(); setShowLicense(true); }}>Licencje i źródła</a>
                  <span>&copy; 2026 TripSheet</span>
                </footer>
              </>
            )}
          </main>
        </>
      ) : (
        <>
          <header className="main-header">
            <div className="header-content">
              <div className="logo-section" onClick={() => handleSelectCountry(null)} style={{ cursor: 'pointer' }}>
                <img src={logoNoText} alt="Logo" className="app-logo" />
                <span className="logo-brand">TripSheet</span>
              </div>
              <button className="theme-toggle-btn" onClick={handleToggleTheme}>{theme === 'light' ? '🌙' : '☀️'}</button>
            </div>
          </header>
          <div className="detail-view-layout">
            <aside className="side-menu">
              <button className="side-back-button" onClick={() => handleSelectCountry(null)}>← Powrót</button>
              <div className="side-menu-list">
                {SECTIONS.map(s => (
                  <button key={s.id} className={`side-menu-item ${activeSection === s.id ? 'active' : ''}`} onClick={() => scrollToSection(s.id)}>
                    <span className="side-menu-icon">{s.icon}</span> {s.label}
                  </button>
                ))}
              </div>
            </aside>
            <div className="detail-view-content">
              <div className="detail-card">
                <div id="summary" className="detail-header scroll-mt">
                  <img src={selectedCountry.flag_url} alt={selectedCountry.name_pl} className="detail-flag-img" />
                  <div className="detail-titles">
                    <h2>{selectedCountry.name_pl}</h2>
                    <p>{selectedCountry.name} ({selectedCountry.iso2})</p>
                  </div>
                  <div className="detail-map-container">
                    <ComposableMap projectionConfig={{ scale: 140 }} style={{ width: "100%", height: "100%" }}>
                      <ZoomableGroup center={mapPosition.coordinates} zoom={mapPosition.zoom} onMoveEnd={setMapPosition}>
                        <Geographies geography={geoUrl}>
                          {({ geographies }) => geographies.map((geo: any) => {
                            const isSelected = geo.id === selectedCountry.iso3 || geo.properties?.iso_a3 === selectedCountry.iso3 || geo.properties?.ADM0_A3 === selectedCountry.iso3;
                            return <Geography key={geo.rsmKey} geography={geo} fill={isSelected ? "#2b6cb0" : "#EAEAEC"} stroke="#D6D6DA" strokeWidth={0.5} style={{ default: { outline: "none" } }} />;
                          })}
                        </Geographies>
                        <Marker coordinates={[selectedCountry.longitude || 0, selectedCountry.latitude || 0]}>
                          <circle r={2} fill="#F56565" />
                        </Marker>
                      </ZoomableGroup>
                    </ComposableMap>
                  </div>
                </div>
                
                <div className="detail-body">
                  <div id="discover" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>✨</span> <label>Poznaj kraj</label></div>
                    <div className="discover-section">
                      <ExpandableText text={selectedCountry.wiki_summary || ''} />
                      {selectedCountry.national_symbols && (
                        <div className="national-symbols-bar" style={{ marginTop: '1rem' }}>
                          <strong>Symbole narodowe:</strong> {selectedCountry.national_symbols}
                        </div>
                      )}
                    </div>
                  </div>

                  <div id="docs" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>🛂</span> <label>Dokumenty i Wiza</label></div>
                    <div className="docs-grid">
                      <div className={`doc-item ${selectedCountry.entry?.passport_required ? 'doc-no' : 'doc-yes'}`}>
                        <strong>Paszport:</strong> {selectedCountry.entry?.passport_required ? 'Wymagany' : 'Niepotrzebny'}
                      </div>
                      <div className={`doc-item ${selectedCountry.entry?.id_card_allowed ? 'doc-yes' : 'doc-no'}`}>
                        <strong>Dowód osobisty:</strong> {selectedCountry.entry?.id_card_allowed ? 'Akceptowany' : 'Nieakceptowany'}
                      </div>
                      <div className="doc-item full-width">
                        <strong>Wiza (Polacy):</strong> {selectedCountry.entry?.visa_status || 'Brak szczegółowych informacji.'}
                      </div>
                    </div>
                  </div>

                  <div id="info" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>ℹ️</span> <label>Informacje ogólne</label></div>
                    <div className="basic-info-grid">
                      <div className="info-item-box"><strong>Stolica:</strong> {selectedCountry.capital}</div>
                      <div className="info-item-box"><strong>Populacja:</strong> {selectedCountry.population?.toLocaleString()}</div>
                      <div className="info-item-box"><strong>Strefa czasowa:</strong> {selectedCountry.timezone}</div>
                      <div className="info-item-box"><strong>Kod tel.:</strong> +{selectedCountry.phone_code?.replace('+', '')}</div>
                      <div className="info-item-box full"><strong>Języki:</strong> {selectedCountry.languages.map(l => l.name + (l.is_official ? ' (ofic.)' : '')).join(', ')}</div>
                    </div>
                  </div>

                  <div id="currency" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>💰</span> <label>Waluta i Kurs</label></div>
                    <div className="info-item-box">
                      <p><strong>{selectedCountry.currency.name} ({selectedCountry.currency.code})</strong></p>
                      {selectedCountry.currency.rate_pln ? (
                        <>
                          <p>1 {selectedCountry.currency.code} = <strong>{selectedCountry.currency.rate_pln.toFixed(4)} PLN</strong></p>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Przykład: 100 PLN ≈ {(100 / selectedCountry.currency.rate_pln).toFixed(2)} {selectedCountry.currency.code}
                          </p>
                        </>
                      ) : <p>Brak aktualnego kursu walutowego.</p>}
                    </div>
                  </div>

                  <div id="plugs" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>🔌</span> <label>Elektryczność i Ruch</label></div>
                    <div className="info-grid">
                      <div className="info-item-box">
                        <strong>Gniazdka (Typy):</strong>
                        <p>{selectedCountry.practical.plug_types}</p>
                      </div>
                      <div className="info-item-box">
                        <strong>Ruch drogowy:</strong>
                        <p>{selectedCountry.practical.driving_side === 'right' ? '➡️ Prawostronny' : '⬅️ Lewostronny'}</p>
                      </div>
                    </div>
                  </div>

                  <div id="emergency" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>🚨</span> <label>Numery alarmowe</label></div>
                    <div className="info-grid">
                      <div className="info-item-box" style={{ background: '#fff5f5', borderColor: '#feb2b2' }}>
                        <strong style={{ color: '#c53030' }}>POLICJA</strong>
                        <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{selectedCountry.practical.emergency?.police || '—'}</p>
                      </div>
                      <div className="info-item-box" style={{ background: '#fff5f5', borderColor: '#feb2b2' }}>
                        <strong style={{ color: '#c53030' }}>POGOTOWIE</strong>
                        <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{selectedCountry.practical.emergency?.ambulance || '—'}</p>
                      </div>
                    </div>
                  </div>

                  <div id="costs" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>📊</span> <label>Koszty życia</label></div>
                    <div className="costs-container">
                      {selectedCountry.costs?.ratio_to_pl ? (
                        <>
                          <p>Ceny są o około <strong>{Math.abs((selectedCountry.costs.ratio_to_pl - 1) * 100).toFixed(0)}% {selectedCountry.costs.ratio_to_pl > 1 ? 'wyższe' : 'niższe'}</strong> niż w Polsce.</p>
                          <div className="cost-bar-wrapper" style={{ height: '12px', background: 'var(--bg-app)', borderRadius: '6px', overflow: 'hidden', marginTop: '10px' }}>
                            <div style={{ width: `${Math.min(100, selectedCountry.costs.ratio_to_pl * 50)}%`, height: '100%', background: 'var(--primary-color)' }}></div>
                          </div>
                        </>
                      ) : <p>Brak danych statystycznych o kosztach.</p>}
                    </div>
                  </div>

                  <div id="health" className="info-block full-width scroll-mt">
                    <div className="section-header"><span>💉</span> <label>Zdrowie i Szczepienia</label></div>
                    <div className="health-container" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {selectedCountry.practical.health_info && (
                        <div className="health-full-info">
                          <strong>Zalecenia MSZ:</strong>
                          <ExpandableText text={selectedCountry.practical.health_info} />
                        </div>
                      )}
                      <div className="info-grid">
                        <div className="info-item-box">
                          <strong>Obowiązkowe szczepienia:</strong>
                          <p>{selectedCountry.practical.vaccinations_required || 'Brak danych o obowiązkowych szczepieniach.'}</p>
                        </div>
                        <div className="info-item-box">
                          <strong>Zalecane szczepienia:</strong>
                          <p>{selectedCountry.practical.vaccinations_suggested || 'Brak danych o zalecanych szczepieniach.'}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div id="safety" className={`safety-info risk-${selectedCountry.safety.risk_level} scroll-mt`}>
                    <div className="section-header"><span>🛡️</span> <label>Bezpieczeństwo (gov.pl)</label></div>
                    <p className="risk-desc">Status: <strong>{SAFETY_LABELS[selectedCountry.safety.risk_level]}</strong></p>
                    <div style={{ marginBottom: '1rem' }}>
                      <ExpandableText text={selectedCountry.safety.risk_text} maxHeight={100} />
                    </div>
                    {selectedCountry.safety.risk_details && (
                      <div className="risk-details-box" style={{ background: 'var(--bg-app)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                        <strong>Szczegóły ostrzeżenia:</strong>
                        <ExpandableText text={selectedCountry.safety.risk_details} maxHeight={200} />
                      </div>
                    )}
                    {selectedCountry.safety.url && (
                      <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="msz-link" style={{ display: 'inline-block', marginTop: '1rem', fontWeight: 'bold' }}>Pełny komunikat MSZ →</a>
                    )}
                  </div>

                  <div className="source-links-section">
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>Źródła danych:</span>
                    <a href={`https://pl.wikipedia.org/wiki/${selectedCountry.name_pl}`} target="_blank" rel="noreferrer" className="source-link">🌐 Wikipedia</a>
                    {selectedCountry.safety.url && <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="source-link">🛡️ gov.pl</a>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App
