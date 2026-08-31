export default function Insight({ insight, newSignals, readiness, goHome }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', position: 'relative', background: '#2F4A3F' }}>
      <div style={{ position: 'absolute', top: 40, right: -70, width: 230, height: 220, borderRadius: '52% 48% 45% 55% / 48% 52% 48% 52%', background: 'rgba(166,154,205,.32)', filter: 'blur(4px)', animation: 'apBreathe 15s ease-in-out infinite' }} />
      <div style={{ position: 'relative', padding: '78px 30px 34px' }}>
        <div style={{ fontSize: 10, letterSpacing: '.16em', color: 'rgba(242,237,230,.6)' }}>WHAT I NOTICED</div>
        <div style={{ marginTop: 20, fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: 32, lineHeight: 1.32, color: '#F2EDE6', textWrap: 'pretty', animation: 'apRise .9s cubic-bezier(.2,.8,.2,1) both' }}>“{insight}”</div>
        <div style={{ marginTop: 22, fontSize: 13.5, lineHeight: 1.65, color: 'rgba(242,237,230,.72)', maxWidth: 300 }}>Added to your Blueprint — this is how matches start making sense.</div>
        <div style={{ marginTop: 28, display: 'flex', flexDirection: 'column', gap: 9 }}>
          {newSignals.map((ns, i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '14px 16px', borderRadius: 15, background: 'rgba(242,237,230,.1)', border: '1px solid rgba(242,237,230,.16)', animation: 'apRise .6s ease both' }}><span style={{ flex: 'none', width: 6, height: 6, borderRadius: '50%', background: '#A69ACD' }} /><span style={{ flex: 1, fontSize: 13.5, color: '#F2EDE6' }}>{ns.label}</span><span style={{ flex: 'none', fontSize: 10, letterSpacing: '.08em', color: 'rgba(242,237,230,.5)' }}>NEW</span></div>)}
        </div>
        <div style={{ marginTop: 26, padding: '16px 18px', borderRadius: 15, background: 'rgba(242,237,230,.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}><span style={{ fontSize: 12.5, color: 'rgba(242,237,230,.78)' }}>Readiness</span><span style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, color: '#F2EDE6' }}>{readiness}%</span></div>
        <button onClick={goHome} style={{ marginTop: 26, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: '#F2EDE6', color: '#2F4A3F', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>Back to home</button>
      </div>
    </div>
  );
}
