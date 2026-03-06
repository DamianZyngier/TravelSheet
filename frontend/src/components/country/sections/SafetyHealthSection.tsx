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
            {/* EKUZ Info */}
            <div className={`health-item ${selectedCountry.has_ekuz ? 'suggested' : 'neutral'}`}>
              <div className="health-icon">{selectedCountry.has_ekuz ? '🇪🇺' : '🏥'}</div>
              <div className="health-text">
                <strong>Karta EKUZ</strong>
                <p>
                  {selectedCountry.has_ekuz 
                    ? 'Obowiązuje w tym kraju. Zapewnia dostęp do niezbędnej opieki medycznej.' 
                    : 'Nie obowiązuje w tym kraju. Koniecznie wykup prywatne ubezpieczenie.'}
                </p>
                {selectedCountry.has_ekuz && (
                  <a 
                    href="https://www.nfz.gov.pl/dla-pacjenta/nasze-serwisy/ekuz/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="msz-link"
                    style={{ marginTop: '4px', fontSize: '0.8rem' }}
                  >
                    Wyrób kartę EKUZ (NFZ) ↗
                  </a>
                )}
              </div>
            </div>

            {selectedCountry.practical.health_info && (
              <div className="info-item-box full">
                <strong>Oficjalne zalecenia MSZ</strong>
                <ExpandableText text={selectedCountry.practical.health_info} />
              </div>
            )}

            {(selectedCountry.practical.vaccinations_required || selectedCountry.practical.vaccinations_suggested) && (
              <div className="info-grid">
                {selectedCountry.practical.vaccinations_required && (
                  <div className="info-item-box" style={{ borderLeft: '5px solid #f56565' }}>
                    <strong style={{ color: '#822727' }}>Obowiązkowe</strong>
                    <span>{selectedCountry.practical.vaccinations_required.replace(/szczepienie przeciw /gi, '').replace(/szczepienie przeciwko /gi, '').replace(/Obowiązkowe: /gi, '')}</span>
                  </div>
                )}
                {selectedCountry.practical.vaccinations_suggested && (
                  <div className="info-item-box" style={{ borderLeft: '5px solid #ecc94b' }}>
                    <strong style={{ color: '#744210' }}>Zalecane</strong>
                    <span>{selectedCountry.practical.vaccinations_suggested.replace(/Zalecane: /gi, '')}</span>
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
          <div className="info-item-box full" style={{ backgroundColor: '#ebf8ff', border: '1px solid #bee3f8', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <span style={{ fontSize: '1.25rem' }}>🛡️</span>
              <div>
                <strong>System Odyseusz</strong>
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

          {(selectedCountry.laws_and_customs && selectedCountry.laws_and_customs.length > 0) ? (
            <div className="laws-customs-list" style={{ marginTop: '1rem' }}>
              <div className="law-environment-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                {selectedCountry.laws_and_customs.map((lc, idx) => (
                  <div key={idx} className="law-item-box-v2">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span style={{ fontSize: '1.2rem' }}>
                        {lc.category === 'law' ? '⚖️' : lc.category === 'souvenir' ? '🎁' : '🤝'}
                      </span>
                      <strong style={{ color: '#2d3748' }}>{lc.title}</strong>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#4a5568', lineHeight: '1.5' }}>
                      <ExpandableText text={lc.description} maxLength={300} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (selectedCountry.alcohol_status || selectedCountry.lgbtq_status || selectedCountry.natural_hazards || selectedCountry.practical.tipping_culture || selectedCountry.practical.dress_code || selectedCountry.practical.local_norms) ? (
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
            <div className="no-data-msg">Brak szczegółowych informacji o prawie i obyczajach dla tego kraju. Sekcja w trakcie aktualizacji.</div>
          )}
          
          <DataSource sources={['MSZ', 'WIKI']} lastUpdated={selectedCountry.safety.last_updated} />
        </div>
      )}
    </>
  );
};
