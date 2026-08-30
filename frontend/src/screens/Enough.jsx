export default function Enough({ signalCount, goBlueprint, groups }) {
  const enoughCopy = `I heard ${signalCount || 15} things about who you're looking for — and a few about you. Here's what I took from it.`;
  const chips = groups.slice(0, 4).map((g) => g.title.charAt(0) + g.title.slice(1).toLowerCase());

  return (
    <div className="ap-screen" style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '40px 32px', background: 'linear-gradient(165deg, #2F4A3F 0%, #3A5A4C 60%, #46695A 100%)' }}>
      <div style={{ position: 'absolute', top: -60, left: -60, width: 260, height: 240, borderRadius: '55% 45% 50% 50% / 50% 55% 45% 50%', background: 'rgba(166,154,205,.3)', filter: 'blur(6px)', animation: 'apBreathe 16s ease-in-out infinite' }} />
      <div style={{ position: 'absolute', bottom: -80, right: -70, width: 240, height: 230, borderRadius: '48% 52% 43% 57% / 55% 45% 55% 45%', background: 'rgba(221,234,230,.16)', animation: 'apBreathe 20s ease-in-out infinite reverse' }} />
      <div style={{ position: 'relative', animation: 'apRise .8s cubic-bezier(.2,.8,.2,1) both' }}>
        <div style={{ fontSize: 11, letterSpacing: '.18em', color: 'rgba(242,237,230,.6)' }}>STEP ONE COMPLETE</div>
        <div style={{ marginTop: 16, fontFamily: "'Playfair Display', serif", fontSize: 38, lineHeight: 1.16, color: '#F6F2EC' }}>That's enough<br />to begin.</div>
        <div style={{ marginTop: 20, fontSize: 14, lineHeight: 1.65, color: 'rgba(242,237,230,.78)', maxWidth: 290, textWrap: 'pretty' }}>{enoughCopy}</div>
        <div style={{ marginTop: 26, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {chips.map((label, i) => (
            <span key={i} style={{ padding: '8px 14px', borderRadius: 999, border: '1px solid rgba(242,237,230,.28)', color: '#F6F2EC', fontSize: 12, animation: 'apRise .6s ease both' }}>{label}</span>
          ))}
        </div>
        <button onClick={goBlueprint} style={{ marginTop: 34, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: '#F6F2EC', color: '#2F4A3F', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>See my Blueprint</button>
      </div>
    </div>
  );
}
