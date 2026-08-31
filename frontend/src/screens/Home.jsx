export default function Home({ readiness, ready, readinessHeadline, readinessSub, insight, steps, openPlans, goBlueprint, goTalk, goDiscover, signalCount, discoverySaving, discoverySaveError, retryDiscovery }) {
  const arcOffset = 427 - 427 * (readiness / 100);

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FBF9F6' }}>
      <div style={{ padding: '62px 22px 26px', background: 'linear-gradient(165deg, #F2EDE6 0%, #FBF9F6 100%)', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -110, right: -90, width: 250, height: 240, borderRadius: '55% 45% 48% 52% / 50% 52% 48% 50%', background: 'rgba(166,154,205,.18)' }} />
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 21, color: '#2F4A3F' }}>anaphora</div>
          <button onClick={openPlans} style={{ padding: '7px 13px', borderRadius: 999, border: '1px solid rgba(166,154,205,.5)', background: 'rgba(255,255,255,.7)', color: '#A69ACD', fontSize: 11, letterSpacing: '.04em', cursor: 'pointer' }}>Anaphora+</button>
        </div>

        {ready ? (
          <div style={{ position: 'relative', marginTop: 30, paddingBottom: 4 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: '7px 11px', borderRadius: 999, background: 'rgba(47,74,63,.08)', color: '#2F4A3F', fontSize: 11, letterSpacing: '.04em' }}>✓ READY FOR INTRODUCTIONS</div>
            <div style={{ marginTop: 16, fontFamily: "'Playfair Display', serif", fontSize: 30, lineHeight: 1.2, color: '#2F4A3F' }}>Your Blueprint is alive.</div>
            <div style={{ marginTop: 9, maxWidth: 310, fontSize: 13, lineHeight: 1.6, color: '#5C6B62' }}>We know enough to start matching. From here, every conversation and Discovery simply helps Anaphora understand you more deeply.</div>
          </div>
        ) : (
          <div style={{ position: 'relative', marginTop: 24, display: 'flex', alignItems: 'center', gap: 20 }}>
            <div style={{ flex: 'none', position: 'relative', width: 152, height: 152 }}>
              <svg viewBox="0 0 160 160" style={{ width: 152, height: 152, transform: 'rotate(-90deg)' }}>
                <circle cx="80" cy="80" r="68" fill="none" stroke="rgba(47,74,63,.1)" strokeWidth="9" />
                <circle cx="80" cy="80" r="68" fill="none" stroke="#A69ACD" strokeWidth="9" strokeLinecap="round" strokeDasharray="427" strokeDashoffset={arcOffset} style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.2,.8,.2,1)' }} />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 44, lineHeight: 1, color: '#2F4A3F' }}>{readiness}<span style={{ fontSize: 20, color: '#A69ACD' }}>%</span></div>
                <div style={{ marginTop: 4, fontSize: 9.5, letterSpacing: '.14em', color: '#94A09A' }}>MATCH READY</div>
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, lineHeight: 1.3, color: '#2F4A3F' }}>{readinessHeadline}</div>
              <div style={{ marginTop: 8, fontSize: 12.5, lineHeight: 1.55, color: '#5C6B62', textWrap: 'pretty' }}>{readinessSub}</div>
            </div>
          </div>
        )}
      </div>

      <div style={{ padding: '20px 22px 26px', display: 'flex', flexDirection: 'column', gap: 22 }}>
        {discoverySaving && <div style={{ padding: '15px 18px', borderRadius: 18, background: '#EFECF7', display: 'flex', alignItems: 'center', gap: 12, color: '#5C6B62', fontSize: 12.5 }}><span style={{ width: 15, height: 15, flex: 'none', borderRadius: '50%', border: '2px solid rgba(166,154,205,.25)', borderTopColor: '#A69ACD', animation: 'apSpin .8s linear infinite' }} /><span><strong style={{ color: '#2F4A3F', fontWeight: 500 }}>Adding your insight…</strong><br />Your Blueprint will update in a moment.</span></div>}
        {discoverySaveError && !discoverySaving && <div style={{ padding: '15px 18px', borderRadius: 18, background: '#F6F1EE', color: '#5C6B62', fontSize: 12.5, lineHeight: 1.5 }}>We couldn’t add this insight yet. Your answers are still here.<button onClick={retryDiscovery} style={{ marginLeft: 7, padding: 0, border: 'none', background: 'transparent', color: '#A69ACD', font: 'inherit', fontWeight: 600, cursor: 'pointer' }}>Try again</button></div>}

        {ready && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <button onClick={goTalk} style={{ padding: '18px 16px', textAlign: 'left', border: 'none', borderRadius: 18, background: '#2F4A3F', color: '#F2EDE6', cursor: 'pointer' }}><div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18 }}>Talk to Anaphora</div><div style={{ marginTop: 6, fontSize: 11.5, lineHeight: 1.45, opacity: .72 }}>Add nuance or tell me something new →</div></button>
            <button onClick={goDiscover} style={{ padding: '18px 16px', textAlign: 'left', border: '1px solid rgba(166,154,205,.25)', borderRadius: 18, background: '#EFECF7', color: '#2F4A3F', cursor: 'pointer' }}><div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18 }}>Discover more</div><div style={{ marginTop: 6, fontSize: 11.5, lineHeight: 1.45, color: '#6F7B74' }}>Deepen another part of your Blueprint →</div></button>
          </div>
        )}

        {insight && <div style={{ padding: '20px 22px', borderRadius: 20, background: 'linear-gradient(140deg, #EFECF7, #DDEAE6)', animation: 'apRise .5s ease both' }}><div style={{ fontSize: 10, letterSpacing: '.15em', color: '#A69ACD' }}>LATEST DISCOVERY</div><div style={{ marginTop: 10, fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: 20, lineHeight: 1.4, color: '#2F4A3F' }}>“{insight}”</div></div>}

        {!ready && (
          <div>
            <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F', paddingBottom: 6 }}>WHAT ANAPHORA STILL NEEDS</div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {steps.map((st) => <button key={st.key} onClick={st.onGo} style={{ width: '100%', textAlign: 'left', display: 'flex', alignItems: 'center', gap: 13, padding: '15px 4px', border: 'none', borderBottom: '1px solid rgba(47,74,63,.07)', background: 'transparent', cursor: 'pointer' }}><span style={{ flex: 'none', width: 22, height: 22, borderRadius: '50%', border: `1.5px solid ${st.ring}`, background: st.fill, display: 'grid', placeItems: 'center', color: '#FBF9F6', fontSize: 11 }}>{st.mark}</span><span style={{ flex: 1 }}><span style={{ display: 'block', fontSize: 14, color: '#2F4A3F' }}>{st.title}</span><span style={{ display: 'block', marginTop: 3, fontSize: 12, color: '#94A09A' }}>{st.note}</span></span><span style={{ flex: 'none', fontSize: 11, color: '#A69ACD', letterSpacing: '.04em' }}>{st.cta}</span></button>)}
            </div>
          </div>
        )}

        <div style={{ padding: 20, borderRadius: 20, border: '1px solid rgba(47,74,63,.1)', background: '#FFFFFF' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F' }}>Your Relationship Blueprint</div>
          <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.6, color: '#5C6B62' }}>{signalCount} signals across who you are and who you’re looking for.</div>
          <button onClick={goBlueprint} style={{ marginTop: 14, padding: '12px 20px', border: '1px solid rgba(47,74,63,.16)', borderRadius: 999, background: 'transparent', color: '#2F4A3F', fontSize: 13, cursor: 'pointer' }}>Explore your Blueprint</button>
        </div>
      </div>
    </div>
  );
}
