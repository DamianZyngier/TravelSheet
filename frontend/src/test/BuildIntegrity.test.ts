import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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

  it('should have maxLength prop defined in ExpandableText component source', () => {
    const componentPath = path.resolve(__dirname, '../components/common/ExpandableText.tsx');
    expect(fs.existsSync(componentPath)).toBe(true);
    
    const content = fs.readFileSync(componentPath, 'utf-8');
    // Verify that the interface includes maxLength
    expect(content).toContain('maxLength?: number');
    // Verify that the component destructures maxLength
    expect(content).toContain('({ text, maxLength })');
  });
});
