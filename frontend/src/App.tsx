import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import Header from './components/layout/Header'
import Sidebar from './components/layout/Sidebar'
import Footer from './components/layout/Footer'
import LegalModal from './components/layout/LegalModal'
import CountryGrid from './components/country/CountryGrid'
import CountryDetail from './components/country/CountryDetail'
import ChecklistSection from './components/checklist/ChecklistSection'
import PassengerRightsSection from './components/static/PassengerRightsSection'
import type { CountryData } from './types/index'
import { ALIASES } from './constants'
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
  const [activeChecklist, setActiveChecklist] = useState<string | null>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('checklist');
  })
  const [activeStaticPage, setActiveStaticPage] = useState<string | null>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('page');
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [filterContinent, setFilterContinent] = useState('all')
  const [filterSafety, setFilterSafety] = useState('all')
  const [filterTravelType, setFilterTravelType] = useState('all')
  const [activeSection, setActiveSection] = useState('summary')
  const isManualScrollRef = useRef(false)
  const manualScrollTimeoutRef = useRef<number | null>(null)
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
      setActiveChecklist(null)
      setMapPosition({
        coordinates: [country.longitude || 0, country.latitude || 0],
        zoom: getMapSettings(country).zoom
      })
      window.scrollTo(0, 0)
      setActiveSection('summary')
      
      const url = new URL(window.location.href);
      url.searchParams.delete('checklist');
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

  const handleOpenChecklist = useCallback((variant: string = 'minimum') => {
    setActiveChecklist(variant)
    localStorage.setItem('travelsheet_last_checklist', variant);
    setSelectedCountry(null)
    setActiveStaticPage(null)
    window.scrollTo(0, 0)
    
    const url = new URL(window.location.href);
    url.searchParams.delete('country');
    url.searchParams.delete('kraj');
    url.searchParams.delete('page');
    url.searchParams.set('checklist', variant);
    window.history.pushState({}, '', url.toString());
  }, [])

  const handleOpenPassengerRights = useCallback(() => {
    setActiveStaticPage('passenger-rights')
    setSelectedCountry(null)
    setActiveChecklist(null)
    window.scrollTo(0, 0)

    const url = new URL(window.location.href);
    url.searchParams.delete('country');
    url.searchParams.delete('kraj');
    url.searchParams.delete('checklist');
    url.searchParams.set('page', 'passenger-rights');
    window.history.pushState({}, '', url.toString());
  }, [])

  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const countryIso = params.get('country') || params.get('kraj');
      const checklistVar = params.get('checklist');
      const pageVar = params.get('page');
      
      if (countryIso && countries[countryIso]) {
        setSelectedCountry(countries[countryIso]);
        setActiveChecklist(null);
        setActiveStaticPage(null);
      } else if (checklistVar) {
        setActiveChecklist(checklistVar);
        localStorage.setItem('travelsheet_last_checklist', checklistVar);
        setSelectedCountry(null);
        setActiveStaticPage(null);
      } else if (pageVar) {
        setActiveStaticPage(pageVar);
        setSelectedCountry(null);
        setActiveChecklist(null);
      } else {
        setSelectedCountry(null);
        setActiveChecklist(null);
        setActiveStaticPage(null);
      }
    };

    window.addEventListener('popstate', handlePopState);
    
    if (!loading && Object.keys(countries).length > 0) {
      const params = new URLSearchParams(window.location.search);
      const countryIso = params.get('country') || params.get('kraj');
      const checklistVar = params.get('checklist');
      const pageVar = params.get('page');
      
      if (countryIso && countries[countryIso]) {
        setSelectedCountry(countries[countryIso]);
        setActiveChecklist(null);
        setActiveStaticPage(null);
      } else if (checklistVar) {
        setActiveChecklist(checklistVar);
        localStorage.setItem('travelsheet_last_checklist', checklistVar);
        setSelectedCountry(null);
        setActiveStaticPage(null);
      } else if (pageVar) {
        setActiveStaticPage(pageVar);
        setSelectedCountry(null);
        setActiveChecklist(null);
      }
    }

    return () => window.removeEventListener('popstate', handlePopState);
  }, [countries, loading]);

  useEffect(() => {
    const handleNavChecklist = () => {
      const lastVariant = localStorage.getItem('travelsheet_last_checklist') || 'minimum';
      handleOpenChecklist(lastVariant);
    };
    const handleNavPassengerRights = () => {
      handleOpenPassengerRights();
    };
    window.addEventListener('nav-checklist', handleNavChecklist);
    window.addEventListener('nav-passenger-rights', handleNavPassengerRights);
    return () => {
      window.removeEventListener('nav-checklist', handleNavChecklist);
      window.removeEventListener('nav-passenger-rights', handleNavPassengerRights);
    };
  }, [handleOpenChecklist, handleOpenPassengerRights]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      if (manualScrollTimeoutRef.current) {
        window.clearTimeout(manualScrollTimeoutRef.current);
      }
      isManualScrollRef.current = true;
      setActiveSection(id);
      element.scrollIntoView({ behavior: 'smooth' });
      
      // Reset the manual scroll flag after smooth scroll is likely finished
      manualScrollTimeoutRef.current = window.setTimeout(() => {
        isManualScrollRef.current = false;
        manualScrollTimeoutRef.current = null;
      }, 1000);
    }
  }

  useEffect(() => {
    if (!selectedCountry) return;

    const options = {
      root: null,
      rootMargin: '-10% 0px -85% 0px',
      threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
      // Ignore observer updates if we are currently manually scrolling (clicked a sidebar item)
      if (isManualScrollRef.current) return;

      const intersecting = entries
        .filter(entry => entry.isIntersecting)
        .sort((a, b) => a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top);

      if (intersecting.length > 0) {
        setActiveSection(intersecting[0].target.id);
      }
    }, options);

    const targetIds = ['summary', 'category-1', 'category-2', 'category-3', 'category-4', 'category-5'];
    targetIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    // Handle edge cases: very top and very bottom
    const handleScroll = () => {
      if (isManualScrollRef.current) return;

      const scrollPos = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;

      if (scrollPos < 100) {
        setActiveSection('summary');
      } else if (scrollPos + windowHeight >= documentHeight - 50) {
        setActiveSection('category-5');
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
    };
  }, [selectedCountry]);

  // Filtering logic
  const baseFilteredList = useMemo(() => {
    if (!countries || typeof countries !== 'object') return [];
    return Object.values(countries)
      .filter(c => {
        if (!c || !c.safety) return false;
        
        const matchSafety = filterSafety === 'all' || c.safety.risk_level === filterSafety;
        const matchContinent = filterContinent === 'all' || c.continent === filterContinent;
        const matchTravelType = filterTravelType === 'all' || (c.travel_types?.categories || []).includes(filterTravelType);
        
        const searchLower = searchQuery.toLowerCase();
        const countryAliases = ALIASES[c.iso2] || [];
        
        const matchSearch = (c.name_pl || '').toLowerCase().includes(searchLower) || 
                            (c.name || '').toLowerCase().includes(searchLower) ||
                            (c.iso2 || '').toLowerCase().includes(searchLower) ||
                            (c.iso3 || '').toLowerCase().includes(searchLower) ||
                            countryAliases.some(alias => alias.includes(searchLower));
        
        return matchSafety && matchContinent && matchTravelType && matchSearch;
      })
      .sort((a, b) => (a.name_pl || '').localeCompare(b.name_pl || '', 'pl'));
  }, [countries, filterSafety, filterContinent, filterTravelType, searchQuery]);

  // Split into favorites and non-favorites if "Ulubione" is active
  const { favoriteList, remainingList } = useMemo(() => {
    if (!showOnlyFavorites) {
      return { favoriteList: [], remainingList: baseFilteredList };
    }
    const favs = baseFilteredList.filter(c => favorites.includes(c.iso2));
    const rest = baseFilteredList.filter(c => !favorites.includes(c.iso2));
    return { favoriteList: favs, remainingList: rest };
  }, [baseFilteredList, showOnlyFavorites, favorites]);

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

  const handlePrintCountry = () => {
    window.print();
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!selectedCountry && !activeChecklist && (e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }

      if (e.key === 'Backspace' && (selectedCountry || activeChecklist)) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          handleSelectCountry(null);
          setActiveChecklist(null);
        }
      }

      if (e.key === 'Enter' && !selectedCountry && !activeChecklist && baseFilteredList.length === 1) {
        handleSelectCountry(baseFilteredList[0]);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedCountry, activeChecklist, baseFilteredList, handleSelectCountry]);

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
      {!selectedCountry && !activeChecklist && !activeStaticPage ? (
        <>
          <Header 
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            filterContinent={filterContinent}
            setFilterContinent={setFilterContinent}
            filterSafety={filterSafety}
            setFilterSafety={setFilterSafety}
            filterTravelType={filterTravelType}
            setFilterTravelType={setFilterTravelType}
            showOnlyFavorites={showOnlyFavorites}
            setShowOnlyFavorites={setShowOnlyFavorites}
            continents={continents}
            onLogoClick={() => handleSelectCountry(null)}
            searchInputRef={searchInputRef}
          />

          <main className="content-area">
            <CountryGrid 
              favoriteList={favoriteList}
              remainingList={remainingList}
              showOnlyFavorites={showOnlyFavorites}
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
      ) : activeStaticPage === 'passenger-rights' ? (
        <PassengerRightsSection 
          onBack={() => {
            setActiveStaticPage(null);
            const url = new URL(window.location.href);
            url.searchParams.delete('page');
            window.history.pushState({}, '', url.toString());
          }} 
        />
      ) : activeChecklist ? (
        <ChecklistSection 
          variantId={activeChecklist}
          onBack={() => {
            setActiveChecklist(null);
            const url = new URL(window.location.href);
            url.searchParams.delete('checklist');
            window.history.pushState({}, '', url.toString());
          }} 
          onVariantChange={(v) => {
            setActiveChecklist(v);
            localStorage.setItem('travelsheet_last_checklist', v);
            const url = new URL(window.location.href);
            url.searchParams.set('checklist', v);
            window.history.pushState({}, '', url.toString());
          }}
        />
      ) : (
        <div className="detail-view-layout">
          <Sidebar 
            selectedCountry={selectedCountry!}
            sortedFullList={sortedFullList}
            onSelectCountry={handleSelectCountry}
            activeSection={activeSection}
            scrollToSection={scrollToSection}
            navigateCountry={navigateCountry}
          />

          <div className="detail-view-content">
            <div className="detail-actions-top no-print">
               <button 
                className="print-country-btn"
                onClick={handlePrintCountry}
                style={{
                  marginRight: '1rem',
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  background: 'white',
                  cursor: 'pointer',
                  fontWeight: '600',
                  color: '#4a5568'
                }}
               >
                 🖨️ PDF / Drukuj dane kraju
               </button>
               <button 
                className={`favorite-btn-large ${favorites.includes(selectedCountry!.iso2) ? 'is-fav' : ''}`}
                onClick={() => toggleFavorite(selectedCountry!.iso2)}
               >
                 {favorites.includes(selectedCountry!.iso2) ? '⭐ Zapamiętany' : '☆ Zapamiętaj kraj'}
               </button>
            </div>
            <CountryDetail 
              selectedCountry={selectedCountry!}
              allCountries={sortedFullList}
              onSelectCountry={handleSelectCountry}
              mapPosition={mapPosition}
              setMapPosition={setMapPosition}
              getMapSettings={getMapSettings}
              formatPLN={formatPLN}
              getCurrencyExample={getCurrencyExample}
              checkPlugs={checkPlugs}
              getEnlargedPlugUrl={getEnlargedPlugUrl}
              activeSection={activeSection}
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
