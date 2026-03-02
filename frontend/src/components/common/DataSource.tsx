import React from 'react';
import { DATA_SOURCES } from '../../constants';

interface DataSourceProps {
  sources: (keyof typeof DATA_SOURCES)[];
  lastUpdated?: string | null;
}

export const DataSource: React.FC<DataSourceProps> = ({ sources, lastUpdated }) => {
  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return null;
      return d.toLocaleString('pl-PL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return null;
    }
  };

  const formattedDate = lastUpdated ? formatDate(lastUpdated) : null;

  return (
    <div className="data-source-footer">
      <div className="data-source-links">
        <span>Źródło: </span>
        {sources.map((s, i) => (
          <span key={s}>
            <a href={DATA_SOURCES[s].url} target="_blank" rel="noopener noreferrer" className="data-source-link">
              {DATA_SOURCES[s].name}
            </a>
            {i < sources.length - 1 ? ', ' : ''}
          </span>
        ))}
      </div>
      {formattedDate && (
        <div className="last-updated-tag">
          Aktualizacja: {formattedDate}
        </div>
      )}
    </div>
  );
};
