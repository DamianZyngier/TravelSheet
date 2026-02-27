import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import Header from './components/layout/Header'
import Sidebar from './components/layout/Sidebar'
import CountryGrid from './components/country/CountryGrid'
import CountryDetail from './components/country/CountryDetail/CountryDetail'
import { CountryData } from './types'
import { SECTIONS } from './constants'
import './App.css'
import logoNoText from './assets/logo-no-text.png'
import { 
  formatPLN, 
  getCurrencyExample, 
  checkPlugs, 
  getEnlargedPlugUrl, 
  getMapSettings 
} from './utils/helpers'

const ALIASES: Record<string, string[]> = {
  'GB': ['wielka brytania', 'anglia', 'szkocja', 'uk', 'united kingdom'],
  'US': ['usa', 'stany zjednoczone', 'america', 'united states'],
  'PL': ['polska', 'poland'],
  'DE': ['niemcy', 'germany'],
  'FR': ['francja', 'france'],
  'IT': ['włochy', 'italy'],
  'ES': ['hiszpania', 'spain'],
  'TR': ['turcja', 'turkey'],
  'EG': ['egipt', 'egypt'],
  'TH': ['tajlandia', 'thailand'],
  'AE': ['dubaj', 'zjednoczone emiraty arabskie', 'emiraty', 'uae'],
  'LK': ['cejlon', 'sri lanka'],
  'MV': ['malediwy', 'maldives'],
  'SC': ['seszele', 'seychelles'],
  'MU': ['mauritius'],
  'TZ': ['zanzibar', 'tanzania'],
  'KE': ['kenia', 'kenya'],
  'DO': ['dominikana', 'dominican republic'],
  'MX': ['meksyk', 'mexico'],
  'CU': ['kuba', 'cuba'],
  'CV': ['wyspy zielonego przylądka', 'cape verde'],
  'PT': ['portugalia', 'madeira', 'madera', 'azory'],
  'GR': ['grecja', 'kreta', 'rodos', 'zakynthos', 'corfu'],
  'CY': ['cypr', 'cyprus'],
  'HR': ['chorwacja', 'croatia'],
  'ME': ['czarnogóra', 'montenegro'],
  'AL': ['albania'],
  'BG': ['bułgaria', 'bulgaria'],
  'RO': ['rumunia', 'romania'],
  'GE': ['gruzja', 'georgia'],
  'AM': ['armenia'],
  'JO': ['jordania', 'jordan'],
  'IL': ['izrael', 'israel'],
  'QA': ['katar', 'qatar'],
  'SA': ['arabia saudyjska', 'saudi arabia'],
  'OM': ['oman'],
  'MA': ['maroko', 'morocco'],
  'TN': ['tunezja', 'tunisia'],
  'ZA': ['rpa', 'south africa'],
  'IS': ['islandia', 'iceland'],
  'NO': ['norwegia', 'norway'],
  'SE': ['szwecja', 'sweden'],
  'FI': ['finlandia', 'finland'],
  'DK': ['dania', 'denmark'],
  'CH': ['szwajcaria', 'switzerland'],
  'AT': ['austria'],
  'NL': ['holandia', 'netherlands'],
  'BE': ['belgia', 'belgium'],
  'IE': ['irlandia', 'ireland'],
  'CZ': ['czechy', 'czech republic'],
  'SK': ['słowacja', 'slovakia'],
  'HU': ['węgry', 'hungary'],
  'UA': ['ukraina', 'ukraine'],
  'JP': ['japonia', 'japan'],
  'CN': ['chiny', 'china'],
  'KR': ['korea południowa', 'korea'],
  'VN': ['wietnam', 'vietnam'],
  'KH': ['kambodża', 'cambodia'],
  'LA': ['laos'],
  'ID': ['indonezja', 'bali', 'indonesia'],
  'MY': ['malezja', 'malaysia'],
  'SG': ['singapur', 'singapore'],
  'PH': ['filipiny', 'philippines'],
  'AU': ['australia'],
  'NZ': ['nowa zelandia', 'new zealand'],
  'CA': ['kanada', 'canada'],
  'BR': ['brazylia', 'brazil'],
  'AR': ['argentyna', 'argentina'],
  'CL': ['czile', 'chile'],
  'PE': ['peru'],
  'CO': ['kolumbia', 'colombia'],
  'CR': ['kostaryka', 'costa rica'],
  'PA': ['panama']
};

function App() {
  const [countries, setCountries] = useState<Record<string, CountryData>>({})
  const [loading, setLoading] = useState(true)
  const [selectedCountry, setSelectedCountry] = useState<CountryData | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterContinent, setFilterContinent] = useState('all')
  const [filterSafety, setFilterSafety] = useState('all')
  const [activeSection, setActiveSection] = useState('summary')
  const [error, setError] = useState<string | null>(null)
  
  const [mapPosition, setMapPosition] = useState<{ coordinates: [number, number], zoom: number }>({ coordinates: [0, 0], zoom: 1 })
  const searchInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch('/data.json')
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

  const continents = useMemo(() => {
    if (!countries || typeof countries !== 'object') return [];
    return Array.from(new Set(Object.values(countries).map(c => c.continent).filter(Boolean))).sort()
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
      
      // Update URL without reloading
      const url = new URL(window.location.href);
      url.searchParams.set('country', country.iso2);
      window.history.pushState({}, '', url.toString());
    } else {
      window.scrollTo(0, 0)
      const url = new URL(window.location.href);
      url.searchParams.delete('country');
      window.history.pushState({}, '', url.toString());
    }
  }, [])

  // Handle browser back/forward buttons
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
    
    // Initial load from URL
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
  }, [countries, filterSafety, filterContinent, searchQuery]);

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

  return (
    <div className="app-container" onContextMenu={() => true}>
      {error && <div className="error-toast">{error}</div>}
      
      {!selectedCountry ? (
        <>
          <Header 
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            filterContinent={filterContinent}
            setFilterContinent={setFilterContinent}
            filterSafety={filterSafety}
            setFilterSafety={setFilterSafety}
            continents={continents}
            onLogoClick={() => handleSelectCountry(null)}
            searchInputRef={searchInputRef}
          />

          <main className="content-area">
            <CountryGrid 
              countryList={countryList} 
              onSelectCountry={handleSelectCountry} 
            />
          </main>
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
    </div>
  )
}

export default App
