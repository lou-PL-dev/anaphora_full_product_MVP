export default function Chat({ goHome, messages, turnCount, thinking, draft, onDraft, onDraftKey, sendMessage, readyToComplete, completeConversation, chatEndRef }) {
  const turnDots = [0, 1, 2, 3].map((i) => (i < turnCount ? '#2F4A3F' : 'rgba(47,74,63,.16)'));

  return (
    <div className="ap-screen" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: '#FBF9F6' }}>
      <div style={{ padding: '58px 20px 12px', display: 'flex', alignItems: 'center', gap: 12, borderBottom: '1px solid rgba(47,74,63,.07)' }}>
        <button onClick={goHome} style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid rgba(47,74,63,.12)', background: 'transparent', color: '#2F4A3F', fontSize: 15, cursor: 'pointer', display: 'grid', placeItems: 'center' }}>←</button>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, color: '#2F4A3F' }}>Anaphora</div>
          <div style={{ fontSize: 11, color: '#94A09A', letterSpacing: '.02em' }}>Getting to know who you're looking for</div>
        </div>
        <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
          {turnDots.map((color, i) => (
            <span key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: color }} />
          ))}
        </div>
      </div>

      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '22px 20px 12px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {messages.map((m, i) => (
          <div key={i}>
            {m.role === 'user' ? (
              <div style={{ display: 'flex', justifyContent: 'flex-end', animation: 'apRise .4s ease both' }}>
                <div style={{ maxWidth: '78%', padding: '13px 17px', borderRadius: '20px 20px 5px 20px', background: '#2F4A3F', color: '#F2EDE6', fontSize: 14, lineHeight: 1.55 }}>{m.content}</div>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: 10, animation: 'apRise .45s ease both' }}>
                <div style={{ flex: 'none', width: 26, height: 26, borderRadius: '50%', background: 'linear-gradient(140deg, #A69ACD, #DDEAE6)', marginTop: 3 }} />
                <div style={{ maxWidth: '80%', padding: '13px 17px', borderRadius: '5px 20px 20px 20px', background: '#FFFFFF', border: '1px solid rgba(47,74,63,.07)', color: '#2F4A3F', fontSize: 14, lineHeight: 1.6, boxShadow: '0 2px 10px rgba(47,74,63,.04)' }}>{m.content}</div>
              </div>
            )}
          </div>
        ))}
        {thinking && (
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', animation: 'apFade .3s ease both' }}>
            <div style={{ flex: 'none', width: 26, height: 26, borderRadius: '50%', background: 'linear-gradient(140deg, #A69ACD, #DDEAE6)' }} />
            <div style={{ padding: '14px 18px', borderRadius: '5px 20px 20px 20px', background: '#FFFFFF', border: '1px solid rgba(47,74,63,.07)', display: 'flex', gap: 5 }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#A69ACD', animation: 'apFade 1s ease-in-out infinite alternate' }} />
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#A69ACD', animation: 'apFade 1s ease-in-out .2s infinite alternate' }} />
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#A69ACD', animation: 'apFade 1s ease-in-out .4s infinite alternate' }} />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {readyToComplete && !thinking && (
        <div style={{ padding: '0 20px 10px' }}>
          <button
            onClick={completeConversation}
            style={{ width: '100%', padding: 15, border: 'none', borderRadius: 999, background: 'linear-gradient(100deg, #A69ACD, #8C7FBE)', color: '#FFFFFF', fontSize: 14, fontWeight: 500, cursor: 'pointer', boxShadow: '0 8px 22px rgba(140,127,190,.32)', animation: 'apRise .5s ease both' }}
          >
            Create my Blueprint
          </button>
        </div>
      )}

      <div style={{ padding: '10px 16px 18px', borderTop: '1px solid rgba(47,74,63,.07)', display: 'flex', gap: 10, alignItems: 'flex-end', background: '#FBF9F6' }}>
        <textarea
          value={draft}
          onChange={onDraft}
          onKeyDown={onDraftKey}
          rows={1}
          placeholder="Type your answer…"
          style={{ flex: 1, resize: 'none', padding: '13px 16px', borderRadius: 22, border: '1px solid rgba(47,74,63,.14)', background: '#FFFFFF', fontSize: 14, lineHeight: 1.5, color: '#2F4A3F', maxHeight: 96, outline: 'none' }}
        />
        <button onClick={sendMessage} style={{ flex: 'none', width: 46, height: 46, borderRadius: '50%', border: 'none', background: '#2F4A3F', color: '#F2EDE6', fontSize: 16, cursor: 'pointer', display: 'grid', placeItems: 'center' }}>↑</button>
      </div>
    </div>
  );
}
