import React from 'react';
import logoNoText from '../../assets/logo-no-text.png';
import FilterDropdown from './FilterDropdown';

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filterContinent: string;
  setFilterContinent: (continent: string) => void;
  filterSafety: string;
  setFilterSafety: (safety: string) => void;
  filterTravelType: string;
  setFilterTravelType: (type: string) => void;
  showOnlyFavorites: boolean;
  setShowOnlyFavorites: (val: boolean) => void;
  continents: string[];
  onLogoClick: () => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
  isStaticPage?: boolean;
  activePage?: string | null;
}

const Header: React.FC<HeaderProps> = ({
  searchQuery,
  setSearchQuery,
  filterContinent,
  setFilterContinent,
  filterSafety,
  setFilterSafety,
  filterTravelType,
  setFilterTravelType,
  showOnlyFavorites,
  setShowOnlyFavorites,
  continents,
  onLogoClick,
  searchInputRef,
  isStaticPage = false,
  activePage = null
}) => {
  const handleLogoClick = (e: React.MouseEvent) => {
    if (e.button === 1 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    onLogoClick();
  };

  const handleNavClick = (e: React.MouseEvent, eventName: string) => {
    if (e.button === 1 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    window.dispatchEvent(new CustomEvent(eventName));
  };

  return (
    <header className="main-header">
      <div className="header-content-wrapper">
        <div className="header-top-row">
          <a 
            href="./" 
            className="logo-section" 
            onClick={handleLogoClick} 
            style={{ cursor: 'pointer', textDecoration: 'none', color: 'inherit' }}
          >
            <img 
              src={logoNoText} 
              alt="TripSheet" 
              className="app-logo" 
              width="45" 
              height="45" 
            />
            <div className="logo-text">
              <span className="logo-brand">TripSheet</span>
              <p>Twoje centrum bezpiecznych podróży</p>
            </div>
          </a>
          
          <nav className="header-nav-links top-nav">
            <a 
              href="?checklist=minimum"
              className={`nav-link-btn ${activePage === 'checklist' ? 'active' : ''}`}
              onClick={(e) => handleNavClick(e, 'nav-checklist')}
              style={{ textDecoration: 'none' }}
            >
              📋 <span>Checklisty</span>
            </a>

            <a 
              href="?page=passenger-rights"
              className={`nav-link-btn ${activePage === 'passenger-rights' ? 'active' : ''}`}
              onClick={(e) => handleNavClick(e, 'nav-passenger-rights')}
              style={{ textDecoration: 'none' }}
            >
              ✈️ <span>Prawa pasażera</span>
            </a>

            <a 
              href="?page=rankings"
              className={`nav-link-btn ${activePage === 'rankings' ? 'active' : ''}`}
              onClick={(e) => handleNavClick(e, 'nav-rankings')}
              style={{ textDecoration: 'none' }}
            >
              🏆 <span>Rankingi</span>
            </a>
          </nav>
        </div>

        {!isStaticPage && (
          <div className="header-bottom-row">
            <div className="bottom-controls-wrapper">
              <button 
                className={`nav-link-btn fav-toggle-btn ${showOnlyFavorites ? 'active' : ''}`}
                onClick={() => setShowOnlyFavorites(!showOnlyFavorites)}
              >
                {showOnlyFavorites ? '⭐ ' : '☆ '}
                <span>{showOnlyFavorites ? 'Ulubione' : 'Wszystkie kraje'}</span>
              </button>

              <div className="top-controls">
                <div className="search-container">
                  <input 
                    ref={searchInputRef}
                    type="text" 
                    placeholder="Szukaj kraju..." 
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                  {searchQuery && (
                    <button 
                      className="clear-input-btn" 
                      onClick={() => setSearchQuery('')}
                      title="Wyczyść szukanie"
                    >
                      ✕
                    </button>
                  )}
                </div>
                
                <FilterDropdown 
                  filterContinent={filterContinent}
                  setFilterContinent={setFilterContinent}
                  filterSafety={filterSafety}
                  setFilterSafety={setFilterSafety}
                  filterTravelType={filterTravelType}
                  setFilterTravelType={setFilterTravelType}
                  continents={continents}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
