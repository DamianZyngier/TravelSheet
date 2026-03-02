import React, { useState, useEffect, useRef } from 'react';
import { LinkifyOdyseusz } from './LinkifyOdyseusz';

interface ExpandableTextProps {
  text: string;
  maxLength?: number;
}

export const ExpandableText: React.FC<ExpandableTextProps> = ({ text, maxLength }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (maxLength) {
      setHasMore(text.length > maxLength);
    } else if (textRef.current) {
      const { scrollHeight, clientHeight } = textRef.current;
      setHasMore(scrollHeight > clientHeight);
    }
  }, [text, maxLength]);

  if (!text) return null;

  const displayText = (!isExpanded && maxLength && text.length > maxLength) 
    ? text.substring(0, maxLength) + '...' 
    : text;

  return (
    <div className={`expandable-text-container ${isExpanded ? 'expanded' : ''}`}>
      <div 
        ref={textRef}
        className={`risk-details-text ${!maxLength ? 'line-clamp' : ''}`}
      >
        <LinkifyOdyseusz text={displayText} />
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
};
