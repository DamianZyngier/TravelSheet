import React, { useState, useEffect, useRef } from 'react';
import type { CountryData } from '../../types';
import { getLongNameClass } from '../../utils/helpers';
import { SECTIONS } from '../../constants';
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
  getEnlargedPlugUrl,
  activeSection
}) => {
  const [chartTooltip, setChartTooltip] = useState({ visible: false, x: 0, y: 0, text: '' });
  const [isEmbassiesExpanded, setIsEmbassiesExpanded] = useState(false);
  const [isUnescoExpanded, setIsUnescoExpanded] = useState(false);

  // Accordion state for main categories
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    '1. Przygotowanie i Formalności': true,
    '2. Zdrowie i Bezpieczeństwo': true,
    '3. Praktyczne Codzienne': true,
    '4. Warunki Środowiskowe': false,
    '5. Kultura i Atrakcje': false
  });

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => ({ ...prev, [group]: !prev[group] }));
  };

  // Logic to expand category group if a child section is active
  useEffect(() => {
    const activeCat = SECTIONS.find(s => s.id === activeSection)?.category;
    if (activeCat && !expandedGroups[activeCat]) {
      setExpandedGroups(prev => ({ ...prev, [activeCat]: true }));
    }
  }, [activeSection]);

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
        {/* 1. Przygotowanie i Formalności */}
        <div id="category-1" className={`category-group scroll-mt ${expandedGroups['1. Przygotowanie i Formalności'] ? 'expanded' : 'collapsed'}`}>
          <button className="category-group-header" onClick={() => toggleGroup('1. Przygotowanie i Formalności')}>
            <h3 className="category-group-title">1. Przygotowanie i Formalności</h3>
            <span className="category-expand-icon">{expandedGroups['1. Przygotowanie i Formalności'] ? '−' : '+'}</span>
          </button>
          {expandedGroups['1. Przygotowanie i Formalności'] && (
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
          )}
        </div>

        {/* 2. Zdrowie i Bezpieczeństwo */}
        <div id="category-2" className={`category-group scroll-mt ${expandedGroups['2. Zdrowie i Bezpieczeństwo'] ? 'expanded' : 'collapsed'}`}>
          <button className="category-group-header" onClick={() => toggleGroup('2. Zdrowie i Bezpieczeństwo')}>
            <h3 className="category-group-title">2. Zdrowie i Bezpieczeństwo</h3>
            <span className="category-expand-icon">{expandedGroups['2. Zdrowie i Bezpieczeństwo'] ? '−' : '+'}</span>
          </button>
          {expandedGroups['2. Zdrowie i Bezpieczeństwo'] && (
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
          )}
        </div>

        {/* 3. Praktyczne Codzienne */}
        <div id="category-3" className={`category-group scroll-mt ${expandedGroups['3. Praktyczne Codzienne'] ? 'expanded' : 'collapsed'}`}>
          <button className="category-group-header" onClick={() => toggleGroup('3. Praktyczne Codzienne')}>
            <h3 className="category-group-title">3. Praktyczne Codzienne</h3>
            <span className="category-expand-icon">{expandedGroups['3. Praktyczne Codzienne'] ? '−' : '+'}</span>
          </button>
          {expandedGroups['3. Praktyczne Codzienne'] && (
            <div className="category-content">
              <WeatherForecastSection selectedCountry={selectedCountry} />
              <PracticalSection 
                selectedCountry={selectedCountry}
                formatPLN={formatPLN}
                getCurrencyExample={getCurrencyExample}
                checkPlugs={checkPlugs}
                getEnlargedPlugUrl={getEnlargedPlugUrl}
                onlySections={['plugs']}
              />
              <EmergencySection selectedCountry={selectedCountry} />
              <CostsClimateSection 
                selectedCountry={selectedCountry}
                chartTooltip={chartTooltip}
                setChartTooltip={setChartTooltip}
                onlySections={['costs']}
              />
            </div>
          )}
        </div>

        {/* 4. Warunki Środowiskowe */}
        <div id="category-4" className={`category-group scroll-mt ${expandedGroups['4. Warunki Środowiskowe'] ? 'expanded' : 'collapsed'}`}>
          <button className="category-group-header" onClick={() => toggleGroup('4. Warunki Środowiskowe')}>
            <h3 className="category-group-title">4. Warunki Środowiskowe</h3>
            <span className="category-expand-icon">{expandedGroups['4. Warunki Środowiskowe'] ? '−' : '+'}</span>
          </button>
          {expandedGroups['4. Warunki Środowiskowe'] && (
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
          )}
        </div>

        {/* 5. Kultura i Atrakcje */}
        <div id="category-5" className={`category-group scroll-mt ${expandedGroups['5. Kultura i Atrakcje'] ? 'expanded' : 'collapsed'}`}>
          <button className="category-group-header" onClick={() => toggleGroup('5. Kultura i Atrakcje')}>
            <h3 className="category-group-title">5. Kultura i Atrakcje</h3>
            <span className="category-expand-icon">{expandedGroups['5. Kultura i Atrakcje'] ? '−' : '+'}</span>
          </button>
          {expandedGroups['5. Kultura i Atrakcje'] && (
            <div className="category-content">
              <SummarySection 
                selectedCountry={selectedCountry} 
                allCountries={allCountries}
                onSelectCountry={onSelectCountry}
              />
              <BasicInfoSection selectedCountry={selectedCountry} />
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
          )}
        </div>
      </div>
    </div>
  );
};

export default CountryDetail;
