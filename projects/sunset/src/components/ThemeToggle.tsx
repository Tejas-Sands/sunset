'use client';

import {toggleTheme} from '../lib/theme.mjs';

export default function ThemeToggle() {
  return <button type="button" className="theme-toggle" onClick={toggleTheme} title="Change color theme">
    <span className="theme-to-dark">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20.8 13.1A8.5 8.5 0 0 1 10.9 3.2a8.5 8.5 0 1 0 9.9 9.9Z"/></svg>
      <span className="sr-only">Switch to dark mode</span><span className="theme-name" aria-hidden="true">Dark</span>
    </span>
    <span className="theme-to-light">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4m11.2 11.2L19 19M5 19l1.4-1.4M17.6 6.4 19 5"/></svg>
      <span className="sr-only">Switch to light mode</span><span className="theme-name" aria-hidden="true">Light</span>
    </span>
  </button>;
}
