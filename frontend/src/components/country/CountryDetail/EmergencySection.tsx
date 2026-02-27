import React from 'react';
import { CountryData } from '../../../types';
import { DataSource } from '../../Common';

interface EmergencySectionProps {
  selectedCountry: CountryData;
}

const EmergencySection: React.FC<EmergencySectionProps> = ({ selectedCountry }) => {
  return (
    <div id="emergency" className="info-block full-width emergency-section-box scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">🚨</span>
        <label>Telefony i Łączność</label>
      </div>
      <div className="emergency-container">
        <div className="connectivity-badges">
          {selectedCountry.practical.emergency?.member_112 && (
            <div className="emergency-112-hero mini">
              <span className="hero-112-badge">🇪🇺 112</span>
              <div className="hero-112-text">
                <strong>Europejski Numer Alarmowy</strong>
              </div>
            </div>
          )}
          {selectedCountry.practical.roaming_info && (
            <div className="roaming-badge-hero">
              <span className="roaming-icon">📱</span>
              <div className="roaming-text">
                <strong>Roam Like at Home</strong>
                <p>Rozmowy i internet jak w Polsce (UE/EOG)</p>
              </div>
            </div>
          )}
        </div>

        <div className="emergency-grid">
          <div className="emergency-item-box">
            <span className="emergency-icon">🚓</span>
            <span className="emergency-label">Policja</span>
            <span className="emergency-num">{selectedCountry.practical.emergency?.police || (selectedCountry.practical.emergency?.member_112 ? '112' : 'Brak')}</span>
          </div>
          <div className="emergency-item-box">
            <span className="emergency-icon">🚑</span>
            <span className="emergency-label">Pogotowie</span>
            <span className="emergency-num">{selectedCountry.practical.emergency?.ambulance || (selectedCountry.practical.emergency?.member_112 ? '112' : 'Brak')}</span>
          </div>
          <div className="emergency-item-box">
            <span className="emergency-icon">🚒</span>
            <span className="emergency-label">Straż</span>
            <span className="emergency-num">{selectedCountry.practical.emergency?.fire || (selectedCountry.practical.emergency?.member_112 ? '112' : 'Brak')}</span>
          </div>
        </div>
      </div>
      <DataSource sources={['MSZ', 'WIKI']} />
    </div>
  );
};

export default EmergencySection;
