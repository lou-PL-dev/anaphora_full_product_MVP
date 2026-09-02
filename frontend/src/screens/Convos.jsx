export default function Convos({ convoStatus, convoCta, resumeConversation, discoveries, startDiscovery }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: 'linear-gradient(180deg, #F2EDE6 0%, #FFFFFF 42%, #F2EDE6 100%)', padding: '64px 22px 24px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>Conversations</div>
      <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>Anaphora is here to listen.</div>

      <button
        onClick={resumeConversation}
        style={{ marginTop: 24, position: 'relative', overflow: 'hidden', width: '100%', textAlign: 'left', padding: '30px 26px 26px', borderRadius: 28, border: 'none', background: 'linear-gradient(150deg, #F2EDE6 0%, #FFFFFF 52%, #DDEAE6 100%)', cursor: 'pointer' }}
      >
        <span style={{ position: 'absolute', width: 210, height: 196, right: -66, top: -74, borderRadius: '56% 44% 48% 52% / 50% 46% 54% 50%', background: 'linear-gradient(140deg, rgba(166,154,205,.42), rgba(221,234,230,.5))', filter: 'blur(1px)' }} />
        <span style={{ position: 'absolute', width: 130, height: 120, left: -46, bottom: -52, borderRadius: '45% 55% 60% 40% / 52% 44% 56% 48%', background: 'rgba(166,154,205,.14)' }} />
        <span style={{ position: 'relative', display: 'block', fontSize: 10, letterSpacing: '.16em', color: '#A69ACD' }}>YOUR CONVERSATION</span>
        <span style={{ position: 'relative', display: 'block', marginTop: 14, maxWidth: 250, fontFamily: "'Playfair Display', serif", fontSize: 30, lineHeight: 1.18, color: '#2F4A3F' }}>The person you'd love to meet</span>
        <span style={{ position: 'relative', display: 'block', marginTop: 12, maxWidth: 268, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>Keep adding nuance about who you're looking for — and about you.</span>
        <span style={{ position: 'relative', display: 'flex', alignItems: 'baseline', gap: 12, marginTop: 22 }}>
          <span style={{ flex: 1, fontSize: 11.5, color: '#A69ACD' }}>{convoStatus}</span>
          <span style={{ flex: 'none', fontSize: 13, fontWeight: 600, color: '#2F4A3F' }}>{convoCta} →</span>
        </span>
      </button>

      <div style={{ marginTop: 32, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>DISCOVERIES</div>
        <div style={{ fontSize: 11, color: '#A69ACD' }}>GO A LITTLE DEEPER</div>
      </div>

      <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 10 }}>
        {discoveries.map((d) => (
          <button
            key={d.id}
            onClick={() => startDiscovery(d.id, 'convos')}
            style={{ width: '100%', textAlign: 'left', padding: 18, borderRadius: 20, border: 'none', background: d.done ? '#DDEAE6' : '#F2EDE6', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
              <div style={{ fontSize: 10, letterSpacing: '.13em', color: '#A69ACD' }}>{d.deeper ? 'DEEPER REFLECTION' : `${d.questions} QUESTIONS · ${d.minutes} MIN`}</div>
              <div style={{ padding: d.done ? '4px 8px' : 0, borderRadius: 999, background: d.done ? '#F2EDE6' : 'transparent', fontSize: 11, color: d.done ? '#2F4A3F' : '#A69ACD', whiteSpace: 'nowrap', fontWeight: d.done ? 600 : 400 }}>{d.done ? 'Done ✓' : 'Explore →'}</div>
            </div>
            <div style={{ marginTop: 7, fontFamily: "'Playfair Display', serif", fontSize: 19, lineHeight: 1.3, color: '#2F4A3F' }}>{d.title}</div>
            <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.5, color: '#2F4A3F' }}>{d.note}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
