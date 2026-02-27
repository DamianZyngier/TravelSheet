import React from 'react';
import type { CountryData } from '../../types';
import { CONTINENT_MAP, SAFETY_LABELS } from '../../constants';
import { getLongNameClass } from '../../utils/helpers';

interface CountryCardProps {
  country: CountryData;
  onClick: () => void;
}

const CountryCard: React.FC<CountryCardProps> = ({ country, onClick }) => {
  return (
    <div 
      className={`country-card risk-border-${country.safety.risk_level}`}
      onClick={onClick}
    >
      <div className="card-content">
        <img 
          src={country.flag_url} 
          alt={`Flaga ${country.name_pl}`} 
          className="main-flag-img" 
          style={{ objectFit: 'contain' }}
        />
        <h3 className={getLongNameClass(country.name_pl, 'h3')}>{country.name_pl}</h3>
        <p className="card-continent">
          {CONTINENT_MAP[country.continent] || country.continent}
          {country.parent && (
            <span className="card-dependency"> (zal. {country.parent.name_pl})</span>
          )}
        </p>
        <span className={`risk-badge risk-${country.safety.risk_level}`}>
          {SAFETY_LABELS[country.safety.risk_level] || country.safety.risk_level}
        </span>
      </div>
    </div>
  );
};

export default CountryCard;
