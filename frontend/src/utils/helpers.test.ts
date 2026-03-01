import { describe, it, expect } from 'vitest';
import { formatPLN, checkPlugs, getMapSettings, getLongNameClass } from './helpers';
import type { CountryData } from '../types';

describe('Helpers Unit Tests', () => {
  it('formatPLN should format numbers correctly', () => {
    const result = formatPLN(1234.56);
    expect(result).toContain('1');
    expect(result).toContain('234');
    expect(result).toContain('56');
    expect(result).toContain('zł');
  });

  it('checkPlugs should detect Polish compatibility', () => {
    expect(checkPlugs('C, E').text).toContain('Standard taki sam');
    expect(checkPlugs('C, G').text).toContain('Częściowo kompatybilne');
    expect(checkPlugs('G').text).toContain('Inne gniazdka');
    expect(checkPlugs('').text).toBe('Brak danych');
  });

  it('getMapSettings should return appropriate zoom for area', () => {
    const bigCountry = { area: 10000000 } as CountryData;
    const smallCountry = { area: 500 } as CountryData;
    
    expect(getMapSettings(bigCountry).zoom).toBe(1.2);
    expect(getMapSettings(smallCountry).zoom).toBe(35);
    expect(getMapSettings(smallCountry).showDot).toBe(true);
  });

  it('getLongNameClass should return correct font class', () => {
    expect(getLongNameClass('Polska', 'h3')).toBe('');
    expect(getLongNameClass('Zjednoczone Emiraty Arabskie', 'h3')).toBe('font-very-small');
    expect(getLongNameClass('Demokratyczna Republika Konga', 'h2')).toBe('font-small');
  });
});
