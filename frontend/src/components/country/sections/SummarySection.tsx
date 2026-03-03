import React from 'react';
import type { CountryData } from '../../../types';
import { ExpandableText, DataSource } from '../../common';
import { TRAVEL_TYPES } from '../../../constants';

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
      <div className="discover-container info-block">
        <div className="section-header">
          <span className="section-header-icon">✨</span>
          <label>Odkryj i poznaj kraj</label>
        </div>

        <div id="discover" className=" full-width discover-section scroll-mt">
        {/* Travel Types Section */}
        {selectedCountry.travel_types?.categories?.length > 0 && (
          <div className="travel-types-container">
            <h4 className="travel-types-title">Polecane rodzaje podróży</h4>
            <div className="travel-types-grid">
              {selectedCountry.travel_types.categories.map(catId => {
                const type = TRAVEL_TYPES[catId];
                if (!type) return null;
                return (
                  <div key={catId} className="travel-type-summary-item">
                    <span className="travel-type-summary-icon">{type.icon}</span>
                    <div className="travel-type-summary-content">
                      <span className="travel-type-summary-label">{type.label}</span>
                      <p className="travel-type-summary-desc">{type.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Parent / Territory Relationships */}
        {(selectedCountry.parent || (selectedCountry.territories && selectedCountry.territories.length > 0)) && (
          <div className="relationship-nav-box">
            {selectedCountry.parent && (
              <div className="parent-info-line">
                <span className="relationship-tag">Terytorium zależne od:</span>
                <button 
                  className="relationship-text-btn"
                  onClick={() => {
                    const parent = allCountries.find(c => c.iso2 === selectedCountry.parent?.iso2);
                    if (parent) onSelectCountry(parent);
                  }}
                >
                  {selectedCountry.parent.name_pl}
                </button>
              </div>
            )}
            
            {selectedCountry.territories && selectedCountry.territories.length > 0 && (
              <div className="territories-info-line">
                <span className="relationship-tag">Terytoria zależne:</span>
                <div className="territories-text-list">
                  {selectedCountry.territories.map((t, idx) => (
                    <React.Fragment key={t.iso2}>
                      <button 
                        className="relationship-text-btn"
                        onClick={() => {
                          const target = allCountries.find(c => c.iso2 === t.iso2);
                          if (target) onSelectCountry(target);
                        }}
                      >
                        {t.name_pl}
                      </button>
                      {idx < selectedCountry.territories!.length - 1 ? ', ' : ''}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

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
          
          <DataSource sources={['WIKI']} lastUpdated={selectedCountry.last_updated} />
        </div>
      </div>
    </div>
  );
};
