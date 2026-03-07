import React from 'react';
import type { CountryData } from '../../types/index';
import { CONTINENT_MAP, SAFETY_LABELS, TRAVEL_TYPES } from '../../constants';
import { getLongNameClass } from '../../utils/helpers';

interface CountryCardProps {
  country: CountryData;
  onClick: () => void;
  isFavorite: boolean;
  toggleFavorite: (iso2: string) => void;
}

const CountryCard: React.FC<CountryCardProps> = ({ country, onClick, isFavorite, toggleFavorite }) => {
  return (
    <div 
      className={`country-card risk-border-${country.safety.risk_level}`}
      onClick={onClick}
    >
      <button 
        className={`card-favorite-btn ${isFavorite ? 'always-visible is-fav' : ''}`}
        onClick={(e) => {
          e.stopPropagation();
          toggleFavorite(country.iso2);
        }}
      >
        {isFavorite ? '⭐' : '☆'}
      </button>
      <div className="card-content">
        <div className="card-travel-types">
          {(country.travel_types?.categories || []).slice(0, 3).map(catId => (
            <span key={catId} title={TRAVEL_TYPES[catId]?.label} className="travel-type-mini-icon">
              {TRAVEL_TYPES[catId]?.icon}
            </span>
          ))}
        </div>
        <img 
          src={country.flag_url} 
          alt={`Flaga ${country.name_pl}`} 
          className="main-flag-img" 
          style={{ objectFit: 'contain' }}
        />
        <h3 className={getLongNameClass(country.name_pl, 'h3')}>{country.name_pl}</h3>
        <div className="card-continent">
          {CONTINENT_MAP[country.continent] || country.continent}
        </div>
        {country.parent && (
          <div className="card-dependency">zal. {country.parent.name_pl}</div>
        )}
        <span className={`risk-badge risk-${country.safety.risk_level}`}>
          {SAFETY_LABELS[country.safety.risk_level] || country.safety.risk_level}
        </span>
      </div>
    </div>
  );
};

export default CountryCard;
