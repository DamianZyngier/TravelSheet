import { useState, useEffect, useRef } from 'react';
import { DATA_SOURCES } from '../constants';

export function DataSource({ sources }: { sources: (keyof typeof DATA_SOURCES)[] }) {
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
}

export function LinkifyOdyseusz({ text }: { text: string }) {
  if (!text) return null;
  
  const parts = text.split(/(systemie\s+Odyseusz|systemie Odyseusz)/gi);
  
  return (
    <>
      {parts.map((part, i) => {
        if (part.toLowerCase().includes('systemie') && part.toLowerCase().includes('odyseusz')) {
          return (
            <a 
              key={i} 
              href="https://odyseusz.msz.gov.pl" 
              target="_blank" 
              rel="noopener noreferrer"
              className="odyseusz-link"
              style={{ color: 'inherit', textDecoration: 'underline', fontWeight: 'bold' }}
            >
              {part}
            </a>
          );
        }
        return part;
      })}
    </>
  );
}

export function ExpandableText({ text }: { text: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (textRef.current) {
      const { scrollHeight, clientHeight } = textRef.current;
      setHasMore(scrollHeight > clientHeight);
    }
  }, [text]);

  if (!text) return null;

  return (
    <div className={`expandable-text-container ${isExpanded ? 'expanded' : ''}`}>
      <div 
        ref={textRef}
        className="risk-details-text line-clamp"
      >
        <LinkifyOdyseusz text={text} />
      </div>
      {hasMore && (
        <button 
          className="show-more-btn" 
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? 'Pokaż mniej' : 'Pokaż więcej'}
        </button>
      )}
    </div>
  );
}

export const getLongNameClass = (name: string, type: 'h3' | 'h2') => {
  if (type === 'h3') {
    if (name.length > 25) return 'font-very-small';
    if (name.length > 18) return 'font-small';
  } else {
    if (name.length > 30) return 'font-very-small';
    if (name.length > 20) return 'font-small';
  }
  return '';
};
