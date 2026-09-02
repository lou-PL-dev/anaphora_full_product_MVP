import { SAGE, LAV, SKY, SAND, CLOUD } from '../theme';

export default function Profile({
  gender, onPickGender, ageMin, ageMax, onAgeMin, onAgeMax,
  onSavePreferences, preferencesSaving, preferencesSaved, preferencesError,
  readiness, breakdownMet, openPlans, goPrivacy, goTerms,
  signalCount, goBlueprint,
}) {
  const genderOptions = ['Women', 'Men', 'Everyone'].map((g) => ({
    label: g,
    onPick: () => onPickGender(g),
    border: gender === g ? LAV : SKY,
    bg: gender === g ? 'rgba(166,154,205,.12)' : CLOUD,
    fg: SAGE,
  }));

  const breakdown = [
    ['basic_matching_preferences', 'Basic matching preferences', 20],
    ['discovery_completed', 'A Discovery completed', 20],
    ['me_profile', 'About you', 30],
    ['ideal_partner_profile', 'Who you are looking for', 30],
  ].map(([key, title, weight]) => ({
    key, title, weight,
    ring: breakdownMet[key] ? SAGE : SKY,
    fill: breakdownMet[key] ? SAGE : 'transparent',
  }));

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: CLOUD, padding: '64px 22px 26px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: SAGE }}>You</div>
      <div style={{ marginTop: 8, fontSize: 12.5, color: LAV }}>Anonymous session · your data stays yours</div>

      <div style={{ marginTop: 24, padding: 20, borderRadius: 20, background: CLOUD, border: `1px solid ${SKY}` }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: SAGE }}>BASIC MATCHING PREFERENCES</div>
        <div style={{ marginTop: 16, fontSize: 12.5, color: SAGE }}>Looking to meet</div>
        <div style={{ marginTop: 9, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {genderOptions.map((go) => (
            <button key={go.label} onClick={go.onPick} style={{ padding: '10px 16px', borderRadius: 999, border: `1.5px solid ${go.border}`, background: go.bg, color: go.fg, fontSize: 12.5, cursor: 'pointer' }}>{go.label}</button>
          ))}
        </div>

        <div style={{ marginTop: 20, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12.5, color: SAGE }}>Age range</span>
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, color: SAGE }}>{ageMin}–{ageMax}</span>
        </div>
        <div style={{ marginTop: 12, fontSize: 11.5, color: LAV }}>Minimum age · {ageMin}</div>
        <input className="ap-sl" type="range" min="18" max="99" step="1" value={ageMin} onChange={onAgeMin} style={{ marginTop: 6, width: '100%' }} />
        <div style={{ marginTop: 12, fontSize: 11.5, color: LAV }}>Maximum age · {ageMax}</div>
        <input className="ap-sl" type="range" min="18" max="99" step="1" value={ageMax} onChange={onAgeMax} style={{ marginTop: 6, width: '100%' }} />

        {preferencesError && <div style={{ marginTop: 12, fontSize: 12, color: '#B04A3A' }}>{preferencesError}</div>}
        {preferencesSaved && !preferencesError && <div style={{ marginTop: 12, fontSize: 12, color: SAGE }}>Preferences saved ✓</div>}
        <button onClick={onSavePreferences} disabled={!gender || preferencesSaving} style={{ marginTop: 16, width: '100%', padding: '12px 16px', borderRadius: 999, border: 'none', background: gender && !preferencesSaving ? SAGE : SAND, color: gender && !preferencesSaving ? CLOUD : SAGE, fontSize: 13, cursor: gender && !preferencesSaving ? 'pointer' : 'default' }}>{preferencesSaving ? 'Saving…' : 'Save preferences'}</button>
      </div>

      <div style={{ marginTop: 14, padding: 20, borderRadius: 20, border: `1px solid ${SKY}`, background: CLOUD }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: SAGE }}>Your Blueprint</div>
        <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.6, color: SAGE }}>{signalCount} signals, drawn from your own words.</div>
        <button onClick={goBlueprint} style={{ marginTop: 14, padding: '12px 20px', border: `1px solid ${SKY}`, borderRadius: 999, background: 'transparent', color: SAGE, fontSize: 13, cursor: 'pointer' }}>Review it</button>
      </div>

      {readiness < 100 && (
        <div style={{ marginTop: 14, padding: 20, borderRadius: 20, background: SAND }}>
          <div style={{ fontSize: 11, letterSpacing: '.14em', color: SAGE }}>READINESS BREAKDOWN</div>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 11 }}>
            {breakdown.map((b) => <div key={b.key} style={{ display: 'flex', alignItems: 'center', gap: 10 }}><span style={{ flex: 'none', width: 16, height: 16, borderRadius: '50%', border: `1.5px solid ${b.ring}`, background: b.fill }} /><span style={{ flex: 1, fontSize: 12.5, color: SAGE }}>{b.title}</span><span style={{ flex: 'none', fontSize: 11.5, color: LAV }}>{b.weight}%</span></div>)}
          </div>
        </div>
      )}

      <button onClick={openPlans} style={{ marginTop: 14, width: '100%', textAlign: 'left', padding: 20, borderRadius: 20, border: 'none', background: 'linear-gradient(140deg, rgba(166,154,205,.18), #DDEAE6)', cursor: 'pointer' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: SAGE }}>Anaphora+</div>
        <div style={{ marginTop: 6, fontSize: 12.5, color: SAGE }}>More Discoveries, deeper match explanations.</div>
      </button>

      <div style={{ marginTop: 22, textAlign: 'center', fontSize: 11, color: LAV, letterSpacing: '.02em' }}>
        <button onClick={goPrivacy} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: LAV, textDecoration: 'underline', cursor: 'pointer' }}>Privacy by design</button>{' · '}<button onClick={goTerms} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: LAV, textDecoration: 'underline', cursor: 'pointer' }}>The fine print</button>
      </div>
    </div>
  );
}
