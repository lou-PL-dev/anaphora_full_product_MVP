export default function Discovery({
  discoveryBack, discoveryProgress, discoveryCounter,
  dqPrompt, dqIsChoice, dqOptions, dqIsSpectrum, dqLeft, dqRight, dqValue, onSpectrum, dqReading,
  dqNextLabel, dqNextBg, discoveryNext,
}) {
  return (
    <div className="ap-screen" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: 'linear-gradient(175deg, #FBF9F6, #F2EDE6)' }}>
      <div style={{ padding: '60px 22px 8px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={discoveryBack} style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid rgba(47,74,63,.12)', background: 'transparent', color: '#2F4A3F', cursor: 'pointer' }}>←</button>
        <div style={{ flex: 1, height: 3, borderRadius: 2, background: 'rgba(47,74,63,.1)', overflow: 'hidden' }}>
          <div style={{ height: '100%', borderRadius: 2, background: 'linear-gradient(90deg, #2F4A3F, #A69ACD)', width: discoveryProgress, transition: 'width .5s cubic-bezier(.2,.8,.2,1)' }} />
        </div>
        <div style={{ fontSize: 11, color: '#94A09A', letterSpacing: '.06em' }}>{discoveryCounter}</div>
      </div>

      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '24px 26px 10px' }}>
        <div style={{ fontSize: 10, letterSpacing: '.15em', color: '#A69ACD' }}>WHAT KIND OF LIFE ARE YOU BUILDING?</div>
        <div style={{ marginTop: 14, fontFamily: "'Playfair Display', serif", fontSize: 27, lineHeight: 1.25, color: '#2F4A3F', textWrap: 'pretty' }}>{dqPrompt}</div>

        {dqIsChoice && (
          <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 11 }}>
            {dqOptions.map((o) => (
              <button
                key={o.key}
                onClick={o.onPick}
                style={{ width: '100%', textAlign: 'left', padding: '18px 20px', borderRadius: 18, border: `1.5px solid ${o.border}`, background: o.bg, color: '#2F4A3F', fontSize: 14, lineHeight: 1.5, cursor: 'pointer', transition: 'border-color .25s, background .25s' }}
              >
                {o.label}
              </button>
            ))}
          </div>
        )}

        {dqIsSpectrum && (
          <div style={{ marginTop: 46 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#5C6B62', letterSpacing: '.02em' }}>
              <span>{dqLeft}</span><span>{dqRight}</span>
            </div>
            <input className="ap-sl" type="range" min="0" max="100" step="1" value={dqValue} onChange={onSpectrum} style={{ marginTop: 14, width: '100%' }} />
            <div style={{ marginTop: 26, textAlign: 'center', fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: 19, color: '#2F4A3F', minHeight: 30 }}>{dqReading}</div>
            <div style={{ marginTop: 6, textAlign: 'center', fontSize: 12, color: '#94A09A' }}>Drag — there's no right answer.</div>
          </div>
        )}
      </div>

      <div style={{ padding: '12px 26px 26px' }}>
        <button onClick={discoveryNext} style={{ width: '100%', padding: 17, border: 'none', borderRadius: 999, background: dqNextBg, color: '#F6F2EC', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>{dqNextLabel}</button>
      </div>
    </div>
  );
}
