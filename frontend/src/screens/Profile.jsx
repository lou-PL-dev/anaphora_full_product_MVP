import { WEIGHTS } from '../data';
import { SAGE, LAV } from '../theme';

export default function Profile({ gender, onPickGender, ageMax, onAge, breakdownMet, openPlans, goPrivacy, goTerms }) {
  const genderOptions = ['Women', 'Men', 'Everyone'].map((g) => ({
    label: g,
    onPick: () => onPickGender(g),
    border: gender === g ? LAV : 'rgba(47,74,63,.12)',
    bg: gender === g ? 'rgba(166,154,205,.12)' : '#FBF9F6',
    fg: gender === g ? SAGE : '#5C6B62',
  }));

  const breakdown = Object.keys(WEIGHTS).map((k) => ({
    key: k, title: WEIGHTS[k][1], weight: WEIGHTS[k][0],
    ring: breakdownMet[k] ? SAGE : 'rgba(47,74,63,.2)',
    fill: breakdownMet[k] ? SAGE : 'transparent',
  }));

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FBF9F6', padding: '64px 22px 26px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>You</div>
      <div style={{ marginTop: 8, fontSize: 12.5, color: '#94A09A' }}>Anonymous session · your data stays yours</div>

      <div style={{ marginTop: 24, padding: 20, borderRadius: 20, background: '#FFFFFF', border: '1px solid rgba(47,74,63,.08)' }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>BASIC MATCHING PREFERENCES</div>
        <div style={{ marginTop: 6, fontSize: 12, color: '#94A09A' }}>Worth 10% of your readiness.</div>
        <div style={{ marginTop: 16, fontSize: 12.5, color: '#5C6B62' }}>Looking to meet</div>
        <div style={{ marginTop: 9, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {genderOptions.map((go) => (
            <button key={go.label} onClick={go.onPick} style={{ padding: '10px 16px', borderRadius: 999, border: `1.5px solid ${go.border}`, background: go.bg, color: go.fg, fontSize: 12.5, cursor: 'pointer' }}>{go.label}</button>
          ))}
        </div>
        <div style={{ marginTop: 20, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12.5, color: '#5C6B62' }}>Age range · upper limit</span>
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, color: '#2F4A3F' }}>24–{ageMax}</span>
        </div>
        <input className="ap-sl" type="range" min="24" max="52" step="1" value={ageMax} onChange={onAge} style={{ marginTop: 12, width: '100%' }} />
      </div>

      <div style={{ marginTop: 14, padding: 20, borderRadius: 20, background: '#F2EDE6' }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>READINESS BREAKDOWN</div>
        <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 11 }}>
          {breakdown.map((b) => (
            <div key={b.key} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ flex: 'none', width: 16, height: 16, borderRadius: '50%', border: `1.5px solid ${b.ring}`, background: b.fill }} />
              <span style={{ flex: 1, fontSize: 12.5, color: '#2F4A3F' }}>{b.title}</span>
              <span style={{ flex: 'none', fontSize: 11.5, color: '#94A09A' }}>{b.weight}%</span>
            </div>
          ))}
        </div>
      </div>

      <button onClick={openPlans} style={{ marginTop: 14, width: '100%', textAlign: 'left', padding: 20, borderRadius: 20, border: 'none', background: 'linear-gradient(140deg, #EFECF7, #DDEAE6)', cursor: 'pointer' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F' }}>Anaphora+</div>
        <div style={{ marginTop: 6, fontSize: 12.5, color: '#4A5C53' }}>More Discoveries, deeper match explanations.</div>
      </button>

      <div style={{ marginTop: 22, textAlign: 'center', fontSize: 11, color: '#94A09A', letterSpacing: '.02em' }}>
        <button onClick={goPrivacy} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: '#8C7FBE', textDecoration: 'underline', cursor: 'pointer' }}>Privacy by design</button>
        {' · '}
        <button onClick={goTerms} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: '#8C7FBE', textDecoration: 'underline', cursor: 'pointer' }}>The fine print</button>
      </div>
    </div>
  );
}
