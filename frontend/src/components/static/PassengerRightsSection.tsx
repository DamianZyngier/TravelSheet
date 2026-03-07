import React, { useEffect } from 'react';

interface PassengerRightsSectionProps {
  onBack: () => void;
}

const PassengerRightsSection: React.FC<PassengerRightsSectionProps> = ({ onBack }) => {
  useEffect(() => {
    // Load Twitter widgets
    const script = document.createElement("script");
    script.src = "https://platform.twitter.com/widgets.js";
    script.async = true;
    document.body.appendChild(script);
    
    return () => {
      // We don't necessarily need to remove it
    };
  }, []);

  return (
    <div className="static-page-container passenger-rights-page">
      <div className="static-page-header no-print">
        <button className="side-back-button" onClick={onBack}>
          ← Powrót do strony głównej
        </button>
      </div>

      <div className="static-page-content printable-area">
        <div className="static-page-title-section">
          <h1>Twoje prawa w podróży lotniczej</h1>
          <p className="static-page-desc">
            Jako pasażer linii lotniczych w Unii Europejskiej masz określone prawa w przypadku zakłóceń lotu. 
            Przepisy te (Rozporządzenie WE 261/2004) obowiązują, jeśli Twój lot odbywa się wewnątrz UE, 
            zaczyna się w UE lub kończy w UE (w przypadku linii z kraju UE).
          </p>
        </div>

        <div className="rights-grid">
          <div className="right-card">
            <div className="right-card-icon">🕒</div>
            <h3>Lot jest opóźniony</h3>
            <div className="right-card-content">
              <p><strong>Opóźnienie powyżej 2 godzin:</strong> Masz prawo do opieki (posiłki, napoje, 2 rozmowy telefoniczne/e-maile).</p>
              <p><strong>Opóźnienie powyżej 3 godzin:</strong> Masz prawo do odszkodowania (od 250 € do 600 €), chyba że wystąpiły "nadzwyczajne okoliczności".</p>
              <p><strong>Opóźnienie powyżej 5 godzin:</strong> Masz prawo do zwrotu kosztów biletu, jeśli zrezygnujesz z podróży.</p>
            </div>
          </div>

          <div className="right-card">
            <div className="right-card-icon">❌</div>
            <h3>Lot jest odwołany</h3>
            <div className="right-card-content">
              <p><strong>Opcje:</strong> Linia musi zaoferować zwrot kosztów biletu lub zmianę planu podróży do miejsca docelowego.</p>
              <p><strong>Opieka:</strong> Jeśli czekasz na nowy lot, przysługuje Ci wyżywienie i nocleg (jeśli konieczny).</p>
              <p><strong>Odszkodowanie:</strong> Przysługuje Ci odszkodowanie, chyba że powiadomiono Cię co najmniej 14 dni wcześniej.</p>
            </div>
          </div>

          <div className="right-card">
            <div className="right-card-icon">✋</div>
            <h3>Odmowa wejścia na pokład</h3>
            <div className="right-card-content">
              <p><strong>Overbooking:</strong> Jeśli linia odmówi Ci wejścia na pokład wbrew Twojej woli, masz prawo do natychmiastowego odszkodowania.</p>
              <p><strong>Wybór:</strong> Możesz wybrać zwrot kosztów biletu lub alternatywne połączenie.</p>
              <p><strong>Opieka:</strong> Przysługuje Ci pełna opieka w oczekiwaniu na lot zastępczy.</p>
            </div>
          </div>

          <div className="right-card">
            <div className="right-card-icon">🧳</div>
            <h3>Problem z bagażem</h3>
            <div className="right-card-content">
              <p><strong>Uszkodzony bagaż:</strong> Masz 7 dni na złożenie pisemnej reklamacji (PIR) od momentu odebrania bagażu.</p>
              <p><strong>Opóźniony bagaż:</strong> Masz 21 dni na reklamację. Możesz ubiegać się o zwrot kosztów za niezbędne zakupy.</p>
              <p><strong>Zgubiony bagaż:</strong> Jeśli nie odnajdzie się w ciągu 21 dni, uznaje się go za zagubiony (przysługuje odszkodowanie do ok. 1600 €).</p>
            </div>
          </div>
        </div>

        <section className="useful-links">
          <h3>Więcej informacji i pomoc</h3>
          <div className="links-container">
            <a href="https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_pl.htm" target="_blank" rel="noopener noreferrer" className="useful-link-item">
              <span>🇪🇺</span> Twoja Europa - Prawa pasażera (Oficjalna strona UE)
            </a>
            <a href="https://www.ulc.gov.pl/pl/prawa-pasazera" target="_blank" rel="noopener noreferrer" className="useful-link-item">
              <span>🇵🇱</span> Urząd Lotnictwa Cywilnego (Polska)
            </a>
            <a href="https://pasazer.ulc.gov.pl/" target="_blank" rel="noopener noreferrer" className="useful-link-item">
              <span>📋</span> Rzecznik Praw Pasażera
            </a>
          </div>
        </section>

        <section className="twitter-widget-section">
          <h3>Aktualności od @PolakZaGranica</h3>
          <div className="twitter-embed-container">
            <a 
              className="twitter-timeline" 
              data-height="600" 
              data-theme="light" 
              href="https://twitter.com/PolakZaGranica?ref_src=twsrc%5Etfw"
            >
              Tweets by PolakZaGranica
            </a>
          </div>
        </section>
      </div>
    </div>
  );
};

export default PassengerRightsSection;
