import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ExpandableText } from './ExpandableText';

describe('ExpandableText Component', () => {
  const longText = 'This is a very long text that should definitely exceed the maximum length limit for testing purposes.';

  it('renders full text when shorter than maxLength', () => {
    render(<ExpandableText text="Short text" maxLength={50} />);
    expect(screen.getByText('Short text')).toBeDefined();
    expect(screen.queryByText('Pokaż więcej')).toBeNull();
  });

  it('truncates text when longer than maxLength', () => {
    const limit = 20;
    render(<ExpandableText text={longText} maxLength={limit} />);
    
    // Check if truncated text is present
    const expectedTruncated = longText.substring(0, limit) + '...';
    expect(screen.getByText(expectedTruncated)).toBeDefined();
    
    // Check if show more button is present
    expect(screen.getByText('Pokaż więcej')).toBeDefined();
  });

  it('expands text when clicking show more', () => {
    const limit = 20;
    render(<ExpandableText text={longText} maxLength={limit} />);
    
    const button = screen.getByText('Pokaż więcej');
    fireEvent.click(button);
    
    // Should now show full text (or at least the start without ...)
    expect(screen.getByText(longText)).toBeDefined();
    expect(screen.getByText('Pokaż mniej')).toBeDefined();
  });

  it('handles empty text gracefully', () => {
    const { container } = render(<ExpandableText text="" />);
    expect(container.firstChild).toBeNull();
  });
});
