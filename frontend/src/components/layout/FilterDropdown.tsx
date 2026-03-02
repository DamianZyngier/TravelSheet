import React, { useState, useRef, useEffect } from 'react';
import { CONTINENT_MAP } from '../../constants';

// Import continent icons
import africaIcon from '../../assets/continents/Africa.svg';
import antarcticaIcon from '../../assets/continents/Antarctica.svg';
import asiaIcon from '../../assets/continents/Asia.svg';
import oceaniaIcon from '../../assets/continents/Australia.svg';
import europeIcon from '../../assets/continents/Europe.svg';
import northAmericaIcon from '../../assets/continents/North_America.svg';
import southAmericaIcon from '../../assets/continents/South_America.svg';

interface FilterDropdownProps {
  filterContinent: string;
  setFilterContinent: (continent: string) => void;
  filterSafety: string;
  setFilterSafety: (safety: string) => void;
  continents: string[];
}

const ContinentIcon: React.FC<{ name: string; active: boolean }> = ({ name, active }) => {
  const iconMap: Record<string, string> = {
    'Africa': africaIcon,
    'Asia': asiaIcon,
    'Europe': europeIcon,
    'North America': northAmericaIcon,
    'South America': southAmericaIcon,
    'Oceania': oceaniaIcon,
    'Antarctica': antarcticaIcon
  };

  const iconSrc = iconMap[name];

  if (!iconSrc) return <span>🌐</span>;

  return (
    <img 
      src={iconSrc} 
      alt={name} 
      className="continent-tile-icon"
      style={{ 
        filter: active ? 'brightness(0) invert(1)' : 'none'
      }} 
    />
  );
};

const FilterDropdown: React.FC<FilterDropdownProps> = ({
  filterContinent,
  setFilterContinent,
  filterSafety,
  setFilterSafety,
  continents
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const continentStyles: Record<string, { color: string, bg: string }> = {
    'Africa': { color: '#2f855a', bg: '#f0fff4' },
    'Asia': { color: '#c05621', bg: '#fffaf0' },
    'Europe': { color: '#2b6cb0', bg: '#ebf8ff' },
    'North America': { color: '#c53030', bg: '#fff5f5' },
    'South America': { color: '#6b46c1', bg: '#faf5ff' },
    'Oceania': { color: '#2c7a7b', bg: '#e6fffa' },
    'Antarctica': { color: '#4a5568', bg: '#edf2f7' }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const safetyLevels = [
    { id: 'low', label: 'Bezpiecznie', class: 'risk-low' },
    { id: 'medium', label: 'Średnio', class: 'risk-medium' },
    { id: 'high', label: 'Niebezpiecznie', class: 'risk-high' },
    { id: 'critical', label: 'Bardzo niebezpiecznie', class: 'risk-critical' }
  ];

  const activeFiltersCount = (filterContinent !== 'all' ? 1 : 0) + (filterSafety !== 'all' ? 1 : 0);

  const handleContinentClick = (c: string) => {
    if (filterContinent === c) {
      setFilterContinent('all');
    } else {
      setFilterContinent(c);
    }
  };

  const handleSafetyClick = (s: string) => {
    if (filterSafety === s) {
      setFilterSafety('all');
    } else {
      setFilterSafety(s);
    }
  };

  return (
    <div className="filter-dropdown-container" ref={dropdownRef}>
      <button 
        className={`filter-main-btn ${isOpen ? 'active' : ''} ${activeFiltersCount > 0 ? 'has-filters' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="filter-icon">🔍</span>
        <span>Filtry {activeFiltersCount > 0 && `(${activeFiltersCount})`}</span>
        <span className="chevron">{isOpen ? '▴' : '▾'}</span>
      </button>

      {isOpen && (
        <div className="filter-panel">
          <div className="filter-section">
            <label className="filter-label">Kontynent</label>
            <div className="continent-filter-grid-v2">
              <button 
                className={`continent-tile-btn ${filterContinent === 'all' ? 'active' : ''}`}
                onClick={() => setFilterContinent('all')}
              >
                <span>Wszystkie</span>
              </button>
              {continents.map(c => {
                const style = continentStyles[c] || { color: '#4a5568', bg: '#f7fafc' };
                const isActive = filterContinent === c;
                return (
                  <button 
                    key={c}
                    className={`continent-tile-btn ${isActive ? 'active' : ''}`}
                    onClick={() => handleContinentClick(c)}
                    style={{ 
                      '--tile-color': style.color,
                      '--tile-bg': isActive ? style.color : style.bg,
                      '--tile-text': isActive ? 'white' : style.color,
                      borderColor: isActive ? style.color : '#e2e8f0'
                    } as any}
                  >
                    <ContinentIcon name={c} active={isActive} />
                    <span className="continent-tile-label">{CONTINENT_MAP[c] || c}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="filter-section">
            <label className="filter-label">Bezpieczeństwo</label>
            <div className="safety-filter-list-v2">
              <button
                className={`safety-badge-btn risk-badge risk-unknown ${filterSafety === 'all' ? 'active' : ''}`}
                onClick={() => setFilterSafety('all')}
              >
                Wszystkie
              </button>
              {safetyLevels.map(level => (
                <button
                  key={level.id}
                  className={`safety-badge-btn risk-badge ${level.class} ${filterSafety === level.id ? 'active' : ''}`}
                  onClick={() => handleSafetyClick(level.id)}
                >
                  {level.label}
                </button>
              ))}
            </div>
          </div>

          <div className="filter-panel-footer">
            <button 
              className="clear-all-filters"
              onClick={() => {
                setFilterContinent('all');
                setFilterSafety('all');
              }}
            >
              Wyczyść wszystkie
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterDropdown;
