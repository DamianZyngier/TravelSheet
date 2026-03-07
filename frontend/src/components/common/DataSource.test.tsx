import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DataSource } from './DataSource';

describe('DataSource Component', () => {
  it('renders valid sources correctly', () => {
    render(<DataSource sources={['MSZ', 'WIKI']} />);
    expect(screen.getByText('Źródło:')).toBeDefined();
    expect(screen.getByText('MSZ (gov.pl)')).toBeDefined();
    expect(screen.getByText('Wikipedia / Wikidata')).toBeDefined();
  });

  it('gracefully handles missing or invalid sources', () => {
    // @ts-ignore - testing runtime safety for invalid keys
    render(<DataSource sources={['INVALID_KEY', 'WIKI']} />);
    expect(screen.getByText('Źródło:')).toBeDefined();
    expect(screen.getByText('Wikipedia / Wikidata')).toBeDefined();
    expect(screen.queryByText('INVALID_KEY')).toBeNull();
  });

  it('renders last updated date when provided', () => {
    const date = '2026-03-06T12:00:00Z';
    render(<DataSource sources={[]} lastUpdated={date} />);
    expect(screen.getByText(/Aktualizacja:/)).toBeDefined();
  });

  it('returns null when no valid sources and no date', () => {
    // @ts-ignore
    const { container } = render(<DataSource sources={['INVALID']} />);
    expect(container.firstChild).toBeNull();
  });
});
