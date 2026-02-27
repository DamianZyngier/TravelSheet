import React from 'react';
import logoNoText from '../../assets/logo-no-text.png';
import { CONTINENT_MAP } from '../../constants';

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filterContinent: string;
  setFilterContinent: (continent: string) => void;
  filterSafety: string;
  setFilterSafety: (safety: string) => void;
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
  continents,
  onLogoClick,
  searchInputRef
}) => {
  return (
    <header className="main-header">
      <div className="header-content">
        <div className="logo-section" onClick={onLogoClick} style={{ cursor: 'pointer' }}>
          <img src={logoNoText} alt="TripSheet" className="app-logo" />
          <div className="logo-text">
            <span className="logo-brand">TripSheet</span>
            <p>Twoje centrum bezpiecznych podróży</p>
          </div>
        </div>
        
        <div className="controls-section">
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
          
          <div className="filter-group">
            <select value={filterContinent} onChange={e => setFilterContinent(e.target.value)}>
              <option value="all">Wszystkie kontynenty</option>
              {continents.map(c => <option key={c} value={c}>{CONTINENT_MAP[c] || c}</option>)}
            </select>
          </div>

          <div className="filter-group">
            <select value={filterSafety} onChange={e => setFilterSafety(e.target.value)}>
              <option value="all">Wszystkie poziomy bezpieczeństwa</option>
              <option value="low">Bezpiecznie</option>
              <option value="medium">Średnio bezpiecznie</option>
              <option value="high">Niebezpiecznie</option>
              <option value="critical">Bardzo niebezpiecznie</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
