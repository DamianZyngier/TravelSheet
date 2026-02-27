import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Sidebar from './Sidebar';
import { CountryData } from '../../types';

const mockCountry: CountryData = {
  iso2: 'MQ',
  name_pl: 'Martynika',
  flag_url: 'mq.png',
  parent: { iso2: 'FR', name_pl: 'Francja' },
  territories: [],
  safety: { risk_level: 'low' },
} as any;

const mockFrance: CountryData = {
  iso2: 'FR',
  name_pl: 'Francja',
  flag_url: 'fr.png',
  territories: [{ iso2: 'MQ', name_pl: 'Martynika' }],
} as any;

const mockList = [mockFrance, mockCountry];

describe('Sidebar Component', () => {
  it('renders country navigation links', () => {
    render(
      <Sidebar 
        selectedCountry={mockCountry} 
        sortedFullList={mockList} 
        onSelectCountry={() => {}}
        activeSection="summary"
        scrollToSection={() => {}}
        navigateCountry={() => {}}
      />
    );

    expect(screen.getByText(/Przeglądasz/i)).toBeInTheDocument();
    expect(screen.getByText(/Martynika/i)).toBeInTheDocument();
  });
});
