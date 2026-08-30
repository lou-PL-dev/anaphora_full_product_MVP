export default function PhoneFrame({ framed, onToggleFrame, modeLabel, modeDot, children }) {
  const outerStyle = framed
    ? { position: 'relative', width: 400, height: 854, padding: 5, borderRadius: 58, background: 'linear-gradient(160deg, #1E2B25, #3A4A42)', boxShadow: '0 40px 90px rgba(31,45,38,.34), 0 0 0 1px rgba(0,0,0,.2)' }
    : { position: 'relative', width: '100%', maxWidth: 430, height: '100vh' };
  const innerStyle = framed
    ? { position: 'relative', width: '100%', height: '100%', borderRadius: 53, overflow: 'hidden', background: '#FBF9F6' }
    : { position: 'relative', width: '100%', height: '100%', overflow: 'hidden', background: '#FBF9F6' };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(120% 90% at 20% 0%, #F6F2EC 0%, #EDE8E1 55%, #E3DDD5 100%)', fontFamily: 'Inter, system-ui, sans-serif', padding: 0 }}>
      <div style={{ position: 'fixed', top: 18, right: 18, zIndex: 50, display: 'flex', gap: 8, alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '7px 12px', borderRadius: 999, background: 'rgba(255,255,255,.72)', border: '1px solid rgba(47,74,63,.1)', fontSize: 11, letterSpacing: '.04em', color: '#5C6B62', backdropFilter: 'blur(8px)' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: modeDot }} />{modeLabel}
        </div>
        <button
          onClick={onToggleFrame}
          style={{ padding: '8px 14px', borderRadius: 999, border: '1px solid rgba(47,74,63,.12)', background: 'rgba(255,255,255,.72)', color: '#2F4A3F', fontSize: 11, letterSpacing: '.04em', cursor: 'pointer', backdropFilter: 'blur(8px)' }}
        >
          {framed ? 'Bare viewport' : 'Device frame'}
        </button>
      </div>

      <div style={outerStyle}>
        <div style={innerStyle}>
          {framed && (
            <div style={{ position: 'absolute', top: 12, left: '50%', transform: 'translateX(-50%)', width: 108, height: 30, borderRadius: 999, background: '#16211C', zIndex: 40 }} />
          )}
          <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', background: '#FBF9F6' }}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
