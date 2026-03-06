import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../common';

interface BasicInfoSectionProps {
  selectedCountry: CountryData;
}

export const BasicInfoSection: React.FC<BasicInfoSectionProps> = ({ selectedCountry }) => {
  // Top 3 religions for maximum compactness
  const topReligions = selectedCountry.religions 
    ? [...selectedCountry.religions].sort((a, b) => b.percentage - a.percentage).slice(0, 3)
    : [];

  const getTimezoneDiff = (tzStr: string | null) => {
    if (!tzStr) return null;
    // Warsaw is UTC+1 (winter) / UTC+2 (summer). 
    // For simplicity and consistency without external libs, we use UTC+1 as base.
    const warsawOffset = 1;
    
    // Extract UTC offset from string like "UTC+05:30" or "UTC-03:00"
    const match = tzStr.match(/UTC([+-])(\d{2}):(\d{2})/);
    if (match) {
      const sign = match[1] === '+' ? 1 : -1;
      const hours = parseInt(match[2]);
      const mins = parseInt(match[3]);
      const offset = sign * (hours + mins/60);
      const diff = offset - warsawOffset;
      
      const diffStr = diff > 0 ? `+${diff}` : `${diff}`;
      // Clean up .0
      return diffStr.replace('.0', '') + 'h';
    }
    return null;
  };

  const tzDiff = getTimezoneDiff(selectedCountry.timezone);

  return (
    <div id="info" className="info-block full-width basic-info-section scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">ℹ️</span>
        <label>Podstawowe informacje</label>
      </div>
      <div className="info-grid">
        <div className="info-item-box">
          <strong>Kontynent</strong>
          <span>{selectedCountry.continent || 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Stolica</strong>
          <span>
            {selectedCountry.capital || 'Brak danych'} 
            {selectedCountry.timezone && (
              <>
                <span style={{ marginLeft: '4px', color: '#64748b', fontSize: '0.85rem' }}>
                  ({selectedCountry.timezone})
                </span>
                {tzDiff && (
                  <span style={{ 
                    color: tzDiff === '0h' ? '#4299e1' : '#48bb78', 
                    fontSize: '0.8rem', 
                    fontWeight: 'bold', 
                    marginLeft: '6px' 
                  }}>
                    <br />({tzDiff === '0h' ? 'ten sam czas' : `${tzDiff} do PL`})
                  </span>
                )}
              </>
            )}
          </span>
        </div>
        <div className="info-item-box">
          <strong>Ludność</strong>
          <span>{selectedCountry.population?.toLocaleString() || 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Gęstość zaludnienia</strong>
          <span>
            {selectedCountry.population && selectedCountry.area ? (
              <>
                {(selectedCountry.population / selectedCountry.area).toFixed(1)} os./km²
                {(() => {
                  const density = selectedCountry.population / selectedCountry.area;
                  const polandDensity = 120;
                  const ratio = density / polandDensity;
                  if (ratio > 1.1) {
                    return <span style={{ color: '#f56565', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                      <br />({ratio.toFixed(1)}x gęściej niż w PL)
                    </span>;
                  } else if (ratio < 0.9) {
                    return <span style={{ color: '#48bb78', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                      <br />({(1/ratio).toFixed(1)}x rzadziej niż w PL)
                    </span>;
                  } else {
                    return <span style={{ color: '#4299e1', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                      <br />(podobnie do PL)
                    </span>;
                  }
                })()}
              </>
            ) : 'Brak danych'}
          </span>
        </div>
        <div className="info-item-box">
          <strong>Języki</strong>
          <span>{selectedCountry.languages?.length > 0 ? selectedCountry.languages.map(l => l.name + (l.is_official ? ' (ofic.)' : '')).join(', ') : 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Nr kierunkowy</strong>
          <span>{selectedCountry.phone_code ? `+${selectedCountry.phone_code.replace('+', '')}` : 'Brak danych'}</span>
        </div>
        
        {/* Integrated Religions */}
        {topReligions.length > 0 && (
          <div id="religion" className="info-item-box">
            <strong>Religie i wyznania</strong>
            <div className="religion-list-simple">
              {topReligions.map((r, i) => (
                <div key={i} className="religion-item-simple">
                  <span className="rel-name">{r.name}</span>
                  <span className="rel-perc">{Math.round(r.percentage)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedCountry.national_dish && (
          <div className="info-item-box">
            <strong>Danie narodowe</strong>
            <span>🍽️ {selectedCountry.national_dish}</span>
          </div>
        )}

        {selectedCountry.climate_description && (
          <div className="info-item-box full">
            <strong>Klimat (opis)</strong>
            <span>☀️ {selectedCountry.climate_description}</span>
          </div>
        )}

        {selectedCountry.main_airport && (
          <div className="info-item-box full">
            <strong>Główne lotnisko</strong>
            <span>✈️ {selectedCountry.main_airport}</span>
          </div>
        )}
        {selectedCountry.railway_info && (
          <div className="info-item-box full">
            <strong>Kolej</strong>
            <span>🚆 {selectedCountry.railway_info}</span>
          </div>
        )}
        {selectedCountry.largest_cities && (
          <div className="info-item-box full">
            <strong>Największe miasta (top 10)</strong>
            <span>{selectedCountry.largest_cities}</span>
          </div>
        )}
        {selectedCountry.ethnic_groups && (
          <div className="info-item-box full">
            <strong>Grupy etniczne</strong>
            <span>{selectedCountry.ethnic_groups}</span>
          </div>
        )}
        {selectedCountry.regional_products && (
          <div className="info-item-box full">
            <strong>Produkty regionalne i pamiątki</strong>
            <span>🎁 {selectedCountry.regional_products}</span>
          </div>
        )}
        {selectedCountry.official_tourist_website && (
          <div className="info-item-box full">
            <strong>Oficjalna strona turystyczna</strong>
            <a 
              href={selectedCountry.official_tourist_website} 
              target="_blank" 
              rel="noopener noreferrer"
              className="msz-link"
              style={{ marginTop: '0', fontWeight: '700' }}
            >
              {selectedCountry.official_tourist_website.replace('https://', '').replace('http://', '').split('/')[0]} ↗
            </a>
          </div>
        )}

        {/* Advanced Stats */}
        {(selectedCountry.hdi || selectedCountry.life_expectancy || selectedCountry.gdp_nominal || selectedCountry.inception_date) && (
          <div className="info-item-box full stats-container">
            <div className="stats-header">Statystyki i Rozwój</div>
            <div className="stats-grid">
              {selectedCountry.hdi && (
                <div className="stat-item">
                  <span className="stat-label">HDI (Rozwój)</span>
                  <span className={`stat-value hdi-${selectedCountry.hdi >= 0.8 ? 'very-high' : selectedCountry.hdi >= 0.7 ? 'high' : 'medium'}`}>
                    {selectedCountry.hdi.toFixed(3)}
                  </span>
                  <span className="stat-comparison">
                    {selectedCountry.iso2 !== 'PL' && `(PL: 0.876)`}
                  </span>
                </div>
              )}
              {selectedCountry.life_expectancy && (
                <div className="stat-item">
                  <span className="stat-label">Długość życia</span>
                  <span className="stat-value">{Math.round(selectedCountry.life_expectancy)} lat</span>
                  <span className="stat-comparison">
                    {selectedCountry.iso2 !== 'PL' && (
                      <span className={selectedCountry.life_expectancy > 76 ? 'text-pos' : 'text-neg'}>
                        {selectedCountry.life_expectancy > 76 ? '+' : ''}{Math.round(selectedCountry.life_expectancy - 76)} lat vs PL
                      </span>
                    )}
                  </span>
                </div>
              )}
              {selectedCountry.gdp_nominal && (
                <div className="stat-item">
                  <span className="stat-label">PKB (Nominal)</span>
                  <span className="stat-value">
                    ${(selectedCountry.gdp_nominal / 1e9).toFixed(1)} mld
                  </span>
                  <span className="stat-comparison">
                    {selectedCountry.iso2 !== 'PL' && (
                      <span>{Math.round((selectedCountry.gdp_nominal / 679.4e9) * 100)}% PL</span>
                    )}
                  </span>
                </div>
              )}
              {selectedCountry.inception_date && (
                <div className="stat-item">
                  <span className="stat-label">Powstanie / Niep.</span>
                  <span className="stat-value">{selectedCountry.inception_date}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <DataSource sources={['REST', 'WIKI']} lastUpdated={selectedCountry.last_updated} />
    </div>
  );
};
