import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../common';

interface WeatherForecastSectionProps {
  selectedCountry: CountryData;
}

export const WeatherForecastSection: React.FC<WeatherForecastSectionProps> = ({ selectedCountry }) => {
  return (
    <div id="weather-forecast" className="info-block full-width scroll-mt">
      <div className="section-header">
        <span className="section-header-icon">🌦️</span>
        <label>Pogoda: dziś i na najbliższy tydzień</label>
      </div>
      <div className="weather-forecast-container">
        {selectedCountry.weather?.forecast && selectedCountry.weather.forecast.length > 0 ? (
          <div className="forecast-scroll-wrapper">
            {selectedCountry.weather.forecast.map((day, idx) => (
              <div key={idx} className={`forecast-day-card ${idx === 0 ? 'today' : ''}`}>
                <span className="forecast-date">
                  {idx === 0 ? 'Dziś' : new Date(day.date).toLocaleDateString('pl-PL', { weekday: 'short', day: 'numeric' })}
                </span>
                <img 
                  src={`https://openweathermap.org/img/wn/${day.icon}.png`} 
                  alt={day.condition} 
                  className="forecast-icon"
                />
                <div className="forecast-temps">
                  <span className="temp-max">{Math.round(day.temp_max)}°</span>
                  <span className="temp-min">{Math.round(day.temp_min)}°</span>
                </div>
                <span className="forecast-condition">{day.condition}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data-msg">Brak szczegółowych danych o prognozie pogody.</div>
        )}
      </div>
      <DataSource sources={['METEO']} lastUpdated={selectedCountry.weather?.last_updated} />
    </div>
  );
};
