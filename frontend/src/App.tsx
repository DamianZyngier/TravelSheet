import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import Header from './components/layout/Header'
import Sidebar from './components/layout/Sidebar'
import Footer from './components/layout/Footer'
import LegalModal from './components/layout/LegalModal'
import CountryGrid from './components/country/CountryGrid'
import CountryDetail from './components/country/CountryDetail'
import type { CountryData } from './types'
import { SECTIONS, ALIASES } from './constants'
import './App.css'
import logoNoText from './assets/logo-no-text.png'
import { 
  formatPLN, 
  getCurrencyExample, 
  checkPlugs, 
  getEnlargedPlugUrl, 
  getMapSettings 
} from './utils/helpers'

function App() {
  const [countries, setCountries] = useState<Record<string, CountryData>>({})
  const [loading, setLoading] = useState(true)
  const [selectedCountry, setSelectedCountry] = useState<CountryData | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterContinent, setFilterContinent] = useState('all')
  const [filterSafety, setFilterSafety] = useState('all')
  const [activeSection, setActiveSection] = useState('summary')
  const [error, setError] = useState<string | null>(null)
  const [favorites, setFavorites] = useState<string[]>(() => {
    const saved = localStorage.getItem('travelsheet_favorites');
    return saved ? JSON.parse(saved) : [];
  })
  const [showOnlyFavorites, setShowOnlyFavorites] = useState(false)
  const [legalModal, setLegalModal] = useState<{ isOpen: boolean, type: 'terms' | 'license' }>({ isOpen: false, type: 'terms' })
  
  const [mapPosition, setMapPosition] = useState<{ coordinates: [number, number], zoom: number }>({ coordinates: [0, 0], zoom: 1 })
  const searchInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch('data.json')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        setCountries(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error loading data:", err)
        setError(`Błąd ładowania danych: ${err.message}`)
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    localStorage.setItem('travelsheet_favorites', JSON.stringify(favorites));
  }, [favorites]);

  const toggleFavorite = (iso2: string) => {
    setFavorites(prev => 
      prev.includes(iso2) ? prev.filter(i => i !== iso2) : [...prev, iso2]
    );
  };

  const continents = useMemo(() => {
    try {
      if (!countries || typeof countries !== 'object' || Object.keys(countries).length === 0) return [];
      return Array.from(new Set(Object.values(countries).map(c => c?.continent).filter(Boolean))).sort()
    } catch (e) {
      console.error("Error computing continents:", e);
      return [];
    }
  }, [countries])

  const handleSelectCountry = useCallback((country: CountryData | null) => {
    setSelectedCountry(country)
    if (country) {
      setMapPosition({
        coordinates: [country.longitude || 0, country.latitude || 0],
        zoom: getMapSettings(country).zoom
      })
      window.scrollTo(0, 0)
      setActiveSection('summary')
      
      const url = new URL(window.location.href);
      url.searchParams.set('country', country.iso2);
      window.history.pushState({}, '', url.toString());
    } else {
      window.scrollTo(0, 0)
      const url = new URL(window.location.href);
      url.searchParams.delete('country');
      url.searchParams.delete('kraj');
      window.history.pushState({}, '', url.toString());
    }
  }, [])

  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const countryIso = params.get('country') || params.get('kraj');
      if (countryIso && countries[countryIso]) {
        setSelectedCountry(countries[countryIso]);
      } else {
        setSelectedCountry(null);
      }
    };

    window.addEventListener('popstate', handlePopState);
    
    if (!loading && Object.keys(countries).length > 0) {
      const params = new URLSearchParams(window.location.search);
      const countryIso = params.get('country') || params.get('kraj');
      if (countryIso && countries[countryIso]) {
        setSelectedCountry(countries[countryIso]);
      }
    }

    return () => window.removeEventListener('popstate', handlePopState);
  }, [countries, loading]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
      setActiveSection(id)
    }
  }

  useEffect(() => {
    if (!selectedCountry) return;

    const options = {
      root: null,
      rootMargin: '-150px 0px -50% 0px',
      threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setActiveSection(entry.target.id);
        }
      });
    }, options);

    SECTIONS.forEach(section => {
      const el = document.getElementById(section.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [selectedCountry]);

  const countryList = useMemo(() => {
    if (!countries || typeof countries !== 'object') return [];
    return Object.values(countries)
      .filter(c => {
        if (!c || !c.safety) return false;
        
        if (showOnlyFavorites && !favorites.includes(c.iso2)) return false;

        const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
        const matchContinent = filterContinent === 'all' || c.continent === filterContinent;
        
        const searchLower = searchQuery.toLowerCase();
        const countryAliases = ALIASES[c.iso2] || [];
        
        const matchSearch = (c.name_pl || '').toLowerCase().includes(searchLower) || 
                            (c.name || '').toLowerCase().includes(searchLower) ||
                            (c.iso2 || '').toLowerCase().includes(searchLower) ||
                            (c.iso3 || '').toLowerCase().includes(searchLower) ||
                            countryAliases.some(alias => alias.includes(searchLower));
        
        return matchSafety && matchContinent && matchSearch;
      })
      .sort((a, b) => (a.name_pl || '').localeCompare(b.name_pl || '', 'pl'));
  }, [countries, filterSafety, filterContinent, searchQuery, showOnlyFavorites, favorites]);

  const sortedFullList = useMemo(() => {
    if (!countries || typeof countries !== 'object') return [];
    return Object.values(countries).sort((a, b) => (a.name_pl || '').localeCompare(b.name_pl || '', 'pl'));
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

  if (error && Object.keys(countries).length === 0) {
    return (
      <div className="app-container">
        <header className="main-header">
          <div className="header-content">
            <div className="logo-section">
              <img src={logoNoText} alt="TripSheet" className="app-logo" />
              <div className="logo-text">
                <span className="logo-brand">TripSheet</span>
              </div>
            </div>
          </div>
        </header>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Coś poszło nie tak</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-btn">Spróbuj ponownie</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container" onContextMenu={() => true}>
      {!selectedCountry ? (
        <>
          <Header 
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            filterContinent={filterContinent}
            setFilterContinent={setFilterContinent}
            filterSafety={filterSafety}
            setFilterSafety={setFilterSafety}
            showOnlyFavorites={showOnlyFavorites}
            setShowOnlyFavorites={setShowOnlyFavorites}
            continents={continents}
            onLogoClick={() => handleSelectCountry(null)}
            searchInputRef={searchInputRef}
          />

          <main className="content-area">
            <div className="hero-intro-v2">
              <div className="hero-icon">🗺️</div>
              <div className="hero-content-text">
                <h1>Witaj w TripSheet</h1>
                <p>
                  Twoje centrum bezpiecznych podróży. Agregujemy aktualne dane z zaufanych źródeł:
                  <span className="source-chip msz">MSZ (gov.pl)</span>
                  <span className="source-chip cdc">CDC Health</span>
                  <span className="source-chip unesco">UNESCO</span>
                  oraz <span className="source-chip wiki">Wikidata</span>.
                </p>
              </div>
            </div>

            <CountryGrid 
              countryList={countryList} 
              onSelectCountry={handleSelectCountry}
              favorites={favorites}
              toggleFavorite={toggleFavorite}
            />
          </main>

          <Footer 
            onOpenTerms={() => setLegalModal({ isOpen: true, type: 'terms' })}
            onOpenLicense={() => setLegalModal({ isOpen: true, type: 'license' })}
          />
        </>
      ) : (
        <div className="detail-view-layout">
          <Sidebar 
            selectedCountry={selectedCountry}
            sortedFullList={sortedFullList}
            onSelectCountry={handleSelectCountry}
            activeSection={activeSection}
            scrollToSection={scrollToSection}
            navigateCountry={navigateCountry}
          />

          <div className="detail-view-content">
            <div className="detail-actions-top">
               <button 
                className={`favorite-btn-large ${favorites.includes(selectedCountry.iso2) ? 'is-fav' : ''}`}
                onClick={() => toggleFavorite(selectedCountry.iso2)}
               >
                 {favorites.includes(selectedCountry.iso2) ? '⭐ Zapamiętany' : '☆ Zapamiętaj kraj'}
               </button>
            </div>
            <CountryDetail 
              selectedCountry={selectedCountry}
              allCountries={sortedFullList}
              onSelectCountry={handleSelectCountry}
              mapPosition={mapPosition}
              setMapPosition={setMapPosition}
              getMapSettings={getMapSettings}
              formatPLN={formatPLN}
              getCurrencyExample={getCurrencyExample}
              checkPlugs={checkPlugs}
              getEnlargedPlugUrl={getEnlargedPlugUrl}
            />
          </div>
        </div>
      )}

      <LegalModal 
        isOpen={legalModal.isOpen} 
        title={legalModal.type === 'terms' ? 'Regulamin Serwisu' : 'Licencja i Prawa Autorskie'}
        onClose={() => setLegalModal({ ...legalModal, isOpen: false })}
      >
        {legalModal.type === 'terms' ? (
          <div className="legal-text">
            <h3>1. Postanowienia ogólne</h3>
            <p>TripSheet jest agregatorem danych publicznych mającym na celu ułatwienie planowania podróży. Dane pochodzą z zewnętrznych źródeł (MSZ, CDC, UNESCO, Wikidata, Open-Meteo).</p>
            
            <h3>2. Odpowiedzialność</h3>
            <p>Informacje prezentowane w serwisie mają charakter wyłącznie informacyjny. Autor serwisu nie ponosi odpowiedzialności za jakiekolwiek szkody wynikające z błędnych danych lub ich nieaktualności. Zawsze weryfikuj dane w oficjalnych źródłach rządowych.</p>
            
            <h3>3. Prawa autorskie</h3>
            <p>Struktura serwisu, kod źródłowy oraz sposób prezentacji danych są chronione prawem autorskim.</p>
          </div>
        ) : (
          <div className="legal-text">
            <h3>Licencja Danych i Oprogramowania</h3>
            <p>Wszystkie dane zagregowane w niniejszym serwisie są udostępniane użytkownikowi końcowemu wyłącznie do użytku osobistego.</p>
            <div style={{ padding: '1rem', backgroundColor: '#fff5f5', borderLeft: '4px solid #f56565', margin: '1rem 0' }}>
              <strong>BARDZO WAŻNE:</strong> Zakazuje się kopiowania, redystrybucji, odsprzedaży oraz jakiegokolwiek publicznego rozpowszechniania bazy danych oraz treści serwisu TripSheet bez wyraźnej, pisemnej zgody autora.
            </div>
            <p>Naruszenie tych warunków może skutkować podjęciem kroków prawnych.</p>
          </div>
        )}
      </LegalModal>
    </div>
  )
}

export default App
