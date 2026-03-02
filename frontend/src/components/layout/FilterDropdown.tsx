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
  // Refined silhouettes for 24x24 icon view
  const silhouettes: Record<string, string> = {
    'Africa': 'M12 2l3 1 2 3 1 4-1 4-2 4-3 4-3-4-2-4-1-4 1-4 3-3 2-1z',
    'Asia': 'M16 4l4 1 2 3 1 4-1 4-2 3-4 1-4-1-2-3-1-4 1-4 3-3 3-1z',
    'Europe': 'M8 4l3-1 3 1 2 3 1 4-1 4-3 1-3-1-2-3-1-4 1-4 3-3 3-1z',
    'North America': 'M6 2l4-1 4 1 2 3 1 4-1 4-2 4-4 1-4-1-2-4-1-4 1-4 3-3 1-1z',
    'South America': 'M8 10l4-1 4 1 2 3 1 4-1 4-2 4-4 1-4-1-2-4-1-4 1-4 3-3 1-1z',
    'Oceania': 'M16 14l3-1 3 1 1 2-1 2-3 1-3-1-1-2 1-2z',
    'Antarctica': 'M12 20l6-1 4 1 1 2-1 2-4 1-6-1-6 1-4-1-1-2 1-2 4-1 6 1z'
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
      fill={active ? 'white' : color} 
      stroke={active ? 'white' : color} 
      strokeWidth="1"
      style={{ marginRight: '4px', flexShrink: 0 }}
    >
      {silhouettes[name] ? (
        <path d={silhouettes[name]} strokeLinecap="round" strokeLinejoin="round" />
      ) : (
        <text y="18" x="0" fontSize="16" fill={color}>{emojiFallback[name] || '🌐'}</text>
      )}
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
