import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../common';

interface BasicInfoSectionProps {
  selectedCountry: CountryData;
}

export const BasicInfoSection: React.FC<BasicInfoSectionProps> = ({ selectedCountry }) => {
  return (
    <div className="info-block full-width basic-info-section">
      <div className="section-header">
        <span className="section-header-icon">📊</span>
        <label>Podstawowe informacje</label>
      </div>
      
      <div className="info-grid">
        <div className="info-item-box">
          <strong>Stolica</strong>
          <span>🏛️ {selectedCountry.capital || 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Strefa czasowa</strong>
          <span>🕒 {selectedCountry.timezone || 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Ludność</strong>
          <span>
            👥 {selectedCountry.population?.toLocaleString() || 'Brak danych'}
            {selectedCountry.population && selectedCountry.iso2 !== 'PL' && (
              <span className="stat-comparison" style={{ display: 'block', fontWeight: 'bold' }}>
                {(() => {
                  const plPop = 38000000;
                  const ratio = selectedCountry.population / plPop;
                  if (ratio > 1.1) return <span style={{ color: '#64748b' }}>({ratio.toFixed(1)}x więcej niż PL)</span>;
                  if (ratio < 0.9) return <span style={{ color: '#64748b' }}>({(1/ratio).toFixed(1)}x mniej niż PL)</span>;
                  return <span style={{ color: '#4299e1' }}>(podobna do PL)</span>;
                })()}
              </span>
            )}
          </span>
        </div>
        <div className="info-item-box">
          <strong>Gęstość zaludnienia</strong>
          <span>
            {selectedCountry.population && selectedCountry.area ? (
              <>
                {(selectedCountry.population / selectedCountry.area).toFixed(1)} os./km²
                {selectedCountry.iso2 !== 'PL' && (() => {
                  const density = selectedCountry.population / selectedCountry.area;
                  const polandDensity = 120;
                  const ratio = density / polandDensity;
                  if (ratio > 1.1) {
                    return <span style={{ color: '#f56565', fontSize: '0.8rem', fontWeight: 'bold', display: 'block' }}>
                      ({ratio.toFixed(1)}x gęściej niż PL)
                    </span>;
                  } else if (ratio < 0.9) {
                    return <span style={{ color: '#48bb78', fontSize: '0.8rem', fontWeight: 'bold', display: 'block' }}>
                      ({(1/ratio).toFixed(1)}x rzadziej niż PL)
                    </span>;
                  } else {
                    return <span style={{ color: '#4299e1', fontSize: '0.8rem', fontWeight: 'bold', display: 'block' }}>
                      (podobnie do PL)
                    </span>;
                  }
                })()}
              </>
            ) : 'Brak danych'}
          </span>
        </div>
        <div className="info-item-box">
          <strong>Religie</strong>
          <div className="religion-list-simple">
            {selectedCountry.religions && selectedCountry.religions.length > 0 ? (
              selectedCountry.religions.map((r, idx) => (
                <div key={idx} className="religion-item-simple">
                  <span className="rel-name">{r.name}</span>
                  <span className="rel-perc">{r.percentage > 0 ? `${r.percentage}%` : 'Główne wyznanie'}</span>
                </div>
              ))
            ) : (
              <span>Brak danych</span>
            )}
          </div>
        </div>
        <div className="info-item-box">
          <strong>Języki</strong>
          <span>💬 {selectedCountry.languages?.map(l => l.name).join(', ') || 'Brak danych'}</span>
        </div>
        
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
        {(selectedCountry.hdi || selectedCountry.life_expectancy || selectedCountry.gdp_per_capita || selectedCountry.inception_date) && (
          <div className="info-item-box full stats-container">
            <div className="stats-header">Statystyki i Rozwój</div>
            <div className="stats-grid">
              {selectedCountry.hdi && (
                <div className="stat-item">
                  <span className="stat-label">HDI (Rozwój)</span>
                  <span className={`stat-value hdi-${selectedCountry.hdi >= 0.8 ? 'very-high' : selectedCountry.hdi >= 0.7 ? 'high' : 'medium'}`}>
                    {selectedCountry.hdi.toFixed(3)}
                  </span>
                  {selectedCountry.iso2 !== 'PL' && (
                    <span className="stat-comparison" style={{ fontWeight: 'bold' }}>
                      {(() => {
                        const plHdi = 0.876;
                        const diff = selectedCountry.hdi - plHdi;
                        if (Math.abs(diff) < 0.01) return <span style={{ color: '#4299e1' }}>(jak w PL)</span>;
                        return <span className={diff > 0 ? 'text-pos' : 'text-neg'}>
                          ({diff > 0 ? 'wyższy' : 'niższy'} niż PL)
                        </span>;
                      })()}
                    </span>
                  )}
                </div>
              )}
              {selectedCountry.life_expectancy && (
                <div className="stat-item">
                  <span className="stat-label">Długość życia</span>
                  <span className="stat-value">{Math.round(selectedCountry.life_expectancy)} lat</span>
                  {selectedCountry.iso2 !== 'PL' && (
                    <span className="stat-comparison" style={{ fontWeight: 'bold' }}>
                      {(() => {
                        const plLife = 76;
                        const diff = Math.round(selectedCountry.life_expectancy - plLife);
                        if (Math.abs(diff) === 0) return <span style={{ color: '#4299e1' }}>(jak w PL)</span>;
                        return <span className={diff > 0 ? 'text-pos' : 'text-neg'}>
                          ({diff > 0 ? '+' : ''}{diff} lat vs PL)
                        </span>;
                      })()}
                    </span>
                  )}
                </div>
              )}
              {selectedCountry.gdp_per_capita && (
                <div className="stat-item">
                  <span className="stat-label">PKB na osobę</span>
                  <span className="stat-value">
                    ${Math.round(selectedCountry.gdp_per_capita).toLocaleString()}
                  </span>
                  {selectedCountry.iso2 !== 'PL' && (
                    <span className="stat-comparison" style={{ fontWeight: 'bold' }}>
                      {(() => {
                        const plGdpCapita = 18000;
                        const ratio = selectedCountry.gdp_per_capita / plGdpCapita;
                        if (ratio > 1.1) return <span className="text-pos">({ratio.toFixed(1)}x więcej niż PL)</span>;
                        if (ratio < 0.9) return <span className="text-neg">({(1/ratio).toFixed(1)}x mniej niż PL)</span>;
                        return <span style={{ color: '#4299e1' }}>(jak w PL)</span>;
                      })()}
                    </span>
                  )}
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
