export default function Convos({ convoStatus, convoCta, resumeConversation, discoveries, startDiscovery }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FFFFFF', padding: '64px 22px 24px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>Conversations</div>
      <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.6, color: '#5C6B62' }}>Anaphora only learns what you choose to tell it.</div>

      <button onClick={resumeConversation} style={{ marginTop: 22, width: '100%', textAlign: 'left', padding: 20, borderRadius: 20, border: '1px solid rgba(47,74,63,.1)', background: '#FFFFFF', cursor: 'pointer' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ flex: 'none', width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(140deg, #A69ACD, #DDEAE6)' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 14, color: '#2F4A3F' }}>The person you'd love to meet</div>
            <div style={{ marginTop: 3, fontSize: 11.5, color: '#94A09A' }}>{convoStatus}</div>
          </div>
          <div style={{ fontSize: 12, color: '#A69ACD' }}>{convoCta}</div>
        </div>
      </button>

      <div style={{ marginTop: 14, padding: 20, borderRadius: 20, background: '#F2EDE6' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, color: '#2F4A3F' }}>Tell me more</div>
        <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.6, color: '#5C6B62' }}>Something changed, or you thought of something new? Add to it any time — your Blueprint updates.</div>
      </div>

      <div style={{ marginTop: 28, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>DISCOVERIES</div>
        <div style={{ fontSize: 11, color: '#94A09A' }}>Choose what feels useful</div>
      </div>

      <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 10 }}>
        {discoveries.map((d, i) => (
          <button
            key={d.id}
            onClick={() => startDiscovery(d.id, 'convos')}
            style={{ width: '100%', textAlign: 'left', padding: 18, borderRadius: 20, border: '1px solid rgba(47,74,63,.07)', background: i % 3 === 0 ? '#DDEAE6' : (i % 3 === 1 ? '#F2EDE6' : 'rgba(166,154,205,.12)'), cursor: 'pointer' }}
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
