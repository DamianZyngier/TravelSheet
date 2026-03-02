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
        {selectedCountry.climate && selectedCountry.climate.length > 0 ? (
          <div className="combined-chart-container" onMouseLeave={() => setChartTooltip((prev: any) => ({ ...prev, visible: false }))}>
            <div className="chart-y-axis-label left">Temperatura (°C)</div>
            <div className="chart-y-axis-label right">Opady (mm)</div>

            {chartTooltip.visible && (
              <div className="chart-custom-tooltip" style={{ left: chartTooltip.x, top: chartTooltip.y }}>
                {chartTooltip.text}
              </div>
            )}

            {(() => {
              // Calculate dynamic range for temperatures
              const allTemps = selectedCountry.climate?.flatMap(c => [c.temp_day, c.temp_night]) || [];
              const minT = Math.min(...allTemps, 0);
              const maxT = Math.max(...allTemps, 30);
              
              // Add margin and round to nearest 10
              const yMin = Math.floor(minT / 10) * 10 - 10;
              const yMax = Math.ceil(maxT / 10) * 10 + 10;
              const yRange = yMax - yMin;
              
              // Generate ticks
              const ticks = [];
              for (let t = yMin; t <= yMax; t += 10) ticks.push(t);
              
              const getY = (temp: number) => 200 - ((temp - yMin) / yRange) * 180;
              const getX = (i: number) => 62 + i * 43;
              
              const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);

              return (
                <svg viewBox="0 0 600 260" className="combined-svg-chart">
                  {/* Dynamic Grid lines & Y-Axis Labels */}
                  {ticks.map(temp => {
                    const y = getY(temp);
                    return (
                      <g key={temp}>
                        <line x1="40" y1={y} x2="560" y2={y} className={`chart-grid-line ${temp === 0 ? 'zero-line' : ''}`} />
                        <text x="35" y={y + 4} textAnchor="end" className="chart-axis-text temp">{temp}°</text>
                      </g>
                    );
                  })}

                  {/* Rain Y-axis labels */}
                  {[0, 0.5, 1].map(p => (
                    <text key={p} x="565" y={200 - p * 180 + 4} textAnchor="start" className="chart-axis-text rain">
                      {Math.round(p * maxRain)}
                    </text>
                  ))}

                  {/* Rainfall Bars */}
                  {selectedCountry.climate?.map((cl, i) => {
                    const barHeight = (cl.rain / maxRain) * 180;
                    return (
                      <rect
                        key={`rain-${i}`}
                        x={50 + i * 43}
                        y={200 - barHeight}
                        width="24"
                        height={barHeight}
                        className="chart-bar-rain"
                        onMouseEnter={(e) => setChartTooltip({
                          visible: true,
                          text: `${cl.rain} mm`,
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

                  {/* Temperature Lines */}
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

                  {/* Month Labels */}
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
                <span className="legend-label">Temperatura w dzień</span>
              </div>
              <div className="legend-item">
                <span className="legend-color-box" style={{ backgroundColor: '#4299e1' }}></span>
                <span className="legend-label">Temperatura w nocy</span>
              </div>
              <div className="legend-item">
                <span className="legend-color-box" style={{ backgroundColor: '#a0aec0', opacity: 0.3 }}></span>
                <span className="legend-label">Opady (mm)</span>
              </div>
            </div>
          </div>
        ) : (
          <p className="no-data-text">Brak danych klimatycznych dla tego kraju.</p>
        )}
        <DataSource sources={['METEO', 'OWM']} lastUpdated={selectedCountry.weather?.last_updated} />
      </div>
    </>
  );
};
