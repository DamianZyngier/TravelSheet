import React from 'react';
import type { CountryData } from '../../../types';
import { CONTINENT_MAP, PLUG_IMAGES } from '../../../constants';
import { DataSource } from '../../Common';

interface PracticalSectionProps {
  selectedCountry: CountryData;
  formatPLN: (val: number) => string;
  getCurrencyExample: (country: CountryData) => string;
  checkPlugs: (plugs: string) => { text: string; warning: boolean; class: string };
  getEnlargedPlugUrl: (url: string) => string;
}

const PracticalSection: React.FC<PracticalSectionProps> = ({ 
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
          <label>Waluta</label>
        </div>
        <span>
          {selectedCountry.currency.name || 'Brak danych'} {selectedCountry.currency.code && `(${selectedCountry.currency.code})`} <br/>
          {selectedCountry.currency.rate_pln ? (
            <>
              1 {selectedCountry.currency.code} = {formatPLN(selectedCountry.currency.rate_pln)}
              <br/>
              <small style={{ color: '#718096' }}>{getCurrencyExample(selectedCountry)}</small>
            </>
          ) : 'brak danych o kursie'}
        </span>
        <DataSource sources={['REST', 'WIKI']} />
      </div>

      <div id="plugs" className="info-block full-width scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">🔌</span>
          <label>Gniazdka elektryczne</label>
        </div>
        <div className="plugs-container">
          <div className="plug-types-list">
            {selectedCountry.practical.plug_types ? selectedCountry.practical.plug_types.split(',').map(type => (
              <div key={type} className="plug-icon-box">
                <span className="plug-letter">Typ {type.trim()}</span>
                {PLUG_IMAGES[type.trim().toUpperCase()] && (
                  <div className="plug-img-wrapper">
                    <img src={PLUG_IMAGES[type.trim().toUpperCase()]} alt={`Typ ${type}`} className="plug-img" referrerPolicy="no-referrer" />
                    <div className="plug-img-enlarged">
                      <img src={getEnlargedPlugUrl(PLUG_IMAGES[type.trim().toUpperCase()])} alt={`Typ ${type} powiększony`} referrerPolicy="no-referrer" />
                    </div>
                  </div>
                )}
              </div>
            )) : <div className="no-data-msg">Brak danych o typach gniazdek</div>}
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

export default PracticalSection;
