import { useState, useEffect, useMemo } from 'react'
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
  Sphere,
  Graticule
} from 'react-simple-maps'
import './App.css'

const geoUrl = "https://raw.githubusercontent.com/lotusms/world-map-data/main/world.json"

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
  const [filterDriving, setFilterDriving] = useState<string>('all');
  const [filterVisa, setFilterVisa] = useState<string>('all');

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

  const filteredCountries = useMemo(() => {
    return Object.values(countries).filter(c => {
      const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
      const matchDriving = filterDriving === 'all' || c.practical.driving_side === filterDriving;
      const matchVisa = filterVisa === 'all' || 
        (filterVisa === 'required' && c.entry?.visa_required === true) ||
        (filterVisa === 'free' && c.entry?.visa_required === false);
      
      return matchSafety && matchDriving && matchVisa;
    });
  }, [countries, filterSafety, filterDriving, filterVisa]);

  const getSafetyColor = (risk: string) => {
    switch (risk) {
      case 'low': return '#4ade80';
      case 'medium': return '#facc15';
      case 'high': return '#f87171';
      case 'critical': return '#991b1b';
      default: return '#e2e8f0';
    }
  };

  if (loading) return <div className="loader">Ładowanie mapy świata...</div>;

  return (
    <div className="app-container">
      <aside className="sidebar">
        <header>
          <h1>🌍 TravelSheet</h1>
          <p>Informacje MSZ i dane praktyczne</p>
        </header>

        <section className="filters">
          <h3>Filtry</h3>
          <div className="filter-group">
            <label>Bezpieczeństwo:</label>
            <select value={filterSafety} onChange={e => setFilterSafety(e.target.value)}>
              <option value="all">Wszystkie</option>
              <option value="low">Niskie ryzyko</option>
              <option value="medium">Średnie ryzyko</option>
              <option value="high">Wysokie ryzyko</option>
              <option value="critical">Ekstremalne</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Ruch drogowy:</label>
            <select value={filterDriving} onChange={e => setFilterDriving(e.target.value)}>
              <option value="all">Dowolny</option>
              <option value="right">Prawostronny</option>
              <option value="left">Lewostronny</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Wiza (Polacy):</label>
            <select value={filterVisa} onChange={e => setFilterVisa(e.target.value)}>
              <option value="all">Dowolna</option>
              <option value="required">Wymagana</option>
              <option value="free">Ruch bezwizowy</option>
            </select>
          </div>
        </section>

        {selectedCountry ? (
          <section className="details-panel active">
            <button className="close-btn" onClick={() => setSelectedCountry(null)}>×</button>
            <div className="detail-header">
              <span className="big-flag">{selectedCountry.flag_emoji}</span>
              <h2>{selectedCountry.name_pl}</h2>
              <p className="orig-name">{selectedCountry.name}</p>
            </div>
            
            <div className="info-grid">
              <div className="info-item">
                <strong>Stolica:</strong> {selectedCountry.capital}
              </div>
              <div className="info-item">
                <strong>Waluta:</strong> {selectedCountry.currency.code} 
                ({selectedCountry.currency.rate_pln ? `${selectedCountry.currency.rate_pln.toFixed(2)} PLN` : 'brak danych'})
              </div>
              <div className="info-item">
                <strong>Gniazdka:</strong> {selectedCountry.practical.plug_types}
              </div>
              <div className="info-item">
                <strong>Ruch:</strong> {selectedCountry.practical.driving_side === 'right' ? 'Prawostronny' : 'Lewostronny'}
              </div>
            </div>

            <div className={`safety-box risk-${selectedCountry.safety.risk_level}`}>
              <h4>Status MSZ: {selectedCountry.safety.risk_level.toUpperCase()}</h4>
              <p>{selectedCountry.safety.summary || 'Brak szczegółowego opisu.'}</p>
              {selectedCountry.safety.url && (
                <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer">Pełne info na gov.pl</a>
              )}
            </div>
          </section>
        ) : (
          <div className="placeholder-text">
            Kliknij kraj na mapie, aby zobaczyć szczegóły. <br/>
            Wyświetlam <strong>{filteredCountries.length}</strong> krajów.
          </div>
        )}
      </aside>

      <main className="map-area">
        <ComposableMap projectionConfig={{ rotate: [-10, 0, 0], scale: 147 }}>
          <ZoomableGroup>
            <Sphere stroke="#E4E5E6" strokeWidth={0.5} fill="transparent" id="sphere" />
            <Graticule stroke="#E4E5E6" strokeWidth={0.5} id="graticule" />
            <Geographies geography={geoUrl}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const country = Object.values(countries).find(c => c.iso3 === geo.id || c.iso3 === geo.properties.ISO_A3);
                  const isFiltered = country && filteredCountries.find(fc => fc.iso3 === country.iso3);
                  
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      onClick={() => country && setSelectedCountry(country)}
                      style={{
                        default: {
                          fill: isFiltered ? getSafetyColor(country.safety.risk_level) : "#F5F4F6",
                          outline: "none",
                          stroke: "#D6D6DA",
                          strokeWidth: 0.5
                        },
                        hover: {
                          fill: "#3b82f6",
                          outline: "none",
                          cursor: "pointer"
                        },
                        pressed: {
                          fill: "#2563eb",
                          outline: "none"
                        }
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>
      </main>
    </div>
  )
}

export default App
