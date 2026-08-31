export default function Convos({ convoStatus, convoCta, resumeConversation, discoveries, startDiscovery }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FFFFFF', padding: '64px 22px 24px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>Conversations</div>
      <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.6, color: '#5C6B62' }}>Share only what feels useful.</div>

      <button
        onClick={resumeConversation}
        style={{ marginTop: 22, width: '100%', textAlign: 'left', padding: '24px 22px', borderRadius: 24, border: 'none', background: '#2F4A3F', cursor: 'pointer', boxShadow: '0 12px 30px rgba(47,74,63,.16)' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 14 }}>
          <div style={{ fontSize: 10, letterSpacing: '.15em', color: '#A69ACD' }}>YOUR CONVERSATION</div>
          <div style={{ padding: '6px 10px', borderRadius: 999, background: '#DDEAE6', color: '#2F4A3F', fontSize: 10.5, fontWeight: 600 }}>{convoCta} →</div>
        </div>
        <div style={{ marginTop: 14, fontFamily: "'Playfair Display', serif", fontSize: 24, lineHeight: 1.25, color: '#FFFFFF' }}>The person you'd love to meet</div>
        <div style={{ marginTop: 8, maxWidth: 300, fontSize: 12.5, lineHeight: 1.6, color: '#DDEAE6' }}>Keep adding nuance about who you're looking for — and about you.</div>
        <div style={{ marginTop: 18, fontSize: 11.5, color: '#F2EDE6' }}>{convoStatus}</div>
      </button>

      <div style={{ marginTop: 32, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>DISCOVERIES</div>
        <div style={{ fontSize: 11, color: '#94A09A' }}>Choose what feels useful</div>
      </div>

      <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 10 }}>
        {discoveries.map((d, i) => (
          <button
            key={d.id}
            onClick={() => startDiscovery(d.id, 'convos')}
            style={{ width: '100%', textAlign: 'left', padding: 18, borderRadius: 20, border: '1px solid rgba(47,74,63,.10)', background: i === 0 ? '#DDEAE6' : '#FFFFFF', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
              <div style={{ fontSize: 10, letterSpacing: '.13em', color: '#A69ACD' }}>{d.deeper ? 'DEEPER REFLECTION' : `${d.questions} QUESTIONS · ${d.minutes} MIN`}</div>
              <div style={{ fontSize: 11, color: d.done ? '#2F4A3F' : '#A69ACD', whiteSpace: 'nowrap' }}>{d.done ? 'Done ✓' : 'Explore →'}</div>
            </div>
            <div style={{ marginTop: 7, fontFamily: "'Playfair Display', serif", fontSize: 19, lineHeight: 1.3, color: '#2F4A3F' }}>{d.title}</div>
            <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.5, color: '#5C6B62' }}>{d.note}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
