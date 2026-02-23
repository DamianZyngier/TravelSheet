import { useState, useEffect, useMemo } from 'react'
import './App.css'

interface CountryData {
  name: string;
  name_pl: string;
  iso2: string;
  iso3: string;
  capital: string;
  continent: string;
  flag_emoji: string;
  flag_url: string;
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

  useEffect(() => {
    fetch('./data.json')
      .then(res => {
        if (!res.ok) throw new Error('Błąd pobierania danych');
        return res.json();
      })
      .then(data => {
        setCountries(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

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
      
      <header className="main-header">
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
              <option value="low">Niskie ryzyko</option>
              <option value="medium">Średnie ryzyko</option>
              <option value="high">Wysokie ryzyko</option>
              <option value="critical">Ekstremalne ryzyko</option>
            </select>
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
                onClick={() => setSelectedCountry(country)}
              >
                <div className="card-content">
                  <img src={country.flag_url} alt={`Flaga ${country.name_pl}`} className="main-flag-img" />
                  <h3>{country.name_pl}</h3>
                  <p className="card-continent">{CONTINENT_MAP[country.continent] || country.continent}</p>
                  <span className={`risk-badge risk-${country.safety.risk_level}`}>
                    {country.safety.risk_level}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="no-results">Nie znaleziono krajów spełniających kryteria.</div>
          )}
        </div>
      </main>

      {selectedCountry && (
        <div className="modal-overlay" onClick={() => setSelectedCountry(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-modal" onClick={() => setSelectedCountry(null)}>×</button>
            
            <div className="modal-header">
              <img src={selectedCountry.flag_url} alt={`Flaga ${selectedCountry.name_pl}`} className="modal-flag-img" />
              <div className="modal-titles">
                <h2>{selectedCountry.name_pl}</h2>
                <p>{selectedCountry.name} ({selectedCountry.iso2})</p>
              </div>
            </div>

            <div className="modal-body">
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
                          <img 
                            src={`https://www.worldstandards.eu/wp-content/uploads/plug-type-${type.trim().toLowerCase()}-300x300.jpg`} 
                            alt={`Typ ${type}`}
                            className="plug-img"
                            onError={(e) => (e.currentTarget.style.display = 'none')}
                          />
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
                    {selectedCountry.practical.driving_side === 'right' ? '🚗 Prawostronny' : '🏎️ Lewostronny'}
                  </span>
                </div>
              </div>

              <div className={`safety-info risk-${selectedCountry.safety.risk_level}`}>
                <h4>🛡️ Bezpieczeństwo (MSZ)</h4>
                <p className="risk-desc">{selectedCountry.safety.risk_text}</p>
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
