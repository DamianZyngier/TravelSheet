import React from 'react';

interface LinkifyOdyseuszProps {
  text: string;
}

export const LinkifyOdyseusz: React.FC<LinkifyOdyseuszProps> = ({ text }) => {
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
};
