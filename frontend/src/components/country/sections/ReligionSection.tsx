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

  // Find the max percentage to use for a small bar visualization
  const sortedReligions = [...selectedCountry.religions].sort((a, b) => b.percentage - a.percentage);

  return (
    <div id="religion" className="info-block full-width religion-section scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">⛪</span>
        <label>Religie i wyznania</label>
      </div>
      <div className="religion-content-grid">
        {sortedReligions.map((r, i) => (
          <div key={i} className="religion-row">
            <div className="religion-info">
              <span className="religion-name">{r.name}</span>
              <span className="religion-percentage">{r.percentage.toFixed(1)}%</span>
            </div>
            <div className="religion-bar-bg">
              <div 
                className="religion-bar-fill" 
                style={{ width: `${r.percentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      <DataSource sources={['WIKI']} lastUpdated={selectedCountry.religions[0]?.last_updated} />
    </div>
  );
};
