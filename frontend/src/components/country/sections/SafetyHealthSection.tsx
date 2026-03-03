import React from 'react';
import type { CountryData } from '../../../types';
import { SAFETY_LABELS } from '../../../constants';
import { DataSource, ExpandableText, LinkifyOdyseusz } from '../../common';

interface SafetyHealthSectionProps {
  selectedCountry: CountryData;
  onlySections?: string[];
}

export const SafetyHealthSection: React.FC<SafetyHealthSectionProps> = ({ selectedCountry, onlySections }) => {
  const showAll = onlySections === undefined;
  const showHealth = showAll || onlySections?.includes('health');
  const showSafety = showAll || onlySections?.includes('safety');
  const showLaw = showAll || onlySections?.includes('law');

  return (
    <>
      {showHealth && (
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
          <DataSource sources={['CDC', 'MSZ']} lastUpdated={selectedCountry.practical.last_updated || selectedCountry.safety.last_updated} />
        </div>
      )}

      {showSafety && (
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
            <div className="safety-card-header">
              <p className="risk-desc">{SAFETY_LABELS[selectedCountry.safety.risk_level] || selectedCountry.safety.risk_level}</p>
              {selectedCountry.safety.url && (
                <a href={selectedCountry.safety.url} target="_blank" rel="noreferrer" className="msz-external-badge">
                  Oficjalny komunikat MSZ ↗
                </a>
              )}
            </div>
            
            <p className="risk-summary-text"><LinkifyOdyseusz text={selectedCountry.safety.risk_text} /></p>
            {selectedCountry.safety.risk_details && (
              <div className="risk-details-box">
                <ExpandableText text={selectedCountry.safety.risk_details} />
              </div>
            )}
          </div>
          <DataSource sources={['MSZ']} lastUpdated={selectedCountry.safety.last_updated} />
        </div>
      )}

      {showLaw && (
        <div id="law" className="info-block full-width scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">⚖️</span>
            <label>Prawo i obyczaje</label>
          </div>

          {(selectedCountry.alcohol_status || selectedCountry.lgbtq_status || selectedCountry.natural_hazards || selectedCountry.practical.tipping_culture || selectedCountry.practical.dress_code || selectedCountry.practical.local_norms) ? (
            <div className="law-environment-grid" style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
              {selectedCountry.alcohol_status && selectedCountry.alcohol_status !== selectedCountry.practical.local_norms && (
                <div className="law-item">
                  <strong>Alkohol:</strong>
                  <span>{selectedCountry.alcohol_status}</span>
                  {selectedCountry.practical.drinking_age && <small> (Wiek: {selectedCountry.practical.drinking_age})</small>}
                  {selectedCountry.practical.alcohol_rules && selectedCountry.practical.alcohol_rules !== selectedCountry.practical.local_norms && (
                    <p className="law-subtext">{selectedCountry.practical.alcohol_rules}</p>
                  )}
                </div>
              )}
              {selectedCountry.lgbtq_status && selectedCountry.lgbtq_status !== selectedCountry.practical.local_norms && (
                <div className="law-item">
                  <strong>Prawa LGBTQ+:</strong>
                  <span>{selectedCountry.lgbtq_status}</span>
                </div>
              )}
              {selectedCountry.practical.dress_code && selectedCountry.practical.dress_code !== selectedCountry.practical.local_norms && (
                <div className="law-item">
                  <strong>Ubiór i normy:</strong>
                  <p className="law-subtext">{selectedCountry.practical.dress_code}</p>
                </div>
              )}
              {selectedCountry.practical.photography_restrictions && selectedCountry.practical.photography_restrictions !== selectedCountry.practical.local_norms && (
                <div className="law-item">
                  <strong>Fotografowanie:</strong>
                  <p className="law-subtext">{selectedCountry.practical.photography_restrictions}</p>
                </div>
              )}
              {selectedCountry.practical.sensitive_topics && (
                <div className="law-item">
                  <strong>Tematy wrażliwe:</strong>
                  <p className="law-subtext">{selectedCountry.practical.sensitive_topics}</p>
                </div>
              )}
              {selectedCountry.practical.local_norms && (
                <div className="law-item full-width-grid">
                  <strong>Lokalne obyczaje:</strong>
                  <ExpandableText text={selectedCountry.practical.local_norms} />
                </div>
              )}
              {selectedCountry.practical.tipping_culture && selectedCountry.practical.tipping_culture !== selectedCountry.practical.local_norms && (
                <div className="law-item">
                  <strong>Napiwki:</strong>
                  <p className="law-subtext">{selectedCountry.practical.tipping_culture}</p>
                </div>
              )}
              {selectedCountry.natural_hazards && (
                <div className="law-item">
                  <strong>Zagrożenia naturalne:</strong>
                  <span style={{ fontSize: '0.9rem', color: '#2d3748' }}>{selectedCountry.natural_hazards}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="no-data-msg">Brak szczegółowych informacji o prawie i obyczajach dla tego kraju.</div>
          )}
          
          <div className="travel-disclaimer">
            ⚠️ Zawsze weryfikuj informacje w oficjalnych źródłach rządowych przed podróżą; przepisy często ulegają zmianom.
          </div>

          <DataSource sources={['MSZ', 'WIKI']} lastUpdated={selectedCountry.safety.last_updated} />
        </div>
      )}
    </>
  );
};
