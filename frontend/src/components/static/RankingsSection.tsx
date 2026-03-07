import React from 'react';
import './RankingsSection.css';

interface RankingsSectionProps {
  onBack: () => void;
  onSelectCountry: (iso2: string) => void;
}

const RankingsSection: React.FC<RankingsSectionProps> = ({ onBack, onSelectCountry }) => {
  const airlineRanking = [
    { rank: 1, name: 'Qatar Airways', rating: 4.9, icon: '🇶🇦', desc: 'Najlepsza klasa biznes i obsługa na świecie.' },
    { rank: 2, name: 'Singapore Airlines', rating: 4.8, icon: '🇸🇬', desc: 'Legenda komfortu i punktualności.' },
    { rank: 3, name: 'Emirates', rating: 4.7, icon: '🇦🇪', desc: 'Rozrywka pokładowa i sieć połączeń z Polski.' },
    { rank: 4, name: 'ANA All Nippon Airways', rating: 4.7, icon: '🇯🇵', desc: 'Nieskazitelna czystość i japońska gościnność.' },
    { rank: 5, name: 'Turkish Airlines', rating: 4.6, icon: '🇹🇷', desc: 'Najlepszy catering i świetne przesiadki w Stambule.' },
    { rank: 6, name: 'Cathay Pacific', rating: 4.5, icon: '🇭🇰', desc: 'Doskonałe połączenia z Azją Wschodnią.' },
    { rank: 7, name: 'Air France', rating: 4.3, icon: '🇫🇷', desc: 'Europejski szyk i świetne wina na pokładzie.' },
    { rank: 8, name: 'Lufthansa', rating: 4.2, icon: '🇩🇪', desc: 'Solidny europejski wybór z dużą liczbą lotów z PL.' },
    { rank: 9, name: 'LOT Polish Airlines', rating: 4.1, icon: '🇵🇱', desc: 'Narodowy przewoźnik, brak przesiadek dla wielu tras.' },
    { rank: 10, name: 'Finnair', rating: 4.0, icon: '🇫🇮', desc: 'Najkrótsza droga do Azji przez Helsinki.' },
    { rank: 11, name: 'KLM', rating: 4.0, icon: '🇳🇱', desc: 'Najstarsza linia świata, świetna siatka przez Amsterdam.' },
    { rank: 12, name: 'Swiss', rating: 4.0, icon: '🇨🇭', desc: 'Szwajcarska precyzja i jakość.' },
    { rank: 13, name: 'Austrian Airlines', rating: 3.9, icon: '🇦🇹', desc: 'Gościnność i wiedeńska kawiarnia w chmurach.' },
    { rank: 14, name: 'British Airways', rating: 3.8, icon: '🇬🇧', desc: 'Klasyka lotnictwa z dużą siatką transatlantycką.' },
    { rank: 15, name: 'TAP Air Portugal', rating: 3.7, icon: '🇵🇹', desc: 'Brama do Ameryki Południowej i na Azory.' },
  ];

  const destinationRanking = [
    { rank: 1, name: 'Chorwacja', iso2: 'HR', category: 'Plaże i Autem', trend: 'stable', desc: 'Ulubiony wybór Polaków na wakacje własnym samochodem.' },
    { rank: 2, name: 'Grecja', iso2: 'GR', category: 'All Inclusive', trend: 'up', desc: 'Niezmiennie hit dzięki tysiącom wysp i świetnej pogodzie.' },
    { rank: 3, name: 'Włochy', iso2: 'IT', category: 'Jedzenie i Kultura', trend: 'up', desc: 'City breaki w Rzymie i Mediolanie to polski standard.' },
    { rank: 4, name: 'Turcja', iso2: 'TR', category: 'Rodzinne / Resorty', trend: 'stable', desc: 'Najlepszy stosunek jakości do ceny w segmencie resortów.' },
    { rank: 5, name: 'Hiszpania', iso2: 'ES', category: 'Słońce i Zabawa', trend: 'up', desc: 'Wyspy Kanaryjskie to ulubiony kierunek na polską zimę.' },
    { rank: 6, name: 'Albania', iso2: 'AL', category: 'Odkrycie Dekady', trend: 'up', desc: 'Tania i piękna alternatywa dla droższej reszty Europy.' },
    { rank: 7, name: 'Tajlandia', iso2: 'TH', category: 'Egzotyka', trend: 'up', desc: 'Pierwszy wybór Polaków na daleką podróż "na własną rękę".' },
    { rank: 8, name: 'Egipt', iso2: 'EG', category: 'Zima / Nurkowanie', trend: 'down', desc: 'Klasyka zimowego słońca i rafy koralowej.' },
    { rank: 9, name: 'Bułgaria', iso2: 'BG', category: 'Budżetowe Plaże', trend: 'stable', desc: 'Złote Piaski i Słoneczny Brzeg wciąż w czołówce.' },
    { rank: 10, name: 'Gruzja', iso2: 'GE', category: 'Góry i Wino', trend: 'up', desc: 'Gościnność, krajobrazy i fantastyczne jedzenie.' },
    { rank: 11, name: 'Portugalia', iso2: 'PT', category: 'Ocean i Surfing', trend: 'up', desc: 'Algarve i Lizbona przyciągają coraz więcej osób.' },
    { rank: 12, name: 'Czarnogóra', iso2: 'ME', category: 'Bałkański Klimat', trend: 'up', desc: 'Zatoka Kotorska i piękne góry tuż obok morza.' },
    { rank: 13, name: 'Cypr', iso2: 'CY', category: 'Wyspa Słońca', trend: 'stable', desc: 'Świetne miejsce na jesienne i wiosenne wycieczki.' },
    { rank: 14, name: 'Wietnam', iso2: 'VN', category: 'Przygoda w Azji', trend: 'up', desc: 'Dynamicznie rosnący kierunek egzotyczny.' },
    { rank: 15, name: 'Zjedn. Emiraty Arabskie', iso2: 'AE', category: 'Nowoczesność', trend: 'stable', desc: 'Dubaj to synonim luksusu i zimowego słońca.' },
  ];

  return (
    <div className="rankings-container">
      <div className="rankings-header">
        <button className="rankings-back-btn" onClick={onBack}>← Powrót</button>
        <h1>🏆 Rankingi Podróżnicze 2024</h1>
        <p className="rankings-subtitle">Trendy i oceny oparte na wyborach polskich podróżnych.</p>
      </div>

      <div className="rankings-grid">
        {/* Airline Rankings */}
        <section className="ranking-card">
          <div className="ranking-card-header">
            <span className="ranking-icon">✈️</span>
            <h2>Najlepsze Linie Lotnicze</h2>
          </div>
          <div className="ranking-scroll-area">
            <div className="ranking-list">
              {airlineRanking.map((item) => (
                <div key={item.rank} className="ranking-item">
                  <div className="rank-number">#{item.rank}</div>
                  <div className="rank-content">
                    <div className="rank-title-row">
                      <span className="rank-item-name">{item.icon} {item.name}</span>
                      <span className="rank-rating">⭐ {item.rating}</span>
                    </div>
                    <p className="rank-desc">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Destination Rankings */}
        <section className="ranking-card">
          <div className="ranking-card-header">
            <span className="ranking-icon">🌍</span>
            <h2>Top Kierunki z Polski</h2>
          </div>
          <div className="ranking-scroll-area">
            <div className="ranking-list">
              {destinationRanking.map((item) => (
                <div 
                  key={item.rank} 
                  className="ranking-item clickable"
                  onClick={() => onSelectCountry(item.iso2)}
                  title={`Kliknij, aby zobaczyć szczegóły dla: ${item.name}`}
                >
                  <div className="rank-number">#{item.rank}</div>
                  <div className="rank-content">
                    <div className="rank-title-row">
                      <span className="rank-item-name">{item.name}</span>
                      <span className={`rank-trend ${item.trend}`}>
                        {item.trend === 'up' ? '📈' : item.trend === 'down' ? '📉' : '➖'}
                      </span>
                    </div>
                    <div className="rank-category">{item.category}</div>
                    <p className="rank-desc">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <div className="rankings-footer">
        <p>* Rankingi są aktualizowane co kwartał na podstawie trendów rynkowych.</p>
      </div>
    </div>
  );
};

export default RankingsSection;
