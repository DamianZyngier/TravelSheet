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
  safety: {
    risk_level: string;
    summary: string;
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
    visa_on_arrival: boolean | null;
    visa_notes: string;
  };
}

function App() {
  const [countries, setCountries] = useState<Record<string, CountryData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<CountryData | null>(null);
  
  // Filtry
  const [filterSafety, setFilterSafety] = useState<string>('all');
  const [filterContinent, setFilterContinent] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

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

  const filteredCountries = useMemo(() => {
    return Object.values(countries).filter(c => {
      const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
      const matchContinent = filterContinent === 'all' || c.continent === filterContinent;
      const matchSearch = c.name_pl.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          c.iso2.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchSafety && matchContinent && matchSearch;
    });
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
              {continents.map(c => <option key={c} value={c}>{c}</option>)}
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
          {filteredCountries.length > 0 ? (
            filteredCountries.map(country => (
              <div 
                key={country.iso2} 
                className={`country-card risk-border-${country.safety.risk_level}`}
                onClick={() => setSelectedCountry(country)}
              >
                <span className="flag-icon">{country.flag_emoji}</span>
                <div className="card-info">
                  <h3>{country.name_pl}</h3>
                  <p className="card-continent">{country.continent}</p>
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
              <span className="modal-flag">{selectedCountry.flag_emoji}</span>
              <div className="modal-titles">
                <h2>{selectedCountry.name_pl}</h2>
                <p>{selectedCountry.name} ({selectedCountry.iso2})</p>
              </div>
            </div>

            <div className="modal-body">
              <div className="info-grid">
                <div className="info-block">
                  <label>Stolica</label>
                  <span>{selectedCountry.capital || 'Brak danych'}</span>
                </div>
                <div className="info-block">
                  <label>Waluta</label>
                  <span>{selectedCountry.currency.code} ({selectedCountry.currency.rate_pln ? `${selectedCountry.currency.rate_pln.toFixed(2)} PLN` : 'brak kursu'})</span>
                </div>
                <div className="info-block">
                  <label>Gniazdka</label>
                  <span>{selectedCountry.practical.plug_types || 'Brak danych'}</span>
                </div>
                <div className="info-block">
                  <label>Ruch</label>
                  <span>{selectedCountry.practical.driving_side === 'right' ? 'Prawostronny' : 'Lewostronny'}</span>
                </div>
                <div className="info-block">
                  <label>Wiza (Polacy)</label>
                  <span>{selectedCountry.entry?.visa_required === true ? 'Wymagana' : (selectedCountry.entry?.visa_required === false ? 'Bezwizowy' : 'Brak danych')}</span>
                </div>
              </div>

              <div className={`safety-info risk-${selectedCountry.safety.risk_level}`}>
                <h4>⚠️ Poziom bezpieczeństwa: {selectedCountry.safety.risk_level.toUpperCase()}</h4>
                <p>{selectedCountry.safety.summary || 'Brak szczegółowego opisu bezpieczeństwa.'}</p>
                {selectedCountry.safety.url && (
                  <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="msz-link">
                    Zobacz pełny komunikat MSZ na gov.pl
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
