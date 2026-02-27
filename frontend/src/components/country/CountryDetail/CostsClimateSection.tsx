import React from 'react';
import type { CountryData } from '../../../types';
import { DataSource } from '../../Common';

interface CostsClimateSectionProps {
  selectedCountry: CountryData;
  chartTooltip: { visible: boolean; x: number; y: number; text: string };
  setChartTooltip: (tooltip: any) => void;
}

const CostsClimateSection: React.FC<CostsClimateSectionProps> = ({ 
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
              <p className="costs-disclaimer">* Wartości przybliżone w oparciu o koszty w Polsce (100%)</p>
            </>
          ) : (
            <div className="costs-no-data-placeholder">
              <span className="no-data-icon">📉</span>
              <p>Brak dostępnych danych statystycznych o kosztach życia dla tego kraju.</p>
            </div>
          )}
        </div>
        <DataSource sources={['NUMBEO']} />
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

            <svg viewBox="0 0 600 260" className="combined-svg-chart">
              {/* Grid lines & Y-Axis Labels */}
              {[-20, -10, 0, 10, 20, 30, 40].map(temp => {
                const y = 200 - (temp + 20) * 3.5;
                return (
                  <g key={temp}>
                    <line x1="40" y1={y} x2="560" y2={y} className={`chart-grid-line ${temp === 0 ? 'zero-line' : ''}`} />
                    <text x="35" y={y + 4} textAnchor="end" className="chart-axis-text temp">{temp}°</text>
                  </g>
                );
              })}

              {(() => {
                const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);
                return [0, 0.5, 1].map(p => (
                  <text key={p} x="565" y={200 - p * 180 + 4} textAnchor="start" className="chart-axis-text rain">
                    {Math.round(p * maxRain)}
                  </text>
                ));
              })()}

              {selectedCountry.climate?.map((cl, i) => {
                const maxRain = Math.max(...(selectedCountry.climate?.map(c => c.rain) || [100]), 1);
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

              {(() => {
                const getX = (i: number) => 62 + i * 43;
                const getY = (temp: number) => 200 - (temp + 20) * 3.5;
                const dayPath = selectedCountry.climate?.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_day)}`).join(' ') || '';
                const nightPath = selectedCountry.climate?.map((cl, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(cl.temp_night)}`).join(' ') || '';
                return (
                  <>
                    <path d={dayPath} className="chart-line-day" fill="none" />
                    <path d={nightPath} className="chart-line-night" fill="none" />
                    {selectedCountry.climate?.map((cl, i) => (
                      <g key={`dots-${i}`}>
                        <circle cx={getX(i)} cy={getY(cl.temp_day)} r="4" className="chart-dot-day"
                          onMouseEnter={(e) => setChartTooltip({ visible: true, text: `Dzień: ${cl.temp_day}°C`, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 })}
                          onMouseMove={(e) => setChartTooltip((prev: any) => ({ ...prev, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 }))}
                        />
                        <circle cx={getX(i)} cy={getY(cl.temp_night)} r="4" className="chart-dot-night"
                          onMouseEnter={(e) => setChartTooltip({ visible: true, text: `Noc: ${cl.temp_night}°C`, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 })}
                          onMouseMove={(e) => setChartTooltip((prev: any) => ({ ...prev, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY - 30 }))}
                        />
                      </g>
                    ))}
                  </>
                );
              })()}

              {selectedCountry.climate?.map((cl, i) => (
                <text key={`label-${i}`} x={62 + i * 43} y="240" textAnchor="middle" className="chart-month-text">
                  {new Date(2024, cl.month - 1).toLocaleDateString('pl-PL', { month: 'narrow' })}
                </text>
              ))}
            </svg>

            <div className="chart-legend-combined">
              <span className="legend-item"><i className="legend-line day"></i> Dzień</span>
              <span className="legend-item"><i className="legend-line night"></i> Noc</span>
              <span className="legend-item"><i className="legend-rect rain"></i> Opady (mm)</span>
            </div>
          </div>
        ) : (
          <p className="no-data-text">Brak danych klimatycznych dla tego kraju.</p>
        )}
        <DataSource sources={['METEO', 'OWM']} />
      </div>
    </>
  );
};

export default CostsClimateSection;
