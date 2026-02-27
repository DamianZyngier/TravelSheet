import React from 'react';
import { CountryData } from '../../types';
import { SECTIONS } from '../../constants';
import { getLongNameClass } from '../Common';

interface SidebarProps {
  selectedCountry: CountryData;
  sortedFullList: CountryData[];
  onSelectCountry: (country: CountryData) => void;
  activeSection: string;
  scrollToSection: (id: string) => void;
  navigateCountry: (direction: 'prev' | 'next') => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  selectedCountry,
  sortedFullList,
  onSelectCountry,
  activeSection,
  scrollToSection,
  navigateCountry
}) => {
  const currentIndex = sortedFullList.findIndex(c => c.iso2 === selectedCountry.iso2);
  const prevCountry = currentIndex > 0 ? sortedFullList[currentIndex - 1] : sortedFullList[sortedFullList.length - 1];
  const nextCountry = currentIndex < sortedFullList.length - 1 ? sortedFullList[currentIndex + 1] : sortedFullList[0];

  return (
    <aside className="side-menu">
      <button className="side-back-button" onClick={() => (onSelectCountry as any)(null)}>
        ← Powrót do listy
      </button>

      <div className="current-country-nav-box">
        <img src={selectedCountry.flag_url} alt="" className="current-nav-flag" />
        <div className="current-nav-info">
          <span className="current-nav-label">Przeglądasz:</span>
          <h3 className={`current-nav-name ${getLongNameClass(selectedCountry.name_pl, 'h3')}`}>
            {selectedCountry.name_pl}
          </h3>
        </div>
      </div>

      <div className="country-navigation">
        <button className="nav-button prev" onClick={() => navigateCountry('prev')}>
          <img src={prevCountry?.flag_url} alt="" className="nav-flag" />
          <div className="nav-info">
            <span className="nav-label">Poprzedni</span>
            <span className={`nav-name ${getLongNameClass(prevCountry?.name_pl || '', 'h3')}`}>{prevCountry?.name_pl}</span>
          </div>
          <span className="nav-arrow">←</span>
        </button>
        <button className="nav-button next" onClick={() => navigateCountry('next')}>
          <span className="nav-arrow">→</span>
          <div className="nav-info">
            <span className="nav-label">Następny</span>
            <span className={`nav-name ${getLongNameClass(nextCountry?.name_pl || '', 'h3')}`}>{nextCountry?.name_pl}</span>
          </div>
          <img src={nextCountry?.flag_url} alt="" className="nav-flag" />
        </button>
      </div>

      {/* Territory/Parent relationship links */}
      {(selectedCountry.parent || (selectedCountry.territories && selectedCountry.territories.length > 0)) && (
        <div className="relationship-nav-box">
          {selectedCountry.parent && (
            <div className="parent-link-box">
              <span className="relationship-label">Terytorium państwa:</span>
              <button 
                className="relationship-link-btn"
                onClick={() => {
                   const parent = sortedFullList.find(c => c.iso2 === selectedCountry.parent?.iso2);
                   if (parent) onSelectCountry(parent);
                }}
              >
                🇫🇷 {selectedCountry.parent.name_pl}
              </button>
            </div>
          )}
          
          {selectedCountry.territories && selectedCountry.territories.length > 0 && (
            <div className="territories-link-box">
              <span className="relationship-label">Terytoria zależne:</span>
              <div className="territories-grid">
                {selectedCountry.territories.map(t => (
                  <button 
                    key={t.iso2}
                    className="territory-mini-link"
                    onClick={() => {
                      const territory = sortedFullList.find(c => c.iso2 === t.iso2);
                      if (territory) onSelectCountry(territory);
                    }}
                  >
                    {t.name_pl}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="side-menu-list">
        {SECTIONS.map(s => (
          <button 
            key={s.id}
            className={`side-menu-item ${activeSection === s.id ? 'active' : ''}`}
            onClick={() => scrollToSection(s.id)}
          >
            <span className="side-menu-icon">{s.icon}</span>
            <span className="side-menu-label">{s.label}</span>
          </button>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
