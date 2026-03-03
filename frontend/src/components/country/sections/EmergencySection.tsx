import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../common';

interface EmergencySectionProps {
  selectedCountry: CountryData;
}

export const EmergencySection: React.FC<EmergencySectionProps> = ({ selectedCountry }) => {
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
            {selectedCountry.practical.emergency?.police || selectedCountry.practical.emergency?.member_112 ? (
              <a href={`tel:${selectedCountry.practical.emergency?.police || '112'}`} className="emergency-num clickable-phone">
                {selectedCountry.practical.emergency?.police || '112'}
              </a>
            ) : (
              <span className="emergency-num">Brak</span>
            )}
          </div>
          <div className="emergency-item-box">
            <span className="emergency-icon">🚑</span>
            <span className="emergency-label">Pogotowie</span>
            {selectedCountry.practical.emergency?.ambulance || selectedCountry.practical.emergency?.member_112 ? (
              <a href={`tel:${selectedCountry.practical.emergency?.ambulance || '112'}`} className="emergency-num clickable-phone">
                {selectedCountry.practical.emergency?.ambulance || '112'}
              </a>
            ) : (
              <span className="emergency-num">Brak</span>
            )}
          </div>
          <div className="emergency-item-box">
            <span className="emergency-icon">🚒</span>
            <span className="emergency-label">Straż</span>
            {selectedCountry.practical.emergency?.fire || selectedCountry.practical.emergency?.member_112 ? (
              <a href={`tel:${selectedCountry.practical.emergency?.fire || '112'}`} className="emergency-num clickable-phone">
                {selectedCountry.practical.emergency?.fire || '112'}
              </a>
            ) : (
              <span className="emergency-num">Brak</span>
            )}
          </div>
        </div>
      </div>
      <DataSource sources={['MSZ', 'WIKI']} />
    </div>
  );
};
