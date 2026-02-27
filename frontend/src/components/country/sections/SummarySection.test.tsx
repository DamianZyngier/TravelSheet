import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SummarySection } from './SummarySection';
import { CountryData } from '../../../types';

const mockCountry: CountryData = {
  iso2: 'PL',
  name_pl: 'Polska',
  wiki_summary: 'Piękny kraj w Europie.',
  national_symbols: 'Orzeł Biały',
  parent: null,
  territories: []
} as any;

describe('SummarySection Component', () => {
  it('renders summary and national symbols', () => {
    render(
      <SummarySection 
        selectedCountry={mockCountry} 
        onSelectCountry={() => {}} 
        allCountries={[]} 
      />
    );
    
    expect(screen.getByText(/Piękny kraj w Europie/i)).toBeInTheDocument();
    expect(screen.getByText(/Orzeł Biały/i)).toBeInTheDocument();
  });

  it('renders territory links when present', () => {
    const countryWithTerritory = {
      ...mockCountry,
      territories: [{ iso2: 'MQ', name_pl: 'Martynika' }]
    } as any;

    render(
      <SummarySection 
        selectedCountry={countryWithTerritory} 
        onSelectCountry={() => {}} 
        allCountries={[]} 
      />
    );

    expect(screen.getByText(/Terytoria zależne/i)).toBeInTheDocument();
    expect(screen.getByText(/Martynika/i)).toBeInTheDocument();
  });
});
