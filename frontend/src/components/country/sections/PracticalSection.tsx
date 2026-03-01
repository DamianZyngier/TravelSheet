import React from 'react';
import type { CountryData } from '../../../types';
import { CONTINENT_MAP, PLUG_IMAGES, PLUG_NAMES } from '../../../constants';
import { DataSource } from '../../common';
import { getPlugCompatibility } from '../../../utils/helpers';

interface PracticalSectionProps {
  selectedCountry: CountryData;
  formatPLN: (val: number) => string;
  getCurrencyExample: (country: CountryData) => string;
  checkPlugs: (plugs: string) => { text: string; warning: boolean; class: string };
  getEnlargedPlugUrl: (url: string) => string;
}

export const PracticalSection: React.FC<PracticalSectionProps> = ({ 
  selectedCountry, 
  formatPLN, 
  getCurrencyExample,
  checkPlugs,
  getEnlargedPlugUrl
}) => {
  return (
    <>
      <div className="info-block full-width">
        <div className="info-grid">
          <div className="info-block">
            <label>Kontynent</label>
            <span>{CONTINENT_MAP[selectedCountry.continent] || selectedCountry.continent}</span>
          </div>
          <div className="info-block">
            <label>Stolica</label>
            <span>{selectedCountry.capital || 'Brak danych'}</span>
          </div>
          
          {selectedCountry.weather?.temp !== null && (
            <div className="info-block weather-top-block">
              <label>Pogoda teraz</label>
              <div className="weather-brief">
                {selectedCountry.weather?.icon && (
                  <img 
                    src={`https://openweathermap.org/img/wn/${selectedCountry.weather.icon}.png`} 
                    alt={selectedCountry.weather.condition} 
                    className="weather-mini-icon"
                  />
                )}
                <span className="weather-temp-main">{Math.round(selectedCountry.weather?.temp || 0)}°C</span>
              </div>
            </div>
          )}

          {selectedCountry.timezone && (
            <div className="info-block">
              <label>Strefa czasowa</label>
              <span>{selectedCountry.timezone}</span>
            </div>
          )}

          {selectedCountry.national_dish && (
            <div className="info-block">
              <label>Potrawa narodowa</label>
              <span>🍽️ {selectedCountry.national_dish}</span>
            </div>
          )}

          <div className="info-block">
            <label>Ruch drogowy</label>
            <div className="driving-info-box">
              <span>{selectedCountry.practical.driving_side === 'right' ? '➡️ Prawostronny' : '⬅️ Lewostronny'}</span>
              <span className="license-info">🚗 {selectedCountry.practical.license_type || 'Polskie / IDP'}</span>
            </div>
          </div>
        </div>
      </div>

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
        <DataSource sources={['MSZ', 'WIKI']} />
      </div>

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
              1 {selectedCountry.currency.code} = {formatPLN(selectedCountry.currency.rate_pln)}
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
          </div>
          {selectedCountry.practical.atm_advice && (
            <div className="atm-advice">
              <strong>Bankomaty:</strong> {selectedCountry.practical.atm_advice}
            </div>
          )}
        </div>
        <DataSource sources={['REST', 'WIKI']} />
      </div>

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

      <div id="plugs" className="info-block full-width scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">🔌</span>
          <label>Gniazdka elektryczne</label>
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
                      <img src={PLUG_IMAGES[cleanType]} alt={`Typ ${type}`} className="plug-img" referrerPolicy="no-referrer" />
                      <div className="plug-img-enlarged">
                        <img src={getEnlargedPlugUrl(PLUG_IMAGES[cleanType])} alt={`Typ ${type} powiększony`} referrerPolicy="no-referrer" />
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
        <DataSource sources={['REST', 'WIKI']} />
      </div>
    </>
  );
};
