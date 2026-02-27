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
  it('renders territory relationship links correctly', () => {
    const onSelect = vi.fn();
    render(
      <Sidebar 
        selectedCountry={mockCountry} 
        sortedFullList={mockList} 
        onSelectCountry={onSelect}
        activeSection="summary"
        scrollToSection={() => {}}
        navigateCountry={() => {}}
      />
    );

    expect(screen.getByText(/Terytorium państwa/i)).toBeInTheDocument();
    // Use container query or specific class to find the button
    const parentBtn = document.querySelector('.relationship-link-btn') as HTMLElement;
    fireEvent.click(parentBtn);
    expect(onSelect).toHaveBeenCalledWith(mockFrance);
  });

  it('renders child territories for parent countries', () => {
    render(
      <Sidebar 
        selectedCountry={mockFrance} 
        sortedFullList={mockList} 
        onSelectCountry={() => {}}
        activeSection="summary"
        scrollToSection={() => {}}
        navigateCountry={() => {}}
      />
    );

    expect(screen.getByText(/Terytoria zależne/i)).toBeInTheDocument();
    const territoryBtn = document.querySelector('.territory-mini-link') as HTMLElement;
    expect(territoryBtn).toBeInTheDocument();
    expect(territoryBtn.textContent).toContain('Martynika');
  });
});
