// Reuses Enough.jsx's dark hero pattern (same background, decorative
// paths, typography, animation) for the friend's closing screen.
export default function FriendDone({ inviterName }) {
  const goApp = () => { window.location.href = window.location.origin; };
  return (
    <div className="ap-screen" style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '42px 32px', background: '#2F4A3F' }}>
      <div aria-hidden="true" style={{ position: 'absolute', inset: 0, opacity: .34 }}>
        <svg viewBox="0 0 390 760" preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
          <path d="M-40 190 C70 110, 145 145, 205 235 S318 350, 430 256" fill="none" stroke="rgba(166,154,205,.55)" strokeWidth="1.4" />
          <path d="M-60 260 C58 178, 145 218, 212 305 S322 405, 438 332" fill="none" stroke="rgba(221,234,230,.36)" strokeWidth="1" />
          <path d="M-20 525 C90 430, 180 452, 238 530 S330 640, 425 570" fill="none" stroke="rgba(242,237,230,.20)" strokeWidth="1.2" />
        </svg>
      </div>
      <div style={{ position: 'relative', animation: 'apRise .8s cubic-bezier(.2,.8,.2,1) both' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#A69ACD' }} />
          <div style={{ fontSize: 10.5, letterSpacing: '.18em', color: 'rgba(242,237,230,.68)' }}>SENT</div>
        </div>
        <div style={{ marginTop: 20, fontFamily: "'Playfair Display', serif", fontSize: 33, lineHeight: 1.2, color: '#F2EDE6' }}>
          Thank you for<br />helping {inviterName}.
        </div>
        <div style={{ marginTop: 19, fontSize: 14, lineHeight: 1.65, color: 'rgba(242,237,230,.78)', maxWidth: 300, textWrap: 'pretty' }}>
          What you shared stays private. {inviterName} will only see the broader themes Anaphora draws from it, and decides for themselves what to keep.
        </div>
        <button onClick={goApp} style={{ marginTop: 26, padding: '13px 24px', border: '1px solid rgba(242,237,230,.28)', borderRadius: 999, background: 'transparent', color: '#F2EDE6', fontSize: 13.5, cursor: 'pointer' }}>Go to Anaphora</button>
      </div>
    </div>
  );
}
