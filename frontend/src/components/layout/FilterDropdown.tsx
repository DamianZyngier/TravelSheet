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
import worldIcon from '../../assets/continents/World.svg';

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
    'Antarctica': antarcticaIcon,
    'All': worldIcon
  };

  const iconSrc = iconMap[name];

  if (!iconSrc) {
    console.warn(`Missing icon for continent: ${name}`);
    return <span>🌐</span>;
  }

  return (
    <div 
      className="continent-tile-icon-mask"
      data-continent={name}
      style={{ 
        '--icon-url': `url("${iconSrc}")`,
        backgroundColor: active ? 'white' : 'var(--tile-color)'
      } as any}
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
    'Antarctica': { color: '#00b4d8', bg: '#e0f7fa' }
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
        <div className="filter-btn-label-wrapper">
          <span>Filtry</span>
          {activeFiltersCount > 0 && <span className="filter-count-badge">{activeFiltersCount}</span>}
        </div>
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
                style={{ 
                  '--tile-color': '#4a5568',
                  '--tile-bg': filterContinent === 'all' ? '#4a5568' : 'white',
                  '--tile-text': filterContinent === 'all' ? 'white' : '#4a5568',
                  borderColor: filterContinent === 'all' ? '#4a5568' : '#e2e8f0'
                } as any}
              >
                <ContinentIcon name="All" active={filterContinent === 'all'} />
                <span className="continent-tile-label">Wszystkie</span>
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
                      '--tile-bg': isActive ? style.color : 'white',
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
            <div className={`safety-filter-list-v2 ${filterSafety !== 'all' ? 'has-active' : ''}`}>
              <button
                className={`safety-badge-btn risk-badge risk-unknown ${filterSafety === 'all' ? 'active' : ''}`}
                onClick={() => setFilterSafety('all')}
              >
                {filterSafety === 'all' && <span className="check-icon">✓</span>}
                Wszystkie
              </button>
              {safetyLevels.map(level => (
                <button
                  key={level.id}
                  className={`safety-badge-btn risk-badge ${level.class} ${filterSafety === level.id ? 'active' : ''}`}
                  onClick={() => handleSafetyClick(level.id)}
                >
                  {filterSafety === level.id && <span className="check-icon">✓</span>}
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
