import React from 'react';
import { DATA_SOURCES } from '../../constants';

interface DataSourceProps {
  sources: (keyof typeof DATA_SOURCES)[];
  lastUpdated?: string | null;
}

export const DataSource: React.FC<DataSourceProps> = ({ sources, lastUpdated }) => {
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
      {lastUpdated && (
        <div className="last-updated-tag">
          Aktualizacja: {new Date(lastUpdated).toLocaleDateString('pl-PL')}
        </div>
      )}
    </div>
  );
};
