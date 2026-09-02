import { TABS } from '../data';
import { SAGE, LAV, SKY } from '../theme';

export default function TabBar({ activeScreen, onGo }) {
  return (
    <div style={{ flex: 'none', display: 'flex', padding: '10px 8px 26px', borderTop: `1px solid ${SKY}`, background: 'rgba(255,255,255,.96)', backdropFilter: 'blur(10px)' }}>
      {TABS.map(([key, label, icon]) => {
        const active = activeScreen === key;
        const color = active ? SAGE : LAV;
        const isIntros = key === 'matches';
        return (
          <button
            key={key}
            onClick={() => onGo(key)}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5, padding: '6px 0', border: 'none', background: 'transparent', cursor: 'pointer', color }}
          >
            {isIntros ? (
              <svg viewBox="0 0 28 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 24, height: 21 }}>
                <path d="M2 12s4.4-7 12-7 12 7 12 7-4.4 7-12 7S2 12 2 12Z" />
                <path d="M14 16.7c-1.2-1-4-3.1-4-5.5 0-1.4 1-2.5 2.4-2.5.8 0 1.4.4 1.6 1 .3-.6.9-1 1.7-1 1.4 0 2.4 1.1 2.4 2.5 0 2.4-2.9 4.5-4.1 5.5Z" fill="currentColor" stroke="none" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 21, height: 21 }}>
                <path d={icon} />
              </svg>
            )}
            <span style={{ fontSize: 9.5, letterSpacing: '.03em' }}>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
