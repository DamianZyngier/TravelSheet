import React, { useState, useEffect } from 'react';
import type { CountryData } from '../../types';
import { SECTIONS } from '../../constants';
import { getLongNameClass } from '../../utils/helpers';

interface SidebarProps {
  selectedCountry: CountryData;
  sortedFullList: CountryData[];
  onSelectCountry: (country: CountryData | null) => void;
  activeSection: string;
  scrollToSection: (id: string) => void;
  navigateCountry: (direction: 'prev' | 'next') => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  selectedCountry,
  sortedFullList,
  onSelectCountry,
  activeSection,
  scrollToSection,
  navigateCountry
}) => {
  const currentIndex = sortedFullList.findIndex(c => c.iso2 === selectedCountry.iso2);
  const prevCountry = currentIndex > 0 ? sortedFullList[currentIndex - 1] : sortedFullList[sortedFullList.length - 1];
  const nextCountry = currentIndex < sortedFullList.length - 1 ? sortedFullList[currentIndex + 1] : sortedFullList[0];

  // Define the main categories and their IDs
  const CATEGORIES = [
    { id: 'summary', label: 'Podsumowanie i Mapa', icon: '📍', items: 'Opis, Flaga, Położenie' },
    { id: 'category-1', label: '1. Przygotowanie i Formalności', icon: '📋', items: 'Dokumenty, Waluta, Ambasady' },
    { id: 'category-2', label: '2. Zdrowie i Bezpieczeństwo', icon: '🛡️', items: 'Zdrowie, Bezpieczeństwo, Woda' },
    { id: 'category-3', label: '3. Informacje Praktyczne', icon: '⚡', items: 'Pogoda, Gniazdka, Telefony, Ceny' },
    { id: 'category-4', label: '4. Warunki Środowiskowe', icon: '🌤️', items: 'Klimat, Święta' },
    { id: 'category-5', label: '5. Kultura i Atrakcje', icon: '🏛️', items: 'Info, Prawo, UNESCO' },
  ];

  // Map individual section IDs to category IDs for active state highlighting
  const sectionToCategoryMap: Record<string, string> = SECTIONS.reduce((acc, s) => {
    if (s.id === 'summary') acc[s.id] = 'summary';
    else if (s.category?.includes('1.')) acc[s.id] = 'category-1';
    else if (s.category?.includes('2.')) acc[s.id] = 'category-2';
    else if (s.category?.includes('3.')) acc[s.id] = 'category-3';
    else if (s.category?.includes('4.')) acc[s.id] = 'category-4';
    else if (s.category?.includes('5.')) acc[s.id] = 'category-5';
    return acc;
  }, {} as Record<string, string>);

  const activeCategoryId = sectionToCategoryMap[activeSection] || 'summary';

  return (
    <aside className="side-menu no-print">
      <button className="side-back-button" onClick={() => onSelectCountry(null)}>
        ← Powrót do listy
      </button>

      <div className="current-country-nav-box">
        <img src={selectedCountry.flag_url} alt="" className="current-nav-flag" />
        <div className="current-nav-info">
          <span className="current-nav-label">Przeglądasz:</span>
          <h3 className={`current-nav-name ${getLongNameClass(selectedCountry.name_pl, 'h3')}`}>
            {selectedCountry.name_pl}
          </h3>
        </div>
      </div>

      <div className="country-navigation">
        <button className="nav-button prev" onClick={() => navigateCountry('prev')}>
          <img src={prevCountry?.flag_url} alt="" className="nav-flag" />
          <div className="nav-info">
            <span className="nav-label">Poprzedni</span>
            <span className={`nav-name ${getLongNameClass(prevCountry?.name_pl || '', 'h3')}`}>{prevCountry?.name_pl}</span>
          </div>
          <span className="nav-arrow">←</span>
        </button>
        <button className="nav-button next" onClick={() => navigateCountry('next')}>
          <span className="nav-arrow">→</span>
          <div className="nav-info">
            <span className="nav-label">Następny</span>
            <span className={`nav-name ${getLongNameClass(nextCountry?.name_pl || '', 'h3')}`}>{nextCountry?.name_pl}</span>
          </div>
          <img src={nextCountry?.flag_url} alt="" className="nav-flag" />
        </button>
      </div>

      <div className="side-menu-list simplified">
        {CATEGORIES.map(cat => (
          <button 
            key={cat.id}
            className={`side-menu-category-item ${activeCategoryId === cat.id ? 'active' : ''}`}
            onClick={() => scrollToSection(cat.id)}
          >
            <div className="category-item-main">
              <span className="category-item-icon">{cat.icon}</span>
              <span className="category-item-label">{cat.label}</span>
            </div>
            <div className="category-item-subtext">{cat.items}</div>
          </button>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
