import React, { useState, useRef, useEffect } from 'react';
import { CONTINENT_MAP } from '../../constants';

interface FilterDropdownProps {
  filterContinent: string;
  setFilterContinent: (continent: string) => void;
  filterSafety: string;
  setFilterSafety: (safety: string) => void;
  continents: string[];
}

const ContinentIcon: React.FC<{ name: string; color: string; active: boolean }> = ({ name, color, active }) => {
  // Simple SVG paths for continent outlines
  const paths: Record<string, JSX.Element> = {
    'Africa': (
      <path d="M12,2C11.5,2.1,10.1,3.2,9.4,3.8C8.7,4.4,8.1,4.8,7.4,5.1C6.7,5.4,5.8,5.5,5.1,5.8C4.4,6.1,3.9,6.6,3.6,7.3C3.3,8,3.3,8.9,3.4,9.7 C3.5,10.5,3.8,11.3,4.2,12C4.6,12.7,5.1,13.3,5.7,13.8C6.3,14.3,7,14.7,7.7,15C8.4,15.3,9.1,15.5,9.8,15.7C10.5,15.9,11.2,16.1,11.9,16.4 C12.6,16.7,13.3,17.1,13.9,17.6C14.5,18.1,15,18.7,15.4,19.4C15.8,20.1,16.1,20.9,16.2,21.7C16.3,22.5,16.3,22.5,17.1,22.5 C17.9,22.5,18.7,22.5,19.5,22.5C20.3,22.5,21.1,22.5,21.9,22.5C22.7,22.5,22.7,22.5,22.7,21.7C22.7,20.9,22.7,20.1,22.7,19.3 C22.7,18.5,22.7,17.7,22.7,16.9C22.7,16.1,22.7,15.3,22.7,14.5C22.7,13.7,22.7,12.9,22.7,12.1C22.7,11.3,22.7,10.5,22.7,9.7 C22.7,8.9,22.7,8.1,22.7,7.3C22.7,6.5,22.7,5.7,22.7,4.9C22.7,4.1,22.7,3.3,22.7,2.5C22.7,1.7,22.7,1.7,21.9,1.7C21.1,1.7,20.3,1.7,19.5,1.7 C18.7,1.7,17.9,1.7,17.1,1.7C16.3,1.7,15.5,1.7,14.7,1.7C13.9,1.7,13.1,1.7,12.3,1.7C11.5,1.7,11.5,1.7,11.5,2.5" />
    ),
    'Asia': (
      <path d="M5,10C5,10,7,8,9,8C11,8,13,10,15,10C17,10,19,8,21,8C23,8,25,10,25,10L25,20C25,20,23,18,21,18C19,18,17,20,15,20C13,20,11,18,9,18C7,18,5,20,5,20L5,10" />
    ),
    'Europe': (
      <path d="M12,4L14,8L18,9L15,12L16,16L12,14L8,16L9,12L6,9L10,8L12,4" />
    ),
    'North America': (
      <path d="M8,4L12,2L16,4L18,8L16,12L14,16L10,18L6,16L4,12L6,8L8,4" />
    ),
    'South America': (
      <path d="M10,2L14,4L16,8L14,14L10,20L6,14L4,8L6,4L10,2" />
    ),
    'Oceania': (
      <circle cx="12" cy="12" r="8" />
    )
  };

  const emojiFallback: Record<string, string> = {
    'Africa': '🌍',
    'Asia': '🌏',
    'Europe': '🇪🇺',
    'North America': '🏔️',
    'South America': '🌴',
    'Oceania': '🏝️',
    'Antarctica': '❄️'
  };

  return (
    <svg 
      viewBox="0 0 24 24" 
      width="18" 
      height="18" 
      fill={active ? color : 'none'} 
      stroke={active ? 'white' : color} 
      strokeWidth="2"
      style={{ marginRight: '4px' }}
    >
      {paths[name] || <text y="18" x="0" fontSize="16" fill={color}>{emojiFallback[name] || '🌐'}</text>}
    </svg>
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
                className={`safety-filter-item risk-unknown ${filterSafety === 'all' ? 'active' : ''}`}
                onClick={() => setFilterSafety('all')}
              >
                Wszystkie
              </button>
              {safetyLevels.map(level => (
                <button
                  key={level.id}
                  className={`safety-filter-item ${level.class} ${filterSafety === level.id ? 'active' : ''}`}
                  onClick={() => setFilterSafety(level.id)}
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
