import React from 'react';
import type { CountryData } from '../../../types';
import { ExpandableText, DataSource } from '../../common';

interface MiscSectionProps {
  selectedCountry: CountryData;
  isEmbassiesExpanded: boolean;
  setIsEmbassiesExpanded: (val: boolean) => void;
  isUnescoExpanded: boolean;
  setIsUnescoExpanded: (val: boolean) => void;
}

export const MiscSection: React.FC<MiscSectionProps> = ({ 
  selectedCountry, 
  isEmbassiesExpanded, 
  setIsEmbassiesExpanded,
  isUnescoExpanded,
  setIsUnescoExpanded
}) => {
  return (
    <>
      <div id="holidays" className="info-block full-width holiday-section scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">📅</span>
          <label>Święta i dni wolne</label>
        </div>

        {selectedCountry.holidays && selectedCountry.holidays.length > 0 ? (
          <div className="holiday-container">
            <div className="expanded-holiday-list">
              {Object.entries(
                ([...selectedCountry.holidays])
                  .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                  .reduce((acc, h) => {
                    const month = new Date(h.date).toLocaleDateString('pl-PL', { month: 'long' });
                    if (!acc[month]) acc[month] = [];
                    acc[month].push(h);
                    return acc;
                  }, {} as Record<string, any[]>)
              ).map(([month, monthHolidays]) => (
                <div key={month} className="holiday-month-group">
                  <h5 className="holiday-month-header">{month}</h5>
                  <div className="holiday-month-items">
                    {(monthHolidays as any[]).map((h, idx) => (
                      <div key={idx} className="holiday-item">
                        <span className="holiday-date">{new Date(h.date).toLocaleDateString('pl-PL', { day: 'numeric' })}</span>
                        <span className="holiday-name">{h.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="no-data-msg">Brak informacji o świętach dla tego kraju.</div>
        )}
        <DataSource sources={['NAGER']} lastUpdated={selectedCountry.holidays?.[0]?.last_updated || selectedCountry.last_updated} />
      </div>

      <div id="embassies" className="info-block full-width embassy-section scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">🏢</span>
          <label>Polskie placówki dyplomatyczne</label>
        </div>
        {selectedCountry.embassies && selectedCountry.embassies.length > 0 ? (
          <div className="embassy-container">
            {(() => {
              const order = ['Ambasada', 'Wydział Konsularny', 'Konsulat Generalny', 'Konsulat', 'Konsulat Honorowy', 'Placówka'];
              const sortedAll = [...selectedCountry.embassies].sort((a, b) => {
                let idxA = order.indexOf(a.type);
                let idxB = order.indexOf(b.type);
                if (idxA === -1) idxA = 99;
                if (idxB === -1) idxB = 99;
                return idxA - idxB;
              });

              const embassiesGroup = sortedAll.filter(e => e.type === 'Ambasada');
              const consulatesAll = sortedAll.filter(e => e.type !== 'Ambasada');

              const displayedConsulates = isEmbassiesExpanded ? consulatesAll : consulatesAll.slice(0, 2);
              const hasHiddenConsulates = consulatesAll.length > 2;

              const renderEmbassy = (emb: any, idx: number) => (
                <div key={idx} className="embassy-item">
                  <strong>{emb.type} {emb.city ? `w ${emb.city}` : ''}</strong>
                  {emb.address && <p>📍 {emb.address}</p>}
                  {emb.phone && <p>📞 {emb.phone}</p>}
                  {emb.email && <p>✉️ <a href={`mailto:${emb.email}`}>{emb.email}</a></p>}
                  {emb.website && <p>🌐 <a href={emb.website} target="_blank" rel="noreferrer">Strona WWW</a></p>}
                </div>
              );

              return (
                <>
                  {embassiesGroup.length > 0 && (
                    <div className="embassy-group">
                      <h4 className="embassy-group-title">Ambasada</h4>
                      <div className="embassy-grid">
                        {embassiesGroup.map(renderEmbassy)}
                      </div>
                    </div>
                  )}

                  {consulatesAll.length > 0 && (
                    <div className="embassy-group">
                      <h4 className="embassy-group-title">Konsulaty i pozostałe placówki</h4>
                      <div className="embassy-grid">
                        {displayedConsulates.map(renderEmbassy)}
                      </div>
                    </div>
                  )}

                  {hasHiddenConsulates && (
                    <button
                      className="section-expand-btn"
                      style={{ marginTop: '1rem', width: '100%' }}
                      onClick={() => setIsEmbassiesExpanded(!isEmbassiesExpanded)}
                    >
                      {isEmbassiesExpanded ? 'Pokaż mniej' : `Pokaż pozostałe placówki (${consulatesAll.length - 2})`}
                    </button>
                  )}
                </>
              );
            })()}
          </div>
        ) : (
          <div className="no-data-msg">Brak danych o polskich placówkach w tym kraju.</div>
        )}
        <DataSource sources={['MSZ']} lastUpdated={selectedCountry.embassies?.[0]?.last_updated || selectedCountry.last_updated} />
      </div>

      <div id="attractions" className="info-block full-width unesco-section scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">📍</span>
          <label>Najciekawsze miejsca i atrakcje</label>
        </div>
        {selectedCountry.attractions && selectedCountry.attractions.length > 0 ? (
          <div className="unesco-grid">
            {selectedCountry.attractions.map((attr, idx) => (
              <div key={idx} className="unesco-item-v2">
                <div className="unesco-item-content">
                  <div className="unesco-item-header">
                    <span className="unesco-icon">✨</span>
                    <span className="unesco-name">{attr.name}</span>
                  </div>
                  {attr.description && (
                    <div className="unesco-description">
                      <ExpandableText text={attr.description} />
                    </div>
                  )}
                  {attr.booking_info && (
                    <div className="booking-info-tip" style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#2c5282', backgroundColor: '#ebf8ff', padding: '0.5rem 0.75rem', borderRadius: '8px', borderLeft: '3px solid #4299e1' }}>
                      <span style={{ marginRight: '6px' }}>🎟️</span>
                      <strong>Porada:</strong> {attr.booking_info}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data-msg">Nie znaleziono szczegółowych informacji o atrakcjach turystycznych.</div>
        )}
        <DataSource sources={['WIKI']} lastUpdated={selectedCountry.attractions?.[0]?.last_updated || selectedCountry.last_updated} />
      </div>

      <div id="unesco" className="info-block full-width unesco-section scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">🏛️</span>
          <label>Lista UNESCO ({selectedCountry.unesco_count || 0})</label>
        </div>
        {selectedCountry.unesco_places && selectedCountry.unesco_places.length > 0 ? (
          <>
            <div className="unesco-grid">
              {(isUnescoExpanded ? selectedCountry.unesco_places : selectedCountry.unesco_places.slice(0, 10)).map((place, idx) => (
                <div key={idx} className="unesco-item-v2 has-link" onClick={() => {
                  if (place.unesco_id) window.open(`https://whc.unesco.org/en/list/${place.unesco_id}`, '_blank');
                }}>
                  {place.image_url && (
                    <div className="unesco-item-image">
                      <img src={place.image_url} alt={place.name} loading="lazy" />
                    </div>
                  )}
                  <div className="unesco-item-content">
                    <div className="unesco-item-header">
                      <span className="unesco-icon">
                        {place.category === 'Cultural' ? '🏛️' :
                        place.category === 'Natural' ? '🌳' :
                        place.category === 'Mixed' ? '🏔️' : '📍'}
                      </span>
                      <div className="unesco-name">{place.name}</div>
                    </div>
                    <div className="unesco-badges-container" style={{ display: 'flex', gap: '8px', marginLeft: '32px' }}>
                      <div className={`unesco-type-badge ${place.category?.toLowerCase() || ''}`}>{place.category}</div>
                      {!!place.is_transnational && <div className="unesco-type-badge transnational">MIĘDZYNARODOWE</div>}
                      {!!place.is_danger && <div className="unesco-type-badge danger">ZAGROŻONE</div>}
                    </div>

                    {place.description && (
                      <div className="unesco-description" onClick={(e) => e.stopPropagation()}>
                        <ExpandableText text={place.description} />
                      </div>
                    )}

                    {place.unesco_id && (
                      <div className="unesco-official-link">
                        Zobacz oficjalną stronę UNESCO →
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {selectedCountry.unesco_places.length > 10 && (
              <button
                className="section-expand-btn"
                style={{
                  marginTop: '0.5rem',
                  width: '100%',
                  padding: '0.4rem',
                  fontSize: '0.75rem',
                  backgroundColor: 'transparent',
                  border: '1px solid #e2e8f0',
                  color: '#718096'
                }}
                onClick={() => setIsUnescoExpanded(!isUnescoExpanded)}
              >
                {isUnescoExpanded ? 'Pokaż mniej' : `Pokaż pozostałe (${selectedCountry.unesco_places.length - 10})`}
              </button>
            )}
          </>
        ) : (
          <div className="no-data-msg">Brak wpisów na liście UNESCO dla tego kraju.</div>
        )}
        <DataSource sources={['UNESCO']} lastUpdated={selectedCountry.unesco_places?.[0]?.last_updated || selectedCountry.last_updated} />
      </div>
    </>
  );
};
