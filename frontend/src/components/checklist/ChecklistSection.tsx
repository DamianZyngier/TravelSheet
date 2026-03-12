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

  const clearAll = () => {
    if (Object.keys(checkedItems).length === 0) return;
    if (window.confirm('Czy na pewno chcesz wyczyścić całą checklistę?')) {
      setCheckedItems({});
    }
  };

  const toggleCategory = (categoryItems: { id: string }[]) => {
    const allChecked = categoryItems.every(item => !!checkedItems[item.id]);
    const newChecked = { ...checkedItems };
    
    categoryItems.forEach(item => {
      newChecked[item.id] = !allChecked;
    });
    
    setCheckedItems(newChecked);
  };

  const clearCategory = (categoryItems: { id: string }[]) => {
    const newChecked = { ...checkedItems };
    categoryItems.forEach(item => {
      delete newChecked[item.id];
    });
    setCheckedItems(newChecked);
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
          <div className="checklist-action-buttons">
            <button 
              className="secondary-btn clear-all-btn" 
              onClick={clearAll}
              disabled={Object.keys(checkedItems).length === 0}
            >
              🗑️ Wyczyść wszystko
            </button>
            <button className="primary-btn print-btn" onClick={handlePrint}>
              🖨️ Drukuj / PDF
            </button>
          </div>
        </div>
      </div>

      <div className="static-page-content printable-area">
        <div className="static-page-title-section">
          <h1>{currentChecklist.title}</h1>
          <p className="static-page-desc">{currentChecklist.description}</p>
        </div>

        <div className="checklist-grid">
          {currentChecklist.categories.map((cat, catIdx) => {
            const isAnyChecked = cat.items.some(item => !!checkedItems[item.id]);
            const isAllChecked = cat.items.every(item => !!checkedItems[item.id]);

            return (
              <div key={catIdx} className="checklist-category">
                <div className="category-header-row">
                  <h3>{cat.title}</h3>
                  <div className="category-actions no-print">
                    <button 
                      className={`category-action-btn toggle-all ${isAllChecked ? 'is-all-checked' : ''}`} 
                      onClick={() => toggleCategory(cat.items)}
                      title={isAllChecked ? "Odznacz wszystko" : "Zaznacz wszystko"}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        {isAllChecked ? (
                          <polyline points="20 6 9 17 4 12"></polyline>
                        ) : (
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        )}
                      </svg>
                    </button>
                    {isAnyChecked && (
                      <button 
                        className="category-action-btn clear-cat" 
                        onClick={() => clearCategory(cat.items)}
                        title="Wyczyść kategorię"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
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
            );
          })}
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .checklist-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1.5rem;
          margin-top: 1rem;
          flex-wrap: wrap;
        }
        .checklist-action-buttons {
          display: flex;
          gap: 0.75rem;
          align-items: center;
        }
        .variant-tabs {
          display: flex;
          background-color: #edf2f7;
          padding: 4px;
          border-radius: 12px;
          position: relative;
          width: 100%;
          max-width: 360px;
          height: 44px;
          flex-shrink: 0;
        }
        .variant-tab {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.8rem;
          font-weight: 800;
          color: #4a5568;
          z-index: 2;
          border-radius: 8px;
          transition: color 0.2s;
          letter-spacing: 0.025em;
        }
        .secondary-btn {
          background-color: white;
          color: #4a5568;
          border: 1px solid #e2e8f0;
          padding: 0.6rem 1rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.9rem;
          display: flex;
          align-items: center;
          gap: 6px;
          height: 40px;
          white-space: nowrap;
        }
        .secondary-btn:hover:not(:disabled) {
          background-color: #f7fafc;
          border-color: #cbd5e0;
          color: #2d3748;
        }
        .secondary-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .primary-btn.print-btn {
          height: 40px;
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 0.6rem 1.2rem;
          white-space: nowrap;
        }
        .category-header-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          border-bottom: 2px solid #edf2f7;
          padding-bottom: 0.5rem;
        }
        .category-header-row h3 {
          margin: 0 !important;
          padding: 0 !important;
          border: none !important;
        }
        .category-actions {
          display: flex;
          gap: 0.4rem;
        }
        .category-action-btn {
          background: white;
          border: 1.5px solid #e2e8f0;
          border-radius: 6px;
          cursor: pointer;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #718096;
          transition: all 0.2s;
          padding: 0;
        }
        .category-action-btn:hover {
          background-color: #f7fafc;
          border-color: #cbd5e0;
          color: #4a5568;
        }
        .category-action-btn.toggle-all.is-all-checked {
          background-color: #ebf8ff;
          border-color: #3182ce;
          color: #3182ce;
        }
        .category-action-btn.clear-cat:hover {
          color: #e53e3e;
          border-color: #feb2b2;
          background-color: #fff5f5;
        }
        @media print {
          .no-print, .main-header, .main-footer, .side-menu, .detail-actions-top, .checklist-header, .category-actions {
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
