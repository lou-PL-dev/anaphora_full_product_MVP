export default function Enough({ signalCount, goBlueprint, goHome, groups, isFollowUp }) {
  const enoughCopy = isFollowUp
    ? `What you just shared has been added to your Blueprint — Anaphora's picture of you keeps getting sharper.`
    : `From what you've shared, Anaphora already has a first picture of you — and of the person who could feel right for you.`;
  const chips = groups.slice(0, 4).map((g) => g.title.charAt(0) + g.title.slice(1).toLowerCase());

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
          <div style={{ fontSize: 10.5, letterSpacing: '.18em', color: 'rgba(242,237,230,.68)' }}>A FIRST PICTURE IS TAKING SHAPE</div>
        </div>

        <div style={{ marginTop: 20, fontFamily: "'Playfair Display', serif", fontSize: 37, lineHeight: 1.16, color: '#F2EDE6' }}>
          Here’s what<br />I’m beginning to see.
        </div>

        <div style={{ marginTop: 19, fontSize: 14, lineHeight: 1.65, color: 'rgba(242,237,230,.78)', maxWidth: 300, textWrap: 'pretty' }}>{enoughCopy}</div>

        <div style={{ marginTop: 28, paddingTop: 18, borderTop: '1px solid rgba(242,237,230,.16)' }}>
          <div style={{ fontSize: 10, letterSpacing: '.15em', color: 'rgba(242,237,230,.52)' }}>{signalCount || 15} SIGNALS SO FAR</div>
          <div style={{ marginTop: 13, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {chips.map((label, i) => (
              <span key={i} style={{ padding: '8px 13px', borderRadius: 999, background: 'rgba(255,255,255,.06)', border: '1px solid rgba(242,237,230,.20)', color: '#F2EDE6', fontSize: 11.5 }}>{label}</span>
            ))}
          </div>
        </div>

        <button onClick={goBlueprint} style={{ marginTop: 34, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: '#F2EDE6', color: '#2F4A3F', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>See my Blueprint</button>
        <button onClick={goHome} style={{ marginTop: 12, width: '100%', padding: 15, border: '1px solid rgba(242,237,230,.28)', borderRadius: 999, background: 'transparent', color: '#F2EDE6', fontSize: 14, cursor: 'pointer' }}>Back to Home</button>
      </div>
    </div>
  );
}
