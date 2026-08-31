import { useRef } from 'react';
import { useSpeechToText } from '../useSpeechToText';
import ErrorBanner from '../components/ErrorBanner';

export default function Chat({ goHome, messages, thinking, draft, onDraft, onDraftKey, sendMessage, readyToComplete, completeConversation, chatEndRef, setDraft, error, onRetryStart }) {
  const baseDraftRef = useRef('');
  const { listening, supported: voiceSupported, toggle: toggleVoice, stop: stopVoice } = useSpeechToText({
    onTranscript: (transcript) => {
      const base = baseDraftRef.current;
      setDraft(base ? base + ' ' + transcript : transcript);
    },
  });
  const handleMicClick = () => {
    if (!listening) baseDraftRef.current = draft.trim();
    toggleVoice();
  };
  const handleSend = () => {
    if (listening) stopVoice();
    sendMessage();
  };
  const handleDraftKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && listening) stopVoice();
    onDraftKey(e);
  };

  return (
    <div className="ap-screen" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: '#FBF9F6' }}>
      <div style={{ padding: '58px 20px 12px', display: 'flex', alignItems: 'center', gap: 12, borderBottom: '1px solid rgba(47,74,63,.07)' }}>
        <button onClick={goHome} style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid rgba(47,74,63,.12)', background: 'transparent', color: '#2F4A3F', fontSize: 15, cursor: 'pointer', display: 'grid', placeItems: 'center' }}>←</button>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, color: '#2F4A3F' }}>Anaphora</div>
          <div style={{ fontSize: 11, color: '#94A09A', letterSpacing: '.02em' }}>Getting to know who you're looking for</div>
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
            <div style={{ padding: '14px 18px', borderRadius: '5px 20px 20px 20px', background: '#FFFFFF', border: '1px solid rgba(47,74,63,.07)', color: '#94A09A', fontSize: 12 }}>Thinking…</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {readyToComplete && !thinking && (
        <div style={{ padding: '0 20px 10px' }}>
          <button onClick={completeConversation} style={{ width: '100%', padding: 15, border: 'none', borderRadius: 999, background: 'linear-gradient(100deg, #A69ACD, #8C7FBE)', color: '#FFFFFF', fontSize: 14, fontWeight: 500, cursor: 'pointer', boxShadow: '0 8px 22px rgba(140,127,190,.32)', animation: 'apRise .5s ease both' }}>Create my Blueprint</button>
        </div>
      )}

      <ErrorBanner message={error} onRetry={onRetryStart} />

      <div style={{ padding: '10px 16px 18px', borderTop: '1px solid rgba(47,74,63,.07)', display: 'flex', gap: 10, alignItems: 'flex-end', background: '#FBF9F6' }}>
        <textarea value={draft} onChange={onDraft} onKeyDown={handleDraftKey} rows={1} placeholder={listening ? 'Listening…' : 'Type your answer…'} style={{ flex: 1, resize: 'none', padding: '13px 16px', borderRadius: 22, border: `1px solid ${listening ? '#A69ACD' : 'rgba(47,74,63,.14)'}`, background: '#FFFFFF', fontSize: 14, lineHeight: 1.5, color: '#2F4A3F', maxHeight: 96, outline: 'none', transition: 'border-color .2s' }} />
        {voiceSupported && (
          <button onClick={handleMicClick} title={listening ? 'Stop dictation' : 'Describe it out loud'} style={{ flex: 'none', width: 46, height: 46, borderRadius: '50%', border: listening ? 'none' : '1px solid rgba(47,74,63,.14)', background: listening ? '#A69ACD' : '#FFFFFF', color: listening ? '#FFFFFF' : '#5C6B62', cursor: 'pointer', display: 'grid', placeItems: 'center', animation: listening ? 'apPulse 1.4s ease-out infinite' : 'none' }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 18, height: 18 }}>
              <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z" />
              <path d="M19 11a7 7 0 0 1-14 0" />
              <line x1="12" y1="19" x2="12" y2="22" />
            </svg>
          </button>
        )}
        <button onClick={handleSend} style={{ flex: 'none', width: 46, height: 46, borderRadius: '50%', border: 'none', background: '#2F4A3F', color: '#F2EDE6', fontSize: 16, cursor: 'pointer', display: 'grid', placeItems: 'center' }}>↑</button>
      </div>
    </div>
  );
}
