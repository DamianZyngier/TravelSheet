import React, { useState, useEffect } from 'react';
import { CHECKLISTS } from '../../constants/checklists';

interface ChecklistSectionProps {
  variantId: string;
  onBack: () => void;
  onVariantChange: (variant: string) => void;
}

const ChecklistSection: React.FC<ChecklistSectionProps> = ({ variantId, onBack, onVariantChange }) => {
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>(() => {
    const saved = localStorage.getItem('travelsheet_checklists');
    return saved ? JSON.parse(saved) : {};
  });

  // Local state for the dropdown/tab selection should be synced with prop
  const activeVariant = variantId;

  useEffect(() => {
    localStorage.setItem('travelsheet_checklists', JSON.stringify(checkedItems));
  }, [checkedItems]);

  const toggleItem = (id: string) => {
    setCheckedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handlePrint = () => {
    window.print();
  };

  const handleBackClick = (e: React.MouseEvent) => {
    if (e.button === 1 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    onBack();
  };

  const handleVariantClick = (e: React.MouseEvent, vId: string) => {
    if (e.button === 1 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    onVariantChange(vId);
  };

  const currentChecklist = CHECKLISTS.find(c => c.id === activeVariant) || CHECKLISTS[0];

  return (
    <div className="static-page-container checklist-page">
      <div className="static-page-header no-print">
        <a href="./" className="side-back-button" onClick={handleBackClick} style={{ textDecoration: 'none' }}>
          ← Powrót do strony głównej
        </a>
        <div className="checklist-controls">
          <div className="variant-tabs">
            <div 
              className="variant-slider" 
              style={{ 
                transform: `translateX(${
                  activeVariant === 'minimum' ? '0' : 
                  activeVariant === 'optimal' ? '100%' : '200%'
                })` 
              }}
            ></div>
            {CHECKLISTS.map(v => (
              <a
                key={v.id}
                href={`?checklist=${v.id}`}
                className={`variant-tab ${activeVariant === v.id ? 'active' : ''}`}
                onClick={(e) => handleVariantClick(e, v.id)}
                style={{ textDecoration: 'none' }}
              >
                {v.id.toUpperCase()}
              </a>
            ))}
          </div>
          <button className="primary-btn print-btn" onClick={handlePrint}>
            🖨️ Drukuj / PDF
          </button>
        </div>
      </div>

      <div className="static-page-content printable-area">
        <div className="static-page-title-section">
          <h1>{currentChecklist.title}</h1>
          <p className="static-page-desc">{currentChecklist.description}</p>
        </div>

        <div className="checklist-grid">
          {currentChecklist.categories.map((cat, catIdx) => (
            <div key={catIdx} className="checklist-category">
              <h3>{cat.title}</h3>
              <div className="checklist-items">
                {cat.items.map(item => (
                    <label key={item.id} className="checklist-item">
                      <input
                        type="checkbox"
                        checked={!!checkedItems[item.id]}
                        onChange={() => toggleItem(item.id)}
                      />
                      <span className="checkbox-custom"></span>
                      <div className="checklist-item-text">
                        <span className="item-label">{item.label}</span>
                      </div>
                    </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @media print {
          .no-print, .main-header, .main-footer, .side-menu, .detail-actions-top, .checklist-header {
            display: none !important;
          }
          .printable-area {
            display: block !important;
            width: 100% !important;
            position: absolute;
            top: 0;
            left: 0;
          }
          .checklist-page {
            padding: 0;
          }
          body {
            background: white;
          }
          .checklist-item input {
            display: inline-block !important;
          }
          .checklist-grid {
            display: block !important;
          }
          .checklist-category {
            break-inside: avoid;
            margin-bottom: 2rem;
          }
        }
      `}} />
    </div>
  );
};

export default ChecklistSection;
