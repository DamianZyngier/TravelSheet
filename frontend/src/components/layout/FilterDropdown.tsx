import React, { useState, useRef, useEffect } from 'react';
import { CONTINENT_MAP } from '../../constants';

interface FilterDropdownProps {
  filterContinent: string;
  setFilterContinent: (continent: string) => void;
  filterSafety: string;
  setFilterSafety: (safety: string) => void;
  continents: string[];
}

const ContinentIcon: React.FC<{ name: string; color: string }> = ({ name, color }) => {
  // Simple geometric representations or placeholder icons for continents
  const icons: Record<string, string> = {
    'Africa': '🌍',
    'Asia': '🌏',
    'Europe': '🇪🇺',
    'North America': '🏔️',
    'South America': '🌴',
    'Oceania': '🏝️',
    'Antarctica': '❄️'
  };

  return <span style={{ color }}>{icons[name] || '🌐'}</span>;
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
    { id: 'all', label: 'Wszystkie', class: 'risk-unknown' },
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
                    backgroundColor: filterContinent === c ? `${continentColors[c]}15` : 'transparent'
                  }}
                >
                  <ContinentIcon name={c} color={continentColors[c]} />
                  <span>{CONTINENT_MAP[c] || c}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="filter-section">
            <label className="filter-label">Bezpieczeństwo</label>
            <div className="safety-filter-list">
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
