import React from 'react';

interface LegalModalProps {
  title: string;
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const LegalModal: React.FC<LegalModalProps> = ({ title, isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="legal-modal-overlay" onClick={onClose}>
      <div className="legal-modal-content" onClick={e => e.stopPropagation()}>
        <div className="legal-modal-header">
          <h2>{title}</h2>
          <button className="close-modal-btn" onClick={onClose}>&times;</button>
        </div>
        <div className="legal-modal-body">
          {children}
        </div>
        <div className="legal-modal-footer">
          <button className="primary-btn" onClick={onClose}>Zamknij</button>
        </div>
      </div>
    </div>
  );
};

export default LegalModal;
