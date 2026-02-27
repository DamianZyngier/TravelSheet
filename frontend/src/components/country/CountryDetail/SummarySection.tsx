import React from 'react';
import { CountryData } from '../../../types';
import { ExpandableText, DataSource } from '../../Common';

interface SummarySectionProps {
  selectedCountry: CountryData;
  onSelectCountry: (country: any) => void;
  allCountries: CountryData[];
}

const SummarySection: React.FC<SummarySectionProps> = ({ selectedCountry, onSelectCountry, allCountries }) => {
  return (
    <div id="discover" className="info-block full-width scroll-mt">
      {/* Territory/Parent Relationship Information at the top */}
      {(selectedCountry.parent || (selectedCountry.territories && selectedCountry.territories.length > 0)) && (
        <div className="top-relationship-box">
          {selectedCountry.parent && (
            <div className="parent-info-line">
              <span className="relationship-tag">Terytorium państwa:</span>
              <button 
                className="relationship-text-btn"
                onClick={() => {
                  const parent = allCountries.find(c => c.iso2 === selectedCountry.parent?.iso2);
                  if (parent) onSelectCountry(parent);
                }}
              >
                📍 {selectedCountry.parent.name_pl}
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
                        const territory = allCountries.find(c => c.iso2 === t.iso2);
                        if (territory) onSelectCountry(territory);
                      }}
                    >
                      {t.name_pl}
                    </button>
                    {idx < (selectedCountry.territories?.length || 0) - 1 ? ', ' : ''}
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="section-header">
        <span className="section-header-icon">✨</span>
        <label>Odkryj i poznaj {selectedCountry.name_pl}</label>
      </div>
      
      <div className="discover-section">
        <div className="discover-container">
          {selectedCountry.wiki_summary ? (
            <div className="wiki-summary-text">
              <ExpandableText text={selectedCountry.wiki_summary} />
            </div>
          ) : (
            <p className="no-data-text">Brak dostępnego opisu dla tego kraju.</p>
          )}
          {selectedCountry.national_symbols && (
            <div className="national-symbols-bar">
              <span className="symbols-label">Symbole narodowe:</span>
              <span className="symbols-value">{selectedCountry.national_symbols}</span>
            </div>
          )}
          <DataSource sources={['WIKI']} />
        </div>
      </div>
    </div>
  );
};

export default SummarySection;
