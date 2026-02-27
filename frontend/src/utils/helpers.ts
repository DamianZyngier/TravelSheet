import type { CountryData } from '../types';

export const formatPLN = (val: number) => {
  return new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(val);
};

export const getCurrencyExample = (country: CountryData) => {
  if (!country.currency.rate_pln) return '';
  const price = 10 / country.currency.rate_pln;
  return `Przykład: 10 PLN ≈ ${price.toFixed(2)} ${country.currency.code}`;
};

export const checkPlugs = (plugs: string) => {
  if (!plugs) return { text: 'Brak danych', warning: false, class: 'plugs-err' };
  const hasC = plugs.includes('C');
  const hasE = plugs.includes('E');
  if (hasC && hasE) return { text: '🔌 Standard taki sam jak w Polsce (Typ C/E)', warning: false, class: 'plugs-ok' };
  if (hasC || hasE) return { text: '🔌 Częściowo kompatybilne (Typ C lub E)', warning: true, class: 'plugs-warn' };
  return { text: '🔌 Inne gniazdka - weź przejściówkę!', warning: true, class: 'plugs-err' };
};

export const getEnlargedPlugUrl = (url: string) => {
  if (!url) return '';
  return url.replace('100x100', '250x250');
};

export const getMapSettings = (country: CountryData) => {
  const area = Number(country.area) || 0;
  if (area > 8000000) return { zoom: 1.2, showDot: false }; // Rosja, Kanada, USA, Chiny
  if (area > 2000000) return { zoom: 2.5, showDot: false }; // Australia, Indie
  if (area > 500000) return { zoom: 5, showDot: false };   // Francja, Hiszpania
  if (area > 100000) return { zoom: 8, showDot: false };   // Polska, Grecja
  if (area > 10000) return { zoom: 15, showDot: true };    // Izrael, Albania
  return { zoom: 25, showDot: true };                     // Malta, Singapur
};

export const getLongNameClass = (name: string, type: 'h3' | 'h2') => {
  if (type === 'h3') {
    if (name.length > 25) return 'font-very-small';
    if (name.length > 18) return 'font-small';
  } else {
    if (name.length > 30) return 'font-very-small';
    if (name.length > 20) return 'font-small';
  }
  return '';
};
