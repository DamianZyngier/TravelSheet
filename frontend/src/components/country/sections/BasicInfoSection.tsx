import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource, ExpandableText } from '../../common';

interface BasicInfoSectionProps {
  selectedCountry: CountryData;
}

export const BasicInfoSection: React.FC<BasicInfoSectionProps> = ({ selectedCountry }) => {
  // Top 3 religions for maximum compactness
  const topReligions = selectedCountry.religions 
    ? [...selectedCountry.religions].sort((a, b) => b.percentage - a.percentage).slice(0, 3)
    : [];

  return (
    <div id="info" className="info-block full-width basic-info-section scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">ℹ️</span>
        <label>Podstawowe informacje</label>
      </div>
      <div className="basic-info-grid">
        <div className="info-item-box">
          <strong>Kontynent:</strong>
          <span>{selectedCountry.continent || 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Stolica:</strong>
          <span>{selectedCountry.capital || 'Brak danych'} {selectedCountry.timezone && `(${selectedCountry.timezone})`}</span>
        </div>
        <div className="info-item-box">
          <strong>Ludność:</strong>
          <span>{selectedCountry.population?.toLocaleString() || 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Gęstość zaludnienia:</strong>
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
                      ({ratio.toFixed(1)}x gęściej)
                    </span>;
                  } else if (ratio < 0.9) {
                    return <span style={{ color: '#48bb78', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                      ({(1/ratio).toFixed(1)}x rzadziej)
                    </span>;
                  } else {
                    return <span style={{ color: '#4299e1', fontSize: '0.8rem', fontWeight: 'bold', marginLeft: '6px' }}>
                      (podobnie)
                    </span>;
                  }
                })()}
              </>
            ) : 'Brak danych'}
          </span>
        </div>
        <div className="info-item-box">
          <strong>Języki:</strong>
          <span>{selectedCountry.languages?.length > 0 ? selectedCountry.languages.map(l => l.name + (l.is_official ? ' (ofic.)' : '')).join(', ') : 'Brak danych'}</span>
        </div>
        <div className="info-item-box">
          <strong>Nr kierunkowy:</strong>
          <span>{selectedCountry.phone_code ? `+${selectedCountry.phone_code.replace('+', '')}` : 'Brak danych'}</span>
        </div>
        
        {/* Integrated Religions */}
        {topReligions.length > 0 && (
          <div id="religion" className="info-item-box">
            <strong>Religie i wyznania:</strong>
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
            <strong>Danie narodowe:</strong>
            <span>🍽️ {selectedCountry.national_dish}</span>
          </div>
        )}

        {selectedCountry.main_airport && (
          <div className="info-item-box full">
            <strong>Główne lotnisko:</strong>
            <span>✈️ {selectedCountry.main_airport}</span>
          </div>
        )}
        {selectedCountry.railway_info && (
          <div className="info-item-box full">
            <strong>Kolej:</strong>
            <span>🚆 {selectedCountry.railway_info}</span>
          </div>
        )}
        {selectedCountry.largest_cities && (
          <div className="info-item-box full">
            <strong>Największe miasta:</strong>
            <span>{selectedCountry.largest_cities}</span>
          </div>
        )}
        {selectedCountry.ethnic_groups && (
          <div className="info-item-box full">
            <strong>Grupy etniczne:</strong>
            <span>{selectedCountry.ethnic_groups}</span>
          </div>
        )}
      </div>

      <DataSource sources={['REST', 'WIKI']} lastUpdated={selectedCountry.last_updated} />
    </div>
  );
};
