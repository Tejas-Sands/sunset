// Approved SUNSET silhouette: a semicircle and three progressively shorter lines.
export default function SunsetMark({className = ''}: {className?: string}) {
  return <svg className={className} width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true" focusable="false">
    <path d="M5 22a15 15 0 0 1 30 0" fill="currentColor"/>
    <path d="M5 26h30M8 31h24M13 36h14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
  </svg>;
}
