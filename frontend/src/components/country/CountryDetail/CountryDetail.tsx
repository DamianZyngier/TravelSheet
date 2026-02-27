import React, { useState } from 'react';
import { CountryData } from '../../../types';
import { getLongNameClass } from '../../Common';
import MapSection from './MapSection';
import SummarySection from './SummarySection';
import PracticalSection from './PracticalSection';
import BasicInfoSection from './BasicInfoSection';
import EmergencySection from './EmergencySection';
import SafetyHealthSection from './SafetyHealthSection';
import CostsClimateSection from './CostsClimateSection';
import MiscSection from './MiscSection';

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
      <div id="summary" className="detail-header scroll-mt">
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
        
        <MapSection 
          selectedCountry={selectedCountry}
          mapPosition={mapPosition}
          setMapPosition={setMapPosition}
          getMapSettings={getMapSettings}
        />
      </div>

      <div className="detail-body">
        <SummarySection 
          selectedCountry={selectedCountry} 
          allCountries={allCountries}
          onSelectCountry={onSelectCountry}
        />
        
        <PracticalSection 
          selectedCountry={selectedCountry}
          formatPLN={formatPLN}
          getCurrencyExample={getCurrencyExample}
          checkPlugs={checkPlugs}
          getEnlargedPlugUrl={getEnlargedPlugUrl}
        />

        <BasicInfoSection selectedCountry={selectedCountry} />

        <EmergencySection selectedCountry={selectedCountry} />

        <CostsClimateSection 
          selectedCountry={selectedCountry}
          chartTooltip={chartTooltip}
          setChartTooltip={setChartTooltip}
        />

        <SafetyHealthSection selectedCountry={selectedCountry} />

        <MiscSection 
          selectedCountry={selectedCountry}
          isEmbassiesExpanded={isEmbassiesExpanded}
          setIsEmbassiesExpanded={setIsEmbassiesExpanded}
          isUnescoExpanded={isUnescoExpanded}
          setIsUnescoExpanded={setIsUnescoExpanded}
        />
      </div>
    </div>
  );
};

export default CountryDetail;
