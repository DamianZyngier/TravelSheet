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
      style={{ 
        width: '20px', 
        height: '20px', 
        marginRight: '6px',
        flexShrink: 0,
        // If active, make the icon white using CSS filters
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

  const continentColors: Record<string, string> = {
    'Africa': '#48bb78',
    'Asia': '#ed8936',
    'Europe': '#4299e1',
    'North America': '#f56565',
    'South America': '#9f7aea',
    'Oceania': '#38b2ac',
    'Antarctica': '#a0aec0'
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
            <div className="continent-filter-grid">
              <button 
                className={`continent-btn ${filterContinent === 'all' ? 'active' : ''}`}
                onClick={() => setFilterContinent('all')}
              >
                Wszystkie
              </button>
              {continents.map(c => (
                <button 
                  key={c}
                  className={`continent-btn ${filterContinent === c ? 'active' : ''}`}
                  onClick={() => setFilterContinent(c)}
                  style={{ 
                    borderColor: filterContinent === c ? continentColors[c] : '#e2e8f0',
                    backgroundColor: filterContinent === c ? `${continentColors[c]}` : 'transparent',
                    color: filterContinent === c ? 'white' : '#4a5568'
                  }}
                >
                  <ContinentIcon name={c} color={continentColors[c]} active={filterContinent === c} />
                  <span>{CONTINENT_MAP[c] || c}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="filter-section">
            <label className="filter-label">Bezpieczeństwo</label>
            <div className="safety-filter-list">
              <button
                className={`safety-filter-item risk-badge risk-unknown ${filterSafety === 'all' ? 'active' : ''}`}
                onClick={() => setFilterSafety('all')}
                style={{ marginTop: 0, cursor: 'pointer', border: filterSafety === 'all' ? '2px solid #2b6cb0' : '1px solid #e2e8f0' }}
              >
                Wszystkie
              </button>
              {safetyLevels.map(level => (
                <button
                  key={level.id}
                  className={`safety-filter-item risk-badge ${level.class} ${filterSafety === level.id ? 'active' : ''}`}
                  onClick={() => setFilterSafety(level.id)}
                  style={{ 
                    marginTop: 0, 
                    cursor: 'pointer',
                    border: filterSafety === level.id ? '2px solid #2d3748' : '1px solid transparent',
                    boxShadow: filterSafety === level.id ? '0 0 0 1px white' : 'none'
                  }}
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
