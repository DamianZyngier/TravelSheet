import React, { useState, useEffect, useRef } from 'react';
import { LinkifyOdyseusz } from './LinkifyOdyseusz';

interface ExpandableTextProps {
  text: string;
}

export const ExpandableText: React.FC<ExpandableTextProps> = ({ text }) => {
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
};
