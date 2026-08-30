export default function Convos({ convoStatus, convoCta, resumeConversation, discoveryState, startDiscovery }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FBF9F6', padding: '64px 22px 24px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>Conversations</div>
      <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.6, color: '#5C6B62' }}>Anaphora only learns what you choose to tell it.</div>
      <button
        onClick={resumeConversation}
        style={{ marginTop: 22, width: '100%', textAlign: 'left', padding: 20, borderRadius: 20, border: '1px solid rgba(47,74,63,.1)', background: '#FFFFFF', cursor: 'pointer' }}
      >
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
      <div style={{ marginTop: 26, fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>DISCOVERIES</div>
      <button
        onClick={startDiscovery}
        style={{ marginTop: 10, width: '100%', textAlign: 'left', padding: 20, borderRadius: 20, border: 'none', background: 'linear-gradient(140deg, #EFECF7, #DDEAE6)', cursor: 'pointer' }}
      >
        <div style={{ fontSize: 10, letterSpacing: '.14em', color: '#8C7FBE' }}>4 QUESTIONS · 2 MIN</div>
        <div style={{ marginTop: 8, fontFamily: "'Playfair Display', serif", fontSize: 20, lineHeight: 1.3, color: '#2F4A3F' }}>What kind of life are you building?</div>
        <div style={{ marginTop: 10, fontSize: 12.5, color: '#4A5C53' }}>{discoveryState}</div>
      </button>
    </div>
  );
}
