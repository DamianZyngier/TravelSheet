import { useState, useEffect } from 'react'
import './App.css'

interface CountryData {
  name: string;
  iso2: string;
  capital: string;
  continent: string;
  flag_emoji: string;
  safety: {
    risk_level: string;
    summary: string;
  };
  currency: {
    code: string;
    rate_pln: number | null;
  };
}

function App() {
  const [countries, setCountries] = useState<Record<string, CountryData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Na GitHub Pages plik data.json będzie w tym samym folderze co index.html
    fetch('./data.json')
      .then(res => {
        if (!res.ok) throw new Error('Nie udało się pobrać danych');
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

  if (loading) return <div>Ładowanie danych podróżniczych...</div>;
  if (error) return <div>Błąd: {error}</div>;

  const countryList = Object.values(countries);

  return (
    <div className="app-container">
      <header>
        <h1>🌍 TravelSheet</h1>
        <p>Twoje centrum informacji o świecie</p>
      </header>

      <div className="country-grid">
        {countryList.map(country => (
          <div key={country.iso2} className="country-card">
            <span className="flag">{country.flag_emoji}</span>
            <h2>{country.name}</h2>
            <p><strong>Stolica:</strong> {country.capital}</p>
            <p><strong>Bezpieczeństwo:</strong> 
              <span className={`risk-${country.safety.risk_level}`}>
                {country.safety.risk_level}
              </span>
            </p>
            {country.currency.rate_pln && (
              <p><strong>Kurs:</strong> 1 {country.currency.code} = {country.currency.rate_pln.toFixed(2)} PLN</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
