import React from 'react';
import type { CountryData } from '../../../types';
import { SAFETY_LABELS } from '../../../constants';
import { DataSource, ExpandableText, LinkifyOdyseusz } from '../../common';

interface SafetyHealthSectionProps {
  selectedCountry: CountryData;
}

export const SafetyHealthSection: React.FC<SafetyHealthSectionProps> = ({ selectedCountry }) => {
  return (
    <>
      <div id="health" className="info-block full-width health-section-box scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">💉</span>
          <label>Zdrowie i szczepienia</label>
        </div>
        <div className="health-container">
          {selectedCountry.practical.health_info && (
            <div className="health-full-info">
              <strong>Oficjalne zalecenia MSZ:</strong>
              <ExpandableText text={selectedCountry.practical.health_info} />
            </div>
          )}

          {(selectedCountry.practical.vaccinations_required || selectedCountry.practical.vaccinations_suggested) && (
            <div className="health-summary-vax">
              {selectedCountry.practical.vaccinations_required && (
                <div className="health-item mandatory" style={{ backgroundColor: '#fed7d7', borderLeft: '5px solid #f56565' }}>
                  <span className="health-icon">🚨</span>
                  <div className="health-text">
                    <strong style={{ color: '#822727' }}>Obowiązkowe:</strong>
                    <p>{selectedCountry.practical.vaccinations_required.replace(/szczepienie przeciw /gi, '').replace(/szczepienie przeciwko /gi, '').replace(/Obowiązkowe: /gi, '')}</p>
                  </div>
                </div>
              )}
              {selectedCountry.practical.vaccinations_suggested && (
                <div className="health-item suggested" style={{ backgroundColor: '#fefcbf', borderLeft: '5px solid #ecc94b' }}>
                  <span className="health-icon">💉</span>
                  <div className="health-text">
                    <strong style={{ color: '#744210' }}>Zalecane:</strong>
                    <p>{selectedCountry.practical.vaccinations_suggested.replace(/Zalecane: /gi, '')}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {!selectedCountry.practical.health_info && !selectedCountry.practical.vaccinations_required && !selectedCountry.practical.vaccinations_suggested && (
            <div className="no-data-msg">Brak szczegółowych informacji o zdrowiu (sprawdź aktualny komunikat MSZ).</div>
          )}

          {selectedCountry.safety.url && (
            <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="health-msz-link">
              Pełny raport zdrowotny na gov.pl →
            </a>
          )}
        </div>
        <DataSource sources={['CDC', 'MSZ']} />
      </div>

      <div id="safety" className="info-block full-width scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">🛡️</span>
          <label>Bezpieczeństwo (MSZ)</label>
        </div>

        {/* Informacja o Odyseuszu */}
        <div className="info-item-box full" style={{ backgroundColor: '#ebf8ff', border: '1px solid #bee3f8', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '1.25rem' }}>🛡️</span>
            <div>
              <strong style={{ color: '#2b6cb0', fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>System Odyseusz:</strong>
              <span style={{ fontSize: '0.85rem', color: '#2c5282', lineHeight: '1.4' }}>
                MSZ zaleca rejestrację podróży w <a href="https://odyseusz.msz.gov.pl" target="_blank" rel="noopener noreferrer" style={{ fontWeight: '700', textDecoration: 'underline' }}>systemie Odyseusz</a>. Pozwoli to służbom konsularnym na kontakt i pomoc w sytuacjach kryzysowych.
              </span>
            </div>
          </div>
        </div>

        <div className={`safety-card risk-${selectedCountry.safety.risk_level}`}>
          <p className="risk-desc">{SAFETY_LABELS[selectedCountry.safety.risk_level] || selectedCountry.safety.risk_level}</p>
          <p className="risk-summary-text"><LinkifyOdyseusz text={selectedCountry.safety.risk_text} /></p>
          {selectedCountry.safety.risk_details && (
            <div className="risk-details-box">
              <ExpandableText text={selectedCountry.safety.risk_details} />
            </div>
          )}
          {selectedCountry.safety.url && (
            <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="msz-link">
              Zobacz pełny komunikat MSZ na gov.pl →
            </a>
          )}
        </div>

        {/* Nowa sekcja Prawo i Obyczaje */}
        {(selectedCountry.alcohol_status || selectedCountry.lgbtq_status || selectedCountry.natural_hazards) && (
          <div className="law-environment-grid" style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {selectedCountry.alcohol_status && (
              <div className="law-item" style={{ background: 'white', padding: '1rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <strong style={{ fontSize: '0.75rem', color: '#718096', textTransform: 'uppercase', display: 'block' }}>Alkohol:</strong>
                <span style={{ fontSize: '0.9rem', color: '#2d3748' }}>{selectedCountry.alcohol_status}</span>
              </div>
            )}
            {selectedCountry.lgbtq_status && (
              <div className="law-item" style={{ background: 'white', padding: '1rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <strong style={{ fontSize: '0.75rem', color: '#718096', textTransform: 'uppercase', display: 'block' }}>Prawa LGBTQ+:</strong>
                <span style={{ fontSize: '0.9rem', color: '#2d3748' }}>{selectedCountry.lgbtq_status}</span>
              </div>
            )}
            {selectedCountry.natural_hazards && (
              <div className="law-item" style={{ background: 'white', padding: '1rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <strong style={{ fontSize: '0.75rem', color: '#718096', textTransform: 'uppercase', display: 'block' }}>Zagrożenia:</strong>
                <span style={{ fontSize: '0.9rem', color: '#2d3748' }}>{selectedCountry.natural_hazards}</span>
              </div>
            )}
          </div>
        )}
        <DataSource sources={['MSZ', 'WIKI']} />
      </div>
    </>
  );
};
