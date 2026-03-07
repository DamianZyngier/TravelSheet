import React from 'react';
import './RankingsSection.css';

interface RankingsSectionProps {
  onBack: () => void;
}

const RankingsSection: React.FC<RankingsSectionProps> = ({ onBack }) => {
  const airlineRanking = [
    { rank: 1, name: 'Qatar Airways', rating: 4.9, icon: '🇶🇦', desc: 'Najlepsza klasa biznes i obsługa na świecie.' },
    { rank: 2, name: 'Singapore Airlines', rating: 4.8, icon: '🇸🇬', desc: 'Legenda komfortu i punktualności.' },
    { rank: 3, name: 'Emirates', rating: 4.7, icon: '🇦🇪', desc: 'Rozrywka pokładowa i sieć połączeń z Polski.' },
    { rank: 4, name: 'ANA All Nippon Airways', rating: 4.7, icon: '🇯🇵', desc: 'Nieskazitelna czystość i japońska gościnność.' },
    { rank: 5, name: 'Turkish Airlines', rating: 4.6, icon: '🇹🇷', desc: 'Najlepszy catering i świetne przesiadki w Stambule.' },
    { rank: 6, name: 'Lufthansa', rating: 4.2, icon: '🇩🇪', desc: 'Solidny europejski wybór z dużą liczbą lotów z PL.' },
    { rank: 7, name: 'LOT Polish Airlines', rating: 4.1, icon: '🇵🇱', desc: 'Narodowy przewoźnik, brak przesiadek dla wielu tras.' },
    { rank: 8, name: 'Finnair', rating: 4.0, icon: '🇫🇮', desc: 'Najkrótsza droga do Azji przez Helsinki.' },
  ];

  const destinationRanking = [
    { rank: 1, name: 'Chorwacja', category: 'Plaże i Autem', trend: 'stable', desc: 'Ulubiony wybór Polaków na wakacje własnym samochodem.' },
    { rank: 2, name: 'Grecja', category: 'All Inclusive', trend: 'up', desc: 'Niezmiennie hit dzięki tysiącom wysp i świetnej pogodzie.' },
    { rank: 3, name: 'Włochy', category: 'Jedzenie i Kultura', trend: 'up', desc: 'City breaki w Rzymie i Mediolanie to polski standard.' },
    { rank: 4, name: 'Turcja', category: 'Rodzinne / Resorty', trend: 'stable', desc: 'Najlepszy stosunek jakości do ceny w segmencie resortów.' },
    { rank: 5, name: 'Hiszpania', category: 'Słońce i Zabawa', trend: 'up', desc: 'Wyspy Kanaryjskie to ulubiony kierunek na polską zimę.' },
    { rank: 6, name: 'Albania', category: 'Odkrycie Dekady', trend: 'up', desc: 'Tania i piękna alternatywa dla droższej reszty Europy.' },
    { rank: 7, name: 'Tajlandia', category: 'Egzotyka', trend: 'up', desc: 'Pierwszy wybór Polaków na daleką podróż "na własną rękę".' },
    { rank: 8, name: 'Egipt', category: 'Zima / Nurkowanie', trend: 'down', desc: 'Klasyka zimowego słońca i rafy koralowej.' },
  ];

  return (
    <div className="rankings-container">
      <div className="rankings-header">
        <button className="rankings-back-btn" onClick={onBack}>← Powrót</button>
        <h1>🏆 Rankingi Podróżnicze 2024</h1>
        <p className="rankings-subtitle">Zestawienia oparte na popularności wśród podróżnych z Polski oraz ocenach ekspertów.</p>
      </div>

      <div className="rankings-grid">
        {/* Airline Rankings */}
        <section className="ranking-card">
          <div className="ranking-card-header">
            <span className="ranking-icon">✈️</span>
            <h2>Najlepsze Linie Lotnicze</h2>
          </div>
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
        </section>

        {/* Destination Rankings */}
        <section className="ranking-card">
          <div className="ranking-card-header">
            <span className="ranking-icon">🌍</span>
            <h2>Top Kierunki z Polski</h2>
          </div>
          <div className="ranking-list">
            {destinationRanking.map((item) => (
              <div key={item.rank} className="ranking-item">
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
        </section>
      </div>

      <div className="rankings-footer">
        <p>* Dane statystyczne zbierane z okresu ostatniego roku. Ranking jest subiektywnym zestawieniem ułatwiającym wybór.</p>
      </div>
    </div>
  );
};

export default RankingsSection;
