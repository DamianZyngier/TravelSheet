import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../common';

interface CostsClimateSectionProps {
  selectedCountry: CountryData;
  chartTooltip: { visible: boolean; x: number; y: number; text: string };
  setChartTooltip: (tooltip: any) => void;
}

export const CostsClimateSection: React.FC<CostsClimateSectionProps> = ({ 
  selectedCountry, 
  chartTooltip, 
  setChartTooltip 
}) => {
  // Helper to get month name
  const getMonthName = (m: number) => {
    return new Date(2024, m - 1).toLocaleDateString('pl-PL', { month: 'long' });
  };

  // Helper to calculate best travel months
  const getBestTravelTime = () => {
    if (!selectedCountry.climate || selectedCountry.climate.length === 0) return null;
    
    // Scoring logic: low rain is good, temperature between 18-28 is best
    const scoredMonths = selectedCountry.climate.map(cl => {
      let score = 0;
      if (cl.rain < 40) score += 3;
      else if (cl.rain < 80) score += 1;
      
      if (cl.temp_day >= 18 && cl.temp_day <= 28) score += 3;
      else if (cl.temp_day > 28 && cl.temp_day <= 33) score += 1;
      
      return { month: cl.month, score };
    });

    const bestMonths = scoredMonths
      .filter(m => m.score >= 4)
      .map(m => getMonthName(m.month));

    if (bestMonths.length === 0) {
      // Fallback: just return months with least rain
      const minRain = Math.min(...selectedCountry.climate.map(c => c.rain));
      return selectedCountry.climate
        .filter(c => c.rain === minRain)
        .map(c => getMonthName(c.month));
    }

    return bestMonths;
  };

  const bestMonthsList = getBestTravelTime();
  
  // Check if rainfall data is worth showing
  const hasRainfall = selectedCountry.climate?.some(cl => cl.rain > 0);

  return (
    <>
      <div id="costs" className="info-block full-width costs-section-box scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">📊</span>
          <label>Ceny w porównaniu do Polski</label>
        </div>
        <div className="costs-container">
          {selectedCountry.costs?.ratio_to_pl ? (
            <>
              <div className="costs-main-info">
                <span className={`costs-badge ${
                  selectedCountry.costs.ratio_to_pl < 0.7 ? 'much-cheaper' :
                  selectedCountry.costs.ratio_to_pl < 0.9 ? 'cheaper' :
                  selectedCountry.costs.ratio_to_pl < 1.1 ? 'similar' :
                  selectedCountry.costs.ratio_to_pl < 1.5 ? 'expensive' : 'much-expensive'
                }`}>
                  {selectedCountry.costs.ratio_to_pl < 0.7 ? 'Znacznie taniej niż w PL' :
                   selectedCountry.costs.ratio_to_pl < 0.9 ? 'Taniej niż w PL' :
                   selectedCountry.costs.ratio_to_pl < 1.1 ? 'Ceny zbliżone do PL' :
                   selectedCountry.costs.ratio_to_pl < 1.5 ? 'Drożej niż w PL' : 'Znacznie drożej niż w PL'}
                </span>
                <span className="costs-ratio">
                  Średnio: <strong>{(selectedCountry.costs.ratio_to_pl * 100).toFixed(0)}%</strong> cen w PL
                </span>
              </div>

              <div className="costs-visual-chart">
                <div className="costs-markers">
                  {[0, 50, 100, 150, 200].map(p => (
                    <div key={p} className="marker-line-group" style={{ left: `${(p / 200) * 100}%` }}>
                      <span className="marker-label">{p}%</span>
                      <div className={`marker-line ${p === 100 ? 'base' : ''}`}></div>
                    </div>
                  ))}
                </div>

                <div className="costs-bars-list">
                  {[
                    { label: 'Restauracje', icon: '🍔', val: selectedCountry.costs.restaurants ? selectedCountry.costs.restaurants / 0.42 : null },
                    { label: 'Zakupy', icon: '🛒', val: selectedCountry.costs.groceries ? selectedCountry.costs.groceries / 0.42 : null },
                    { label: 'Transport', icon: '🚌', val: selectedCountry.costs.transport ? selectedCountry.costs.transport / 0.42 : null },
                    { label: 'Nocleg', icon: '🏨', val: selectedCountry.costs.accommodation ? selectedCountry.costs.accommodation / 0.42 : null },
                  ].map((item, idx) => {
                    const isOverflow = (item.val || 0) > 200;
                    return (
                      <div key={idx} className="cost-bar-row">
                        <div className="cost-bar-label-box">
                          <span className="cost-bar-icon">{item.icon}</span>
                          <span className="cost-bar-name">{item.label}</span>
                        </div>
                        <div className="cost-bar-wrapper">
                          {item.val !== null ? (
                            <div
                              className={`cost-bar-fill-v2 ${isOverflow ? 'overflow' : ''}`}
                              style={{
                                width: `${Math.min(100, (item.val / 200) * 100)}%`,
                                backgroundColor: item.val < 90 ? '#48bb78' : item.val < 110 ? '#4299e1' : isOverflow ? '#9b2c2c' : '#f56565'
                              }}
                            >
                              <span className="cost-bar-value">
                                {item.val.toFixed(0)}%{isOverflow ? '+' : ''}
                              </span>
                            </div>
                          ) : (
                            <div className="cost-bar-no-data">Brak danych</div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              {selectedCountry.costs.daily_budget_mid && (
                <div className="budget-estimates-grid">
                  <div className="budget-card low">
                    <div className="budget-card-icon">🎒</div>
                    <div className="budget-card-content">
                      <span className="budget-label">Oszczędnie</span>
                      <span className="budget-value">{selectedCountry.costs.daily_budget_low?.toFixed(0)} PLN / dzień</span>
                      <p className="budget-desc">Hostel, jedzenie market/streetfood, transport publiczny.</p>
                    </div>
                  </div>
                  <div className="budget-card mid">
                    <div className="budget-card-icon">🏨</div>
                    <div className="budget-card-content">
                      <span className="budget-label">Standardowo</span>
                      <span className="budget-value">{selectedCountry.costs.daily_budget_mid?.toFixed(0)} PLN / dzień</span>
                      <p className="budget-desc">Hotel budget, posiłki w barach, kilka płatnych atrakcji.</p>
                    </div>
                  </div>
                  <div className="budget-card high">
                    <div className="budget-card-icon">✨</div>
                    <div className="budget-card-content">
                      <span className="budget-label">Komfortowo</span>
                      <span className="budget-value">{selectedCountry.costs.daily_budget_high?.toFixed(0)} PLN / dzień</span>
                      <p className="budget-desc">Hotel mid-range, restauracje, wynajem auta lub wycieczki.</p>
                    </div>
                  </div>
                </div>
              )}

              <p className="costs-disclaimer">* Wartości przybliżone w oparciu o koszty w Polsce (100%)</p>
            </>
          ) : (
            <div className="costs-no-data-placeholder">
              <span className="no-data-icon">📉</span>
              <p>Brak dostępnych danych statystycznych o kosztach życia dla tego kraju.</p>
            </div>
          )}
        </div>
        <DataSource sources={['NUMBEO']} lastUpdated={selectedCountry.costs?.last_updated} />
      </div>

      <div id="climate" className="info-block full-width climate-section scroll-mt">
        <div className="section-header">
          <span className="section-header-icon">🌤️</span>
          <label>Typowa pogoda (średnie miesięczne)</label>
        </div>
        
        {selectedCountry.climate_description && (
          <div className="climate-type-box" style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#f7fafc', borderRadius: '12px', borderLeft: '4px solid #4299e1' }}>
            <strong style={{ fontSize: '0.75rem', color: '#718096', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>Typ klimatu:</strong>
            <span style={{ fontSize: '1rem', fontWeight: '600', color: '#2d3748' }}>{selectedCountry.climate_description}</span>
          </div>
        )}

        {selectedCountry.climate && selectedCountry.climate.length > 0 ? (
          <div className="combined-chart-container" onMouseLeave={() => setChartTooltip((prev: any) => ({ ...prev, visible: false }))}>
            <div className="chart-y-axis-label left">Temperatura (°C)</div>
            {hasRainfall && <div className="chart-y-axis-label right">Opady (mm)</div>}

            {chartTooltip.visible && (
              <div className="chart-custom-tooltip" style={{ left: chartTooltip.x, top: chartTooltip.y }}>
                {chartTooltip.text}
              </div>
            )}

            {(() => {
              const allTemps = selectedCountry.climate?.flatMap(c => [c.temp_day, c.temp_night]) || [];
              const minT = Math.min(...allTemps);
              const maxT = Math.max(...allTemps, 30);
              
              // Dynamic minimum: if always > 10, start at 0. Otherwise start at -10 or below.
              let yMin = 0;
              if (minT <= 10) {
                yMin = Math.floor(minT / 10) * 10 - 10;
              }
              
              const yMax = Math.ceil(maxT / 10) * 10 + 10;
              const yRange = yMax - yMin;
              
              const ticks = [];
              for (let t = yMin; t <= yMax; t += 10) ticks.push(t);
              
              const getY = (temp: number) => 200 - ((temp - yMin) / yRange) * 180;
              const getX = (i: number) => 62 + i * 43;
              const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);

              return (
                <svg viewBox="0 0 600 260" className="combined-svg-chart">
                  {/* Season Background Bands */}
                  {selectedCountry.climate?.map((cl, i) => {
                    const bandWidth = 43;
                    const xStart = 40.5 + i * bandWidth;
                    if (cl.season === 'wet' && hasRainfall) {
                      return <rect key={`bg-wet-${i}`} x={xStart} y={20} width={bandWidth} height={180} fill="#e6f6ff" opacity="0.8" />;
                    } else if (cl.season === 'dry') {
                      return <rect key={`bg-dry-${i}`} x={xStart} y={20} width={bandWidth} height={180} fill="#fff9eb" opacity="0.8" />;
                    }
                    return null;
                  })}

                  {ticks.map(temp => {
                    const y = getY(temp);
                    return (
                      <g key={temp}>
                        <line x1="40" y1={y} x2="560" y2={y} className={`chart-grid-line ${temp === 0 ? 'zero-line' : ''}`} />
                        <text x="35" y={y + 4} textAnchor="end" className="chart-axis-text temp">{temp}°</text>
                      </g>
                    );
                  })}

                  {hasRainfall && [0, 0.5, 1].map(p => (
                    <text key={p} x="565" y={200 - p * 180 + 4} textAnchor="start" className="chart-axis-text rain">
                      {Math.round(p * maxRain)}
                    </text>
                  ))}

                  {hasRainfall && selectedCountry.climate?.map((cl, i) => {
                    const barHeight = (cl.rain / maxRain) * 180;
                    return (
                      <rect
                        key={`rain-${i}`}
                        x={50 + i * 43}
                        y={200 - barHeight}
                        width="24"
                        height={barHeight}
                        className="chart-bar-rain"
                        style={{ fill: cl.season === 'wet' ? '#3182ce' : '#bee3f8' }}
                        onMouseEnter={(e) => setChartTooltip({
                          visible: true,
                          text: `${cl.rain} mm (${cl.season === 'wet' ? 'pora mokra' : cl.season === 'dry' ? 'pora sucha' : 'sezon przejściowy'})`,
                          x: e.nativeEvent.offsetX,
                          y: e.nativeEvent.offsetY - 30
                        })}
                        onMouseMove={(e) => setChartTooltip((prev: any) => ({
                          ...prev,
                          x: e.nativeEvent.offsetX,
                          y: e.nativeEvent.offsetY - 30
                        }))}
                      />
                    );
                  })}

                  {(() => {
                    const dayPath = selectedCountry.climate?.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_day)}`).join(' ') || '';
                    const nightPath = selectedCountry.climate?.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_night)}`).join(' ') || '';
                    return (
                      <>
                        <path d={dayPath} className="chart-line-day" fill="none" stroke="#f56565" strokeWidth="3" />
                        <path d={nightPath} className="chart-line-night" fill="none" stroke="#4299e1" strokeWidth="3" />
                        {selectedCountry.climate?.map((cl, i) => (
                          <g key={`dots-${i}`}>
                            <circle cx={getX(i)} cy={getY(cl.temp_day)} r="4" fill="#f56565" className="chart-dot-day"
                              onMouseEnter={(e) => setChartTooltip({ visible: true, text: `Dzień: ${cl.temp_day}°C`, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 })}
                              onMouseMove={(e) => setChartTooltip((prev: any) => ({ ...prev, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 }))}
                            />
                            <circle cx={getX(i)} cy={getY(cl.temp_night)} r="4" fill="#4299e1" className="chart-dot-night"
                              onMouseEnter={(e) => setChartTooltip({ visible: true, text: `Noc: ${cl.temp_night}°C`, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 })}
                              onMouseMove={(e) => setChartTooltip((prev: any) => ({ ...prev, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 }))}
                            />
                          </g>
                        ))}
                      </>
                    );
                  })()}

                  {selectedCountry.climate?.map((cl, i) => (
                    <text key={`label-${i}`} x={getX(i)} y="240" textAnchor="middle" className="chart-month-text">
                      {new Date(2024, cl.month - 1).toLocaleDateString('pl-PL', { month: 'narrow' })}
                    </text>
                  ))}
                </svg>
              );
            })()}

            <div className="chart-legend-combined">
              <div className="legend-item">
                <span className="legend-color-box" style={{ backgroundColor: '#f56565' }}></span>
                <span className="legend-label">Dzień</span>
              </div>
              <div className="legend-item">
                <span className="legend-color-box" style={{ backgroundColor: '#4299e1' }}></span>
                <span className="legend-label">Noc</span>
              </div>
              {hasRainfall && (
                <div className="legend-item">
                  <span className="legend-color-box" style={{ backgroundColor: '#bee3f8' }}></span>
                  <span className="legend-label">Opady</span>
                </div>
              )}
              <div className="legend-item">
                <span className="legend-color-box" style={{ backgroundColor: '#fff9eb', border: '1px solid #feebc8' }}></span>
                <span className="legend-label">Pora sucha</span>
              </div>
              {hasRainfall && (
                <div className="legend-item">
                  <span className="legend-color-box" style={{ backgroundColor: '#e6f6ff', border: '1px solid #bee3f8' }}></span>
                  <span className="legend-label">Pora mokra</span>
                </div>
              )}
            </div>

            {bestMonthsList && bestMonthsList.length > 0 && (
              <div className="best-travel-time-box">
                <span className="best-travel-icon">✈️</span>
                <div className="best-travel-content">
                  <strong>Najlepszy czas na wyjazd:</strong>
                  <p>{bestMonthsList.join(', ')}</p>
                  <small>W oparciu o statystycznie najniższe opady i przyjemną temperaturę.</small>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="no-data-text">Brak danych klimatycznych dla tego kraju.</p>
        )}
        <DataSource sources={['METEO', 'OWM']} lastUpdated={selectedCountry.weather?.last_updated} />
      </div>
    </>
  );
};
