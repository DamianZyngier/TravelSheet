import React from 'react';
import { DATA_SOURCES } from '../../constants';

interface DataSourceProps {
  sources: (keyof typeof DATA_SOURCES)[];
}

export const DataSource: React.FC<DataSourceProps> = ({ sources }) => {
  return (
    <div className="data-source-footer">
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
  );
};
