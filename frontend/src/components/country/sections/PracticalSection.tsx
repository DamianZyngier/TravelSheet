import React from 'react';
import type { CountryData } from '../../../types/index';
import { CONTINENT_MAP, PLUG_IMAGES, PLUG_NAMES } from '../../../constants';
import { DataSource } from '../../common';
import { getPlugCompatibility } from '../../../utils/helpers';

interface PracticalSectionProps {
  selectedCountry: CountryData;
  formatPLN: (val: number) => string;
  getCurrencyExample: (country: CountryData) => string;
  checkPlugs: (plugs: string) => { text: string; warning: boolean; class: string };
  getEnlargedPlugUrl: (url: string) => string;
  onlySections?: string[];
}

export const PracticalSection: React.FC<PracticalSectionProps> = ({ 
  selectedCountry, 
  formatPLN, 
  getCurrencyExample,
  checkPlugs,
  getEnlargedPlugUrl,
  onlySections
}) => {
  const showAll = onlySections === undefined;
  const showDocs = showAll || onlySections?.includes('docs');
  const showCurrency = showAll || onlySections?.includes('currency');
  const showWater = showAll || onlySections?.includes('water');
  const showPlugs = showAll || onlySections?.includes('plugs');
  const showInternet = showAll || onlySections?.includes('internet') || onlySections?.includes('phones');
  const showDriving = showAll || onlySections?.includes('driving');
  const showStores = showAll || onlySections?.includes('stores');
  const showTransport = showAll || onlySections?.includes('transport');
  const showSouvenirs = showAll || onlySections?.includes('souvenirs');
  const showGeneral = showAll;

  return (
    <>
      {showGeneral && (
        <div className="info-block full-width">
          <div className="info-grid">
            <div className="info-item-box">
              <strong>Kontynent</strong>
              <span>{CONTINENT_MAP[selectedCountry.continent] || selectedCountry.continent}</span>
            </div>
            <div className="info-item-box">
              <strong>Stolica i strefa</strong>
              <span>{selectedCountry.capital || 'Brak danych'} {selectedCountry.timezone && `(${selectedCountry.timezone})`}</span>
            </div>
          </div>
        </div>
      )}

      {(showInternet || showDriving || showStores || showTransport) && (
        <div className="info-block full-width">
          <div className="info-grid">
            {showInternet && (
              <>
                <div className="info-item-box">
                  <strong>Internet i eSIM</strong>
                  <div className="driving-info-box">
                    <span>{selectedCountry.practical.esim_available ? '📱 eSIM: Dostępne' : '📱 eSIM: Brak danych'}</span>
                    {selectedCountry.practical.internet_notes && <span className="license-info">{selectedCountry.practical.internet_notes}</span>}
                  </div>
                </div>
                <div className="info-item-box">
                  <strong>Komunikacja</strong>
                  <div className="driving-info-box">
                    <span>📱 WhatsApp, Messenger</span>
                  </div>
                </div>
              </>
            )}

            {showTransport && (
              <div className="info-item-box">
                <strong>Aplikacje transportowe</strong>
                <div className="driving-info-box">
                  <span>🚗 {selectedCountry.popular_apps || 'Uber, Bolt, Lokalne taxi'}</span>
                </div>
              </div>
            )}

            {showDriving && (
              <div className="info-item-box">
                <strong>Ruch drogowy</strong>
                <div className="driving-info-box">
                  <span>{selectedCountry.practical.driving_side === 'right' ? '➡️ Prawostronny' : '⬅️ Lewostronny'}</span>
                  <span className="license-info">🚗 {selectedCountry.practical.license_type || 'Polskie / IDP'}</span>
                </div>
              </div>
            )}

            {showStores && (
              <div className="info-item-box">
                <strong>Sklepy i godziny</strong>
                <span>🕒 {selectedCountry.practical.store_hours || 'Brak danych'}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {showDocs && (
        <div id="docs" className="info-block full-width docs-section scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">🛂</span>
            <label>Wymagane dokumenty (dla Polaków)</label>
          </div>
          <div className="docs-grid">
            <div className={`doc-item ${selectedCountry.entry?.passport_required ? 'doc-yes' : 'doc-no'}`}>
              <strong>Paszport</strong>
              <span>{selectedCountry.entry?.passport_required ? '✅ TAK' : '❌ NIE'}</span>
            </div>
            <div className={`doc-item ${selectedCountry.entry?.temp_passport_allowed ? 'doc-yes' : 'doc-no'}`}>
              <strong>Paszport tymczasowy</strong>
              <span>{selectedCountry.entry?.temp_passport_allowed ? '✅ TAK' : '❌ NIE'}</span>
            </div>
            <div className={`doc-item ${selectedCountry.entry?.id_card_allowed ? 'doc-yes' : 'doc-no'}`}>
              <strong>Dowód osobisty</strong>
              <span>{selectedCountry.entry?.id_card_allowed ? '✅ TAK' : '❌ NIE'}</span>
            </div>
            <div className={`doc-item ${selectedCountry.entry?.visa_required ? 'doc-no' : 'doc-yes'}`}>
              <strong>Wiza turystyczna</strong>
              <span>
                {selectedCountry.entry?.visa_status === 'Wiza niepotrzebna' ? '✅ NIEPOTRZEBNA' : 
                  selectedCountry.entry?.visa_status ? `🛂 ${selectedCountry.entry.visa_status.toUpperCase()}` :
                  selectedCountry.entry?.visa_required ? '🛂 WYMAGANA' : '🆓 NIEPOTRZEBNA'}
              </span>
            </div>
          </div>
          <DataSource sources={['MSZ', 'WIKI']} lastUpdated={selectedCountry.practical.last_updated} />
        </div>
      )}

      {(showAll || onlySections?.includes('customs')) && (
        <div id="customs" className="info-block full-width scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">🛃</span>
            <label>Przepisy celne i limity</label>
          </div>
          <div className="customs-content-box">
            {selectedCountry.practical.customs_rules ? (
              <div className="customs-text">
                {selectedCountry.practical.customs_rules.trim().split('\n').map((line, i) => (
                  <p key={i} style={{ marginBottom: line.startsWith('**') ? '0.5rem' : '0.25rem' }}>
                    {line.startsWith('**') ? <strong>{line.replace(/\*\*/g, '')}</strong> : line}
                  </p>
                ))}
              </div>
            ) : (
              <div className="customs-text no-data-text">
                Brak szczegółowych informacji o przepisach celnych dla tego kraju. Zazwyczaj obowiązują ogólne limity międzynarodowe.
              </div>
            )}
            <div className="customs-warning-box">
              <span className="warning-icon">⚠️</span>
              <p>Zawsze sprawdzaj aktualne limity przed podróżą, szczególnie przy wywozie antyków, dużych kwot gotówki lub produktów pochodzenia zwierzęcego.</p>
            </div>
          </div>
          <DataSource sources={['MSZ', 'GOV.PL']} lastUpdated={selectedCountry.practical.last_updated} />
        </div>
      )}

      {showCurrency && (
        <div id="currency" className="info-block full-width scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">💰</span>
            <label>Waluta i płatności</label>
          </div>
          <div className="currency-payment-box">
            <div className="currency-info-line">
              <strong>Waluta:</strong> {selectedCountry.currency.name || 'Brak danych'} {selectedCountry.currency.code && `(${selectedCountry.currency.code})`}
            </div>
            {selectedCountry.currency.rate_pln && (
              <div className="currency-rate-line">
                <div className="rate-main">
                  1 {selectedCountry.currency.code} = {formatPLN(selectedCountry.currency.rate_pln)}
                  {selectedCountry.currency.relative_cost && (
                    <span className={`currency-strength-badge ${
                      selectedCountry.currency.relative_cost.includes('mocna') ? 'strong' :
                      selectedCountry.currency.relative_cost === 'Średnia' ? 'medium' : 'weak'
                    }`}>
                      {selectedCountry.currency.relative_cost}
                    </span>
                  )}
                </div>
                <small className="currency-example"> ({getCurrencyExample(selectedCountry)})</small>
              </div>
            )}
            <div className="payment-advice-grid">
              <div className="advice-item">
                <strong>Karty:</strong> <span>{selectedCountry.practical.card_acceptance || 'Średnia'}</span>
              </div>
              <div className="advice-item">
                <strong>Najlepsza waluta:</strong> <span>{selectedCountry.practical.best_exchange_currency || 'USD, EUR'}</span>
              </div>
              <div className="advice-item">
                <strong>Gdzie wymieniać:</strong> <span>{selectedCountry.practical.exchange_where || 'Na miejscu'}</span>
              </div>
              <div className="advice-item">
                <strong>Targowanie się:</strong> <span>{selectedCountry.practical.bargaining_info || 'Brak danych'}</span>
              </div>
            </div>
            {selectedCountry.practical.atm_advice && (
              <div className="atm-advice">
                <strong>Bankomaty:</strong> {selectedCountry.practical.atm_advice}
              </div>
            )}

            {selectedCountry.currency.denominations && selectedCountry.currency.denominations.length > 0 && (
              <div className="currency-visuals-box">
                <strong>Pieniądze w obiegu (gotówka)</strong>
                <div className="denom-scroll-row">
                  {selectedCountry.currency.denominations.map((d, i) => (
                    <div key={i} className="denom-card">
                      <img 
                        src={d.image_url} 
                        alt={`${d.value} ${d.type}`} 
                        className="denom-img" 
                        width="120"
                        height="70"
                        loading="lazy"
                      />
                      <span className="denom-label">{d.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <DataSource sources={['REST', 'WIKI', 'NBP']} lastUpdated={selectedCountry.currency.last_updated} />
        </div>
      )}

      {showSouvenirs && (selectedCountry.souvenirs_list && selectedCountry.souvenirs_list.length > 0 || selectedCountry.practical.souvenirs) && (
        <div id="souvenirs" className="info-block full-width scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">🎁</span>
            <label>Co kupić i pamiątki</label>
          </div>
          {selectedCountry.souvenirs_list && selectedCountry.souvenirs_list.length > 0 ? (
            <div className="souvenir-enriched-grid">
              {selectedCountry.souvenirs_list.map((s, i) => (
                <div key={i} className="souvenir-enriched-item">
                  {s.image_url && (
                    <img 
                      src={s.image_url} 
                      alt={s.name} 
                      className="souvenir-img" 
                      width="100"
                      height="100"
                      loading="lazy"
                    />
                  )}
                  <div className="souvenir-enriched-content">
                    <strong>{s.name}</strong>
                    {s.description && <p>{s.description}</p>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="info-item-box full">
              <span>{selectedCountry.practical.souvenirs}</span>
            </div>
          )}
        </div>
      )}

      {showWater && (
        <div id="water" className="info-block full-width scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">🚰</span>
            <label>Woda z kranu</label>
          </div>
          <div className="water-safety-grid">
            <div className={`water-item ${selectedCountry.practical.water_safe ? 'safe' : 'unsafe'}`}>
              <span className="water-icon">{selectedCountry.practical.water_safe ? '✅' : '❌'}</span>
              <div className="water-text">
                <strong>Do picia</strong>
                <span>{selectedCountry.practical.water_safe ? 'Zdatna (pijalna)' : 'Niezalecana (lepiej butelkowana)'}</span>
              </div>
            </div>
            <div className={`water-item ${selectedCountry.practical.water_safe_for_brushing ? 'safe' : 'unsafe'}`}>
              <span className="water-icon">{selectedCountry.practical.water_safe_for_brushing ? '✅' : '⚠️'}</span>
              <div className="water-text">
                <strong>Mycie zębów</strong>
                <span>{selectedCountry.practical.water_safe_for_brushing ? 'Bezpieczna' : 'Lepiej użyć wody butelkowanej'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {showPlugs && (
        <div id="plugs" className="info-block full-width scroll-mt">
          <div className="section-header">
            <span className="section-header-icon">🔌</span>
            <label>Gniazdka, napięcie i prąd</label>
          </div>
          
          <div className="voltage-status-box-v2">
            <div style={{ flex: '1' }}>
              <div className="voltage-label">Napięcie i częstotliwość</div>
              <div className="voltage-value">
                {selectedCountry.practical.voltage}V / {selectedCountry.practical.frequency}Hz
              </div>
            </div>
            {selectedCountry.practical.voltage ? (
              <div className={`voltage-badge-v2 ${selectedCountry.practical.voltage >= 220 && selectedCountry.practical.voltage <= 240 ? 'compat-ok' : 'compat-warn'}`}>
                {selectedCountry.practical.voltage >= 220 && selectedCountry.practical.voltage <= 240 
                  ? '✅ Zgodne z polskim standardem' 
                  : '⚠️ Wymagany konwerter napięcia'}
              </div>
            ) : null}
          </div>

          <div className="plugs-container">
            <div className="plug-types-list">
              {selectedCountry.practical.plug_types ? selectedCountry.practical.plug_types.split(',').map(type => {
                const cleanType = type.trim().toUpperCase();
                const compClass = getPlugCompatibility(cleanType);
                return (
                  <div key={type} className={`plug-icon-box ${compClass}`}>
                    <div className="plug-type-label">
                      <span className="plug-letter">Typ {cleanType}</span>
                      <span className="plug-region-name">{PLUG_NAMES[cleanType] || 'Standard lokalny'}</span>
                    </div>
                    {PLUG_IMAGES[cleanType] && (
                      <div className="plug-img-wrapper">
                        <img 
                          src={PLUG_IMAGES[cleanType]} 
                          alt={`Typ ${type}`} 
                          className="plug-img" 
                          width="50"
                          height="50"
                          loading="lazy"
                          referrerPolicy="no-referrer"
                        />
                        <div className="plug-img-enlarged">
                          <img 
                            src={getEnlargedPlugUrl(PLUG_IMAGES[cleanType])} 
                            alt={`Typ ${type} powiększony`} 
                            width="250"
                            height="250"
                            loading="lazy"
                            referrerPolicy="no-referrer"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                );
              }) : <div className="no-data-msg">Brak danych o typach gniazdek</div>}
            </div>
            <div className={`plug-comparison ${checkPlugs(selectedCountry.practical.plug_types).class}`}>
              {checkPlugs(selectedCountry.practical.plug_types).warning && '⚠️ '}
              {checkPlugs(selectedCountry.practical.plug_types).text}
            </div>
          </div>
          <DataSource sources={['REST', 'WIKI']} lastUpdated={selectedCountry.practical.last_updated} />
        </div>
      )}
    </>
  );
};
