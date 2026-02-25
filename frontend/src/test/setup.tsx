import '@testing-library/jest-dom'
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});

// Mock IntersectionObserver which is missing in jsdom
class IntersectionObserverMock {
  readonly root: Element | null = null;
  readonly rootMargin: string = '';
  readonly thresholds: ReadonlyArray<number> = [];
  
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords() { return []; }
}

vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

// Mock window.scrollTo
vi.stubGlobal('scrollTo', vi.fn());

// Mock react-simple-maps to avoid topology loading issues in tests
vi.mock('react-simple-maps', () => ({
  ComposableMap: ({ children }: any) => <svg data-testid="mock-map">{children}</svg>,
  Geographies: ({ children }: any) => children({ geographies: [] }),
  Geography: () => <path />,
  Marker: ({ children }: any) => <g>{children}</g>,
  ZoomableGroup: ({ children }: any) => <g>{children}</g>,
}));
