import React from 'react';
import { CountryData } from '../../types';
import CountryCard from './CountryCard';

interface CountryGridProps {
  countryList: CountryData[];
  onSelectCountry: (country: CountryData) => void;
}

const CountryGrid: React.FC<CountryGridProps> = ({ countryList, onSelectCountry }) => {
  return (
    <div className="country-grid">
      {countryList.length > 0 ? (
        countryList.map(country => (
          <CountryCard 
            key={country.iso2} 
            country={country} 
            onClick={() => onSelectCountry(country)} 
          />
        ))
      ) : (
        <div className="no-results">Nie znaleziono krajów spełniających kryteria.</div>
      )}
    </div>
  );
};

export default CountryGrid;
