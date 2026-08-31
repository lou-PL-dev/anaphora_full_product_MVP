function AnaphoraMark() {
  return (
    <svg viewBox="0 0 180 150" aria-label="Anaphora" style={{ width: 122, height: 102, display: 'block' }}>
      <defs>
        <linearGradient id="anaphoraLoop" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#A69ACD" />
          <stop offset="48%" stopColor="#F2EDE6" />
          <stop offset="100%" stopColor="#2F4A3F" />
        </linearGradient>
      </defs>
      <circle cx="62" cy="22" r="10" fill="#A69ACD" />
      <circle cx="119" cy="22" r="10" fill="#2F4A3F" opacity=".82" />
      <path d="M61 46 C36 48 25 77 39 102 C54 128 96 127 122 97 C143 73 139 50 122 45 C107 40 96 53 94 72 C92 92 106 105 123 106" fill="none" stroke="url(#anaphoraLoop)" strokeWidth="13" strokeLinecap="round" />
      <path d="M119 45 C133 45 141 56 140 72" fill="none" stroke="#2F4A3F" strokeWidth="10" strokeLinecap="round" />
    </svg>
  );
}

export default function Welcome({ onBegin, goPrivacy, goTerms }) {
  return (
    <div className="ap-screen" style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '42px 32px 44px', background: 'linear-gradient(170deg, #F2EDE6 0%, #FFFFFF 48%, #DDEAE6 100%)' }}>
      <div style={{ position: 'absolute', top: -70, right: -90, width: 300, height: 280, borderRadius: '58% 42% 47% 53% / 52% 46% 54% 48%', background: 'linear-gradient(140deg, rgba(166,154,205,.5), rgba(221,234,230,.5))', filter: 'blur(2px)', animation: 'apBreathe 14s ease-in-out infinite' }} />
      <div style={{ position: 'absolute', top: 130, left: -80, width: 210, height: 200, borderRadius: '44% 56% 60% 40% / 48% 52% 48% 52%', background: 'rgba(47,74,63,.09)', animation: 'apBreathe 18s ease-in-out infinite reverse' }} />
      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 4 }}><AnaphoraMark /></div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 46, lineHeight: 1, color: '#2F4A3F', letterSpacing: '-.02em', textAlign: 'center' }}>anaphora</div>
        <div style={{ marginTop: 18, fontSize: 11, letterSpacing: '.17em', color: '#A69ACD', textAlign: 'center' }}>MEANINGFUL CONNECTIONS, LASTING STORIES.</div>
        <div style={{ marginTop: 30, fontFamily: "'Playfair Display', serif", fontSize: 27, lineHeight: 1.35, color: '#2F4A3F' }}>
          AI that listens.<br />Friends who know you.<br />Matches that <span style={{ fontStyle: 'italic', color: '#A69ACD' }}>make sense.</span>
        </div>
        <div style={{ marginTop: 18, fontSize: 14, lineHeight: 1.6, color: '#5C6B62', maxWidth: 280, textWrap: 'pretty' }}>
          No swiping. We start with one conversation about you and who you'd love to meet.
        </div>
        <button onClick={onBegin} style={{ marginTop: 30, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#FFFFFF', fontSize: 15, fontWeight: 500, letterSpacing: '.01em', cursor: 'pointer', boxShadow: '0 10px 26px rgba(47,74,63,.22)' }}>Begin</button>
        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 11, color: '#94A09A', letterSpacing: '.02em' }}>
          <button onClick={goPrivacy} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: '#A69ACD', textDecoration: 'underline', cursor: 'pointer' }}>Privacy by design</button>
          {' · '}
          <button onClick={goTerms} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: '#A69ACD', textDecoration: 'underline', cursor: 'pointer' }}>The fine print</button>
        </div>
      </div>
    </div>
  );
}
