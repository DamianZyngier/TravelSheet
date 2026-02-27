import React from 'react';
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps";
import type { CountryData } from '../../../types';
import { geoUrl } from '../../../constants';

interface MapSectionProps {
  selectedCountry: CountryData;
  mapPosition: { coordinates: [number, number]; zoom: number };
  setMapPosition: (pos: any) => void;
  getMapSettings: (country: CountryData) => { zoom: number; showDot: boolean };
}

export const MapSection: React.FC<MapSectionProps> = ({ 
  selectedCountry, 
  mapPosition, 
  setMapPosition, 
  getMapSettings 
}) => {
  return (
    <div className="detail-map-container">
      <ComposableMap 
        key={selectedCountry.iso2}
        projection="geoMercator"
        projectionConfig={{ 
          scale: 100
        }}
        style={{ width: "100%", height: "100%" }}
      >
        <ZoomableGroup
          center={mapPosition.coordinates}
          zoom={mapPosition.zoom}
          maxZoom={40}
          onMoveEnd={(pos) => setMapPosition(pos)}
        >
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo: any) => {
                const isSelected = 
                  geo.id === selectedCountry.iso3 || 
                  geo.properties?.iso_a3 === selectedCountry.iso3 ||
                  geo.properties?.ADM0_A3 === selectedCountry.iso3 ||
                  geo.properties?.GU_A3 === selectedCountry.iso3 ||
                  geo.properties?.name === selectedCountry.name ||
                  (selectedCountry.iso3 === "CIV" && (geo.properties?.name === "Côte d'Ivoire" || geo.properties?.name === "Cote d'Ivoire")) ||
                  (selectedCountry.iso3 === "USA" && (geo.id === "USA" || geo.properties?.name === "United States of America"));
                
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={isSelected ? "#2b6cb0" : "#EAEAEC"}
                    stroke={isSelected ? "#2b6cb0" : "#D6D6DA"}
                    strokeWidth={0.5}
                    style={{
                      default: { outline: "none" },
                      hover: { outline: "none" },
                      pressed: { outline: "none" },
                    }}
                  />
                );
              })
            }
          </Geographies>
          
          {selectedCountry.longitude !== null && selectedCountry.latitude !== null && getMapSettings(selectedCountry).showDot && (
            <Marker coordinates={[selectedCountry.longitude, selectedCountry.latitude]}>
              <circle r={0.1} fill="none" stroke="#fff" strokeWidth={20} vectorEffect="non-scaling-stroke" />
              <circle r={0.1} fill="none" stroke="#F56565" strokeWidth={14} vectorEffect="non-scaling-stroke" />
            </Marker>
          )}
        </ZoomableGroup>
      </ComposableMap>
      
      <div className="map-controls">
        <button onClick={() => setMapPosition((prev: any) => ({ ...prev, zoom: Math.min(prev.zoom * 1.5, 40) }))}>+</button>
        <button onClick={() => setMapPosition((prev: any) => ({ ...prev, zoom: Math.max(prev.zoom / 1.5, 1) }))}>-</button>
        <button onClick={() => setMapPosition({ coordinates: [selectedCountry.longitude || 0, selectedCountry.latitude || 0], zoom: getMapSettings(selectedCountry).zoom })}>🎯</button>
      </div>
    </div>
  );
};
