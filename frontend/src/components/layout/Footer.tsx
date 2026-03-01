import React from 'react';

interface FooterProps {
  onOpenTerms: () => void;
  onOpenLicense: () => void;
}

const Footer: React.FC<FooterProps> = ({ onOpenTerms, onOpenLicense }) => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="main-footer">
      <div className="footer-content">
        <div className="footer-copyright">
          &copy; {currentYear} TripSheet. Wszystkie prawa zastrzeżone.
        </div>
        <div className="footer-redistribution-notice">
          Kopiowanie i rozpowszechnianie danych bez zgody autora jest zabronione.
        </div>
        <div className="footer-links">
          <button onClick={onOpenTerms} className="footer-link-btn">Regulamin</button>
          <span className="footer-sep">|</span>
          <button onClick={onOpenLicense} className="footer-link-btn">Licencja</button>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
