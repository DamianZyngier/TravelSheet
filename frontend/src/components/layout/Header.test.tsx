import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Header from './Header';

describe('Header Component', () => {
  const mockProps = {
    searchQuery: '',
    setSearchQuery: vi.fn(),
    filterContinent: 'all',
    setFilterContinent: vi.fn(),
    filterSafety: 'all',
    setFilterSafety: vi.fn(),
    continents: ['Europe', 'Asia'],
    onLogoClick: vi.fn(),
    searchInputRef: { current: null } as any
  };

  it('renders title and logo', () => {
    render(<Header {...mockProps} />);
    expect(screen.getByText(/TripSheet/i)).toBeInTheDocument();
    expect(screen.getByText(/Twoje centrum bezpiecznych podróży/i)).toBeInTheDocument();
  });

  it('updates search query on input', () => {
    render(<Header {...mockProps} />);
    const input = screen.getByPlaceholderText(/Szukaj kraju/i);
    fireEvent.change(input, { target: { value: 'Polska' } });
    expect(mockProps.setSearchQuery).toHaveBeenCalledWith('Polska');
  });

  it('calls onLogoClick when logo section is clicked', () => {
    render(<Header {...mockProps} />);
    const logoSection = screen.getByText(/TripSheet/i).closest('.logo-section');
    fireEvent.click(logoSection!);
    expect(mockProps.onLogoClick).toHaveBeenCalled();
  });
});
