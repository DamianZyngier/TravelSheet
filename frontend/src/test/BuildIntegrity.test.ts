import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Build Integrity', () => {
  it('should have index.html in docs with relative paths', () => {
    // Path to docs/index.html from project root
    const indexPath = path.resolve(__dirname, '../../../docs/index.html');
    
    // Check if file exists
    expect(fs.existsSync(indexPath)).toBe(true);
    
    // Read content
    const content = fs.readFileSync(indexPath, 'utf-8');
    
    // 1. Check if assets use relative paths (starting with ./)
    // Instead of absolute paths (starting with /)
    expect(content).toContain('src="./assets/index-');
    expect(content).toContain('href="./assets/index-');
    expect(content).toContain('href="./favicon.ico"');
    
    // 2. Ensure it's not using absolute paths that would break on GitHub Pages subpaths
    expect(content).not.toContain('src="/assets/index-');
    expect(content).not.toContain('href="/assets/index-');
    expect(content).not.toContain('href="/favicon.ico"');
  });

  it('should have data.json in docs', () => {
    const dataPath = path.resolve(__dirname, '../../../docs/data.json');
    expect(fs.existsSync(dataPath)).toBe(true);
    
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
    expect(Object.keys(data).length).toBeGreaterThan(0);
  });
});
