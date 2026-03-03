import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../common';

interface ReligionSectionProps {
  selectedCountry: CountryData;
}

export const ReligionSection: React.FC<ReligionSectionProps> = ({ selectedCountry }) => {
  if (!selectedCountry.religions || selectedCountry.religions.length === 0) {
    return null;
  }

  // Sort and limit to top 6 to keep it compact
  const sortedReligions = [...selectedCountry.religions]
    .sort((a, b) => b.percentage - a.percentage)
    .slice(0, 6);

  return (
    <div id="religion" className="info-block full-width religion-section compact scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">⛪</span>
        <label>Religie i wyznania</label>
      </div>
      <div className="religion-compact-grid">
        {sortedReligions.map((r, i) => (
          <div key={i} className="religion-compact-item">
            <div className="religion-compact-info">
              <span className="religion-compact-name">{r.name}</span>
              <span className="religion-compact-perc">
                {r.percentage > 0 ? `${r.percentage.toFixed(1)}%` : 'Główne wyznanie'}
              </span>
            </div>
            {r.percentage > 0 && (
              <div className="religion-compact-bar-bg">
                <div 
                  className="religion-compact-bar-fill" 
                  style={{ width: `${r.percentage}%` }}
                ></div>
              </div>
            )}
          </div>
        ))}
      </div>
      <DataSource sources={['WIKI']} lastUpdated={selectedCountry.religions[0]?.last_updated || selectedCountry.last_updated} />
    </div>
  );
};
