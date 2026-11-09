// Runs in the document head before either page paints. Storage is optional.
export const themeBootstrap = `(() => {
  let theme = 'light';
  try { if (window.matchMedia('(prefers-color-scheme: dark)').matches) theme = 'dark'; } catch {}
  try {
    const saved = window.localStorage.getItem('sunset-theme');
    if (saved === 'light' || saved === 'dark') theme = saved;
  } catch {}
  document.documentElement.dataset.theme = theme;
})();`;

export function toggleTheme() {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = theme;
  try { window.localStorage.setItem('sunset-theme', theme); } catch {}
}
