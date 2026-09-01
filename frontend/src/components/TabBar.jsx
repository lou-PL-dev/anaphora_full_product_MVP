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
              <img
                src="/brand/anaphora-mark.png"
                alt=""
                aria-hidden="true"
                style={{ width: 23, height: 23, objectFit: 'contain', opacity: active ? 1 : .48, filter: active ? 'none' : 'grayscale(1)' }}
              />
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
