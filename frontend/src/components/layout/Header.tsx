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
  searchInputRef
}) => {
  return (
    <header className="main-header">
      <div className="header-content-wrapper">
        <div className="header-top-row">
          <div className="logo-section" onClick={onLogoClick} style={{ cursor: 'pointer' }}>
            <img src={logoNoText} alt="TripSheet" className="app-logo" />
            <div className="logo-text">
              <span className="logo-brand">TripSheet</span>
              <p>Twoje centrum bezpiecznych podróży</p>
            </div>
          </div>
          
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

        <div className="header-bottom-row">
          <nav className="header-nav-links">
            <button 
              className={`nav-link-btn ${showOnlyFavorites ? 'active' : ''}`}
              onClick={() => setShowOnlyFavorites(!showOnlyFavorites)}
            >
              {showOnlyFavorites ? '⭐ Ulubione' : '☆ Wszystkie kraje'}
            </button>

            <button 
              className="nav-link-btn"
              onClick={() => window.dispatchEvent(new CustomEvent('nav-checklist'))}
            >
              📋 Checklisty
            </button>

            <button 
              className="nav-link-btn"
              onClick={() => window.dispatchEvent(new CustomEvent('nav-passenger-rights'))}
            >
              ✈️ Prawa pasażera
            </button>

            <button 
              className="nav-link-btn"
              onClick={() => window.dispatchEvent(new CustomEvent('nav-rankings'))}
            >
              🏆 Rankingi
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
