import React, { useState } from 'react';
import type { CountryData } from '../../types';
import { getLongNameClass } from '../../utils/helpers';
import { MapSection } from './sections/MapSection';
import { SummarySection } from './sections/SummarySection';
import { PracticalSection } from './sections/PracticalSection';
import { BasicInfoSection } from './sections/BasicInfoSection';
import { EmergencySection } from './sections/EmergencySection';
import { CostsClimateSection } from './sections/CostsClimateSection';
import { MiscSection } from './sections/MiscSection';
import { SafetyHealthSection } from './sections/SafetyHealthSection';
import { WeatherForecastSection } from './sections/WeatherForecastSection';

interface CountryDetailProps {
  selectedCountry: CountryData;
  allCountries: CountryData[];
  onSelectCountry: (country: CountryData) => void;
  mapPosition: { coordinates: [number, number]; zoom: number };
  setMapPosition: (pos: any) => void;
  getMapSettings: (country: CountryData) => { zoom: number; showDot: boolean };
  formatPLN: (val: number) => string;
  getCurrencyExample: (country: CountryData) => string;
  checkPlugs: (plugs: string) => { text: string; warning: boolean; class: string };
  getEnlargedPlugUrl: (url: string) => string;
  activeSection: string;
}

const CountryDetail: React.FC<CountryDetailProps> = ({
  selectedCountry,
  allCountries,
  onSelectCountry,
  mapPosition,
  setMapPosition,
  getMapSettings,
  formatPLN,
  getCurrencyExample,
  checkPlugs,
  getEnlargedPlugUrl
}) => {
  const [chartTooltip, setChartTooltip] = useState({ visible: false, x: 0, y: 0, text: '' });
  const [isEmbassiesExpanded, setIsEmbassiesExpanded] = useState(false);
  const [isUnescoExpanded, setIsUnescoExpanded] = useState(false);

  return (
    <div className="detail-card">
      <div className="detail-body">
        {/* 0. Podsumowanie */}
        <div id="summary" className="category-group scroll-mt">
          <div className="category-group-header-simple">
            <h3 className="category-group-title">Podsumowanie</h3>
          </div>
          <div className="category-content">
            <div className="detail-header-group">
              <div className="header-info-flex">
                <img 
                  src={selectedCountry.flag_url} 
                  alt={`Flaga ${selectedCountry.name_pl}`} 
                  className="detail-flag-img" 
                  style={{ objectFit: 'contain' }}
                />
                <div className="detail-titles">
                  <h2 className={getLongNameClass(selectedCountry.name_pl, 'h2')}>{selectedCountry.name_pl}</h2>
                  <p>{selectedCountry.name} ({selectedCountry.iso2})</p>
                </div>
              </div>
              
              <MapSection 
                selectedCountry={selectedCountry}
                mapPosition={mapPosition}
                setMapPosition={setMapPosition}
                getMapSettings={getMapSettings}
              />
            </div>

            <SummarySection 
              selectedCountry={selectedCountry} 
              allCountries={allCountries}
              onSelectCountry={onSelectCountry}
            />
            
            <BasicInfoSection selectedCountry={selectedCountry} />
          </div>
        </div>

        {/* 1. Przygotowanie i Formalności */}
        <div id="category-1" className="category-group scroll-mt">
          <div className="category-group-header-simple">
            <h3 className="category-group-title">1. Przygotowanie i Formalności</h3>
          </div>
          <div className="category-content">
            <PracticalSection 
              selectedCountry={selectedCountry}
              formatPLN={formatPLN}
              getCurrencyExample={getCurrencyExample}
              checkPlugs={checkPlugs}
              getEnlargedPlugUrl={getEnlargedPlugUrl}
              onlySections={['docs', 'currency']}
            />
            <MiscSection 
              selectedCountry={selectedCountry}
              isEmbassiesExpanded={isEmbassiesExpanded}
              setIsEmbassiesExpanded={setIsEmbassiesExpanded}
              isUnescoExpanded={isUnescoExpanded}
              setIsUnescoExpanded={setIsUnescoExpanded}
              onlySections={['embassies']}
            />
          </div>
        </div>

        {/* 2. Zdrowie i Bezpieczeństwo */}
        <div id="category-2" className="category-group scroll-mt">
          <div className="category-group-header-simple">
            <h3 className="category-group-title">2. Zdrowie i Bezpieczeństwo</h3>
          </div>
          <div className="category-content">
            <SafetyHealthSection 
              selectedCountry={selectedCountry} 
              onlySections={['health', 'safety']}
            />
            <PracticalSection 
              selectedCountry={selectedCountry}
              formatPLN={formatPLN}
              getCurrencyExample={getCurrencyExample}
              checkPlugs={checkPlugs}
              getEnlargedPlugUrl={getEnlargedPlugUrl}
              onlySections={['water']}
            />
          </div>
        </div>

        {/* 3. Praktyczne Codzienne */}
        <div id="category-3" className="category-group scroll-mt">
          <div className="category-group-header-simple">
            <h3 className="category-group-title">3. Informacje Praktyczne</h3>
          </div>
          <div className="category-content">
            <WeatherForecastSection selectedCountry={selectedCountry} />
            <PracticalSection 
              selectedCountry={selectedCountry}
              formatPLN={formatPLN}
              getCurrencyExample={getCurrencyExample}
              checkPlugs={checkPlugs}
              getEnlargedPlugUrl={getEnlargedPlugUrl}
              onlySections={['plugs', 'phones', 'driving', 'stores']}
            />
            <EmergencySection selectedCountry={selectedCountry} />
            <CostsClimateSection 
              selectedCountry={selectedCountry}
              chartTooltip={chartTooltip}
              setChartTooltip={setChartTooltip}
              onlySections={['costs']}
            />
          </div>
        </div>

        {/* 4. Warunki Środowiskowe */}
        <div id="category-4" className="category-group scroll-mt">
          <div className="category-group-header-simple">
            <h3 className="category-group-title">4. Warunki Środowiskowe</h3>
          </div>
          <div className="category-content">
            <CostsClimateSection 
              selectedCountry={selectedCountry}
              chartTooltip={chartTooltip}
              setChartTooltip={setChartTooltip}
              onlySections={['climate']}
            />
            <MiscSection 
              selectedCountry={selectedCountry}
              isEmbassiesExpanded={isEmbassiesExpanded}
              setIsEmbassiesExpanded={setIsEmbassiesExpanded}
              isUnescoExpanded={isUnescoExpanded}
              setIsUnescoExpanded={setIsUnescoExpanded}
              onlySections={['holidays']}
            />
          </div>
        </div>

        {/* 5. Kultura i Atrakcje */}
        <div id="category-5" className="category-group scroll-mt">
          <div className="category-group-header-simple">
            <h3 className="category-group-title">5. Kultura i Atrakcje</h3>
          </div>
          <div className="category-content">
            <MiscSection 
              selectedCountry={selectedCountry}
              isEmbassiesExpanded={isEmbassiesExpanded}
              setIsEmbassiesExpanded={setIsEmbassiesExpanded}
              isUnescoExpanded={isUnescoExpanded}
              setIsUnescoExpanded={setIsUnescoExpanded}
              onlySections={['attractions', 'souvenirs']}
            />
            <SafetyHealthSection 
              selectedCountry={selectedCountry} 
              onlySections={['law']}
            />
            <MiscSection 
              selectedCountry={selectedCountry}
              isEmbassiesExpanded={isEmbassiesExpanded}
              setIsEmbassiesExpanded={setIsEmbassiesExpanded}
              isUnescoExpanded={isUnescoExpanded}
              setIsUnescoExpanded={setIsUnescoExpanded}
              onlySections={['unesco']}
            />
          </div>
        </div>
      </div>

      {/* Global Travel Disclaimer */}
      <div className="global-travel-disclaimer">
        ⚠️ Zawsze weryfikuj informacje w oficjalnych źródłach rządowych przed podróżą; przepisy często ulegają zmianom.
      </div>
    </div>
  );
};

export default CountryDetail;
