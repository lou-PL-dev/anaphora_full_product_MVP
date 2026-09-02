export default function Welcome({ onBegin, goPrivacy, goTerms, name, onName, canBegin }) {
  return (
    <div className="ap-screen" style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '42px 32px 44px', background: 'linear-gradient(170deg, #F2EDE6 0%, #FFFFFF 48%, #DDEAE6 100%)' }}>
      <div style={{ position: 'absolute', top: -70, right: -90, width: 300, height: 280, borderRadius: '58% 42% 47% 53% / 52% 46% 54% 48%', background: 'linear-gradient(140deg, rgba(166,154,205,.5), rgba(221,234,230,.5))', filter: 'blur(2px)', animation: 'apBreathe 14s ease-in-out infinite' }} />
      <div style={{ position: 'absolute', top: 130, left: -80, width: 210, height: 200, borderRadius: '44% 56% 60% 40% / 48% 52% 48% 52%', background: '#DDEAE6', animation: 'apBreathe 18s ease-in-out infinite reverse' }} />
      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 6 }}>
          <img src="/brand/anaphora-mark.png" alt="Anaphora" style={{ width: 126, height: 'auto', display: 'block', objectFit: 'contain' }} />
        </div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 46, lineHeight: 1, color: '#2F4A3F', letterSpacing: '-.02em', textAlign: 'center' }}>anaphora</div>
        <div style={{ marginTop: 18, fontSize: 11, letterSpacing: '.17em', color: '#A69ACD', textAlign: 'center' }}>MEANINGFUL CONNECTIONS, LASTING STORIES.</div>
        <div style={{ marginTop: 30, fontFamily: "'Playfair Display', serif", fontSize: 27, lineHeight: 1.35, color: '#2F4A3F' }}>
          AI that listens.<br />Friends who know you.<br />Matches that <span style={{ fontStyle: 'italic', color: '#A69ACD' }}>make sense.</span>
        </div>
        <div style={{ marginTop: 18, fontSize: 14, lineHeight: 1.6, color: '#2F4A3F', maxWidth: 280, textWrap: 'pretty' }}>
          No swiping. We start with one conversation about you and who you'd love to meet.
        </div>
        <input
          value={name}
          onChange={onName}
          placeholder="Your first name"
          style={{ marginTop: 22, width: '100%', boxSizing: 'border-box', padding: '15px 17px', borderRadius: 16, border: '1.5px solid #DDEAE6', background: '#FFFFFF', color: '#2F4A3F', fontFamily: "'Inter', sans-serif", fontSize: 14, outline: 'none' }}
        />
        <button onClick={onBegin} disabled={!canBegin} style={{ marginTop: 12, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: canBegin ? '#2F4A3F' : '#F2EDE6', color: canBegin ? '#FFFFFF' : '#2F4A3F', fontSize: 15, fontWeight: 500, letterSpacing: '.01em', cursor: canBegin ? 'pointer' : 'default', boxShadow: canBegin ? '0 10px 26px rgba(166,154,205,.24)' : 'none' }}>Begin</button>
        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 11, color: '#A69ACD', letterSpacing: '.02em' }}>
          <button onClick={goPrivacy} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: '#A69ACD', textDecoration: 'underline', cursor: 'pointer' }}>Privacy by design</button>
          {' · '}
          <button onClick={goTerms} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: '#A69ACD', textDecoration: 'underline', cursor: 'pointer' }}>The fine print</button>
        </div>
      </div>
    </div>
  );
}
