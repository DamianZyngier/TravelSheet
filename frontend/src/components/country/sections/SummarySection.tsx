import React from 'react';
import type { CountryData } from '../../../types';
import { ExpandableText, DataSource } from '../../common';

interface SummarySectionProps {
  selectedCountry: CountryData;
  allCountries: CountryData[];
  onSelectCountry: (country: CountryData) => void;
}

export const SummarySection: React.FC<SummarySectionProps> = ({ 
  selectedCountry, 
  allCountries,
  onSelectCountry
}) => {
  return (
    <div id="discover" className="info-block full-width discover-section scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">✨</span>
        <label>Odkryj i poznaj kraj</label>
      </div>
      
      <div className="discover-container">
        {selectedCountry.wiki_summary ? (
          <div className="wiki-summary-text">
            <ExpandableText text={selectedCountry.wiki_summary} maxLength={450} />
          </div>
        ) : (
          <p className="no-data-text">Brak dostępnego podsumowania dla tego kraju.</p>
        )}

        <div className="summary-metadata-grid" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {selectedCountry.national_symbols && (
            <div className="national-symbols-bar">
              <span className="symbols-label">Symbole:</span>
              <span className="symbols-value">{selectedCountry.national_symbols}</span>
            </div>
          )}
          
          {selectedCountry.unique_things && (
            <div className="national-symbols-bar" style={{ backgroundColor: '#f0fff4', borderLeftColor: '#48bb78' }}>
              <span className="symbols-label" style={{ color: '#2f855a' }}>Unikatowe:</span>
              <span className="symbols-value">{selectedCountry.unique_things}</span>
            </div>
          )}

          {/* New Souvenirs / Shopping Data Point */}
          {selectedCountry.practical.souvenirs && (
            <div className="souvenirs-box">
              <span className="souvenirs-icon">🎁</span>
              <div className="souvenirs-content">
                <span className="souvenirs-label">Co warto kupić / Pamiątki:</span>
                <div className="souvenirs-value">
                  <ExpandableText text={selectedCountry.practical.souvenirs} maxLength={200} />
                </div>
              </div>
            </div>
          )}
          
          <DataSource sources={['WIKI']} lastUpdated={selectedCountry.last_updated} />
        </div>
      </div>
    </div>
  );
};
