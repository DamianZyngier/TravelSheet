import React from 'react';
import type { CountryData } from '../../types/index';
import CountryCard from './CountryCard';

interface CountryGridProps {
  favoriteList: CountryData[];
  remainingList: CountryData[];
  showOnlyFavorites: boolean;
  onSelectCountry: (country: CountryData) => void;
  favorites: string[];
  toggleFavorite: (iso2: string) => void;
}

const CountryGrid: React.FC<CountryGridProps> = ({ 
  favoriteList, 
  remainingList, 
  showOnlyFavorites,
  onSelectCountry, 
  favorites, 
  toggleFavorite 
}) => {
  const hasFavorites = favoriteList.length > 0;
  const hasRemaining = remainingList.length > 0;

  if (!hasFavorites && !hasRemaining) {
    return <div className="no-results">Nie znaleziono krajów spełniających kryteria.</div>;
  }

  return (
    <div className="country-grid-container">
      {showOnlyFavorites && (
        <>
          <div className="grid-section-label">Zapamiętane kraje</div>
          {hasFavorites ? (
            <div className="country-grid">
              {favoriteList.map(country => (
                <CountryCard 
                  key={country.iso2} 
                  country={country} 
                  onClick={() => onSelectCountry(country)} 
                  isFavorite={true}
                  toggleFavorite={toggleFavorite}
                />
              ))}
            </div>
          ) : (
            <div className="empty-favorites-message">
              <p>Nie masz jeszcze żadnych ulubionych krajów.</p>
              <p className="hint">Kliknij ikonę gwiazdki ⭐ przy dowolnym kraju, aby go tu dodać i mieć do niego szybki dostęp.</p>
            </div>
          )}
          
          {hasRemaining && (
            <div className="grid-separator">
              <hr />
              <span>Pozostałe kraje</span>
            </div>
          )}
        </>
      )}

      {hasRemaining && (
        <div className="country-grid">
          {remainingList.map(country => (
            <CountryCard 
              key={country.iso2} 
              country={country} 
              onClick={() => onSelectCountry(country)} 
              isFavorite={favorites.includes(country.iso2)}
              toggleFavorite={toggleFavorite}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default CountryGrid;
