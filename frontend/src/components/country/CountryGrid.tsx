import React from 'react';
import type { CountryData } from '../../types';
import CountryCard from './CountryCard';

interface CountryGridProps {
  countryList: CountryData[];
  onSelectCountry: (country: CountryData) => void;
  favorites: string[];
  toggleFavorite: (iso2: string) => void;
}

const CountryGrid: React.FC<CountryGridProps> = ({ countryList, onSelectCountry, favorites, toggleFavorite }) => {
  return (
    <div className="country-grid">
      {countryList.length > 0 ? (
        countryList.map(country => (
          <CountryCard 
            key={country.iso2} 
            country={country} 
            onClick={() => onSelectCountry(country)} 
            isFavorite={favorites.includes(country.iso2)}
            toggleFavorite={toggleFavorite}
          />
        ))
      ) : (
        <div className="no-results">Nie znaleziono krajów spełniających kryteria.</div>
      )}
    </div>
  );
};

export default CountryGrid;
