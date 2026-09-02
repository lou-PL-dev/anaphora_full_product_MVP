// Reuses Welcome.jsx's exact background/blob decorations/logo/typography —
// the friend's very first screen deserves the same brand moment as the
// user's, just with different copy (PRD section 18).
export default function FriendLanding({ friendName, onFriendName, onContinue, canContinue }) {
  return (
    <div className="ap-screen" style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '42px 32px 44px', background: 'linear-gradient(170deg, #F2EDE6 0%, #FFFFFF 48%, #DDEAE6 100%)' }}>
      <div style={{ position: 'absolute', top: -70, right: -90, width: 300, height: 280, borderRadius: '58% 42% 47% 53% / 52% 46% 54% 48%', background: 'linear-gradient(140deg, rgba(166,154,205,.5), rgba(221,234,230,.5))', filter: 'blur(2px)', animation: 'apBreathe 14s ease-in-out infinite' }} />
      <div style={{ position: 'absolute', top: 130, left: -80, width: 210, height: 200, borderRadius: '44% 56% 60% 40% / 48% 52% 48% 52%', background: '#DDEAE6', animation: 'apBreathe 18s ease-in-out infinite reverse' }} />
      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 6 }}>
          <img src="/brand/anaphora-mark.png" alt="Anaphora" style={{ width: 96, height: 'auto', display: 'block', objectFit: 'contain' }} />
        </div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 30, lineHeight: 1.25, color: '#2F4A3F' }}>
          A friend trusts your judgment <span style={{ fontStyle: 'italic', color: '#A69ACD' }}>❤</span>
        </div>
        <div style={{ marginTop: 14, fontSize: 14, lineHeight: 1.6, color: '#2F4A3F', maxWidth: 300, textWrap: 'pretty' }}>
          They've asked you to help Anaphora understand who might genuinely suit them. This takes about 5 minutes.
        </div>
        <div style={{ marginTop: 16, padding: '14px 16px', borderRadius: 16, background: 'rgba(255,255,255,.6)', border: '1px solid #DDEAE6', fontSize: 12.5, lineHeight: 1.6, color: '#2F4A3F' }}>
          Your individual answers are private. They will not see what you wrote — Anaphora uses your answers to identify broader themes that may help with matchmaking.
        </div>
        <input
          value={friendName}
          onChange={onFriendName}
          placeholder="Your first name"
          style={{ marginTop: 18, width: '100%', boxSizing: 'border-box', padding: '15px 17px', borderRadius: 16, border: '1.5px solid #DDEAE6', background: '#FFFFFF', color: '#2F4A3F', fontFamily: "'Inter', sans-serif", fontSize: 14, outline: 'none' }}
        />
        <button
          onClick={onContinue}
          disabled={!canContinue}
          style={{ marginTop: 14, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: canContinue ? '#2F4A3F' : '#F2EDE6', color: canContinue ? '#FFFFFF' : '#2F4A3F', fontSize: 15, fontWeight: 500, letterSpacing: '.01em', cursor: canContinue ? 'pointer' : 'default', boxShadow: canContinue ? '0 10px 26px rgba(166,154,205,.24)' : 'none' }}
        >
          I agree — continue
        </button>
      </div>
    </div>
  );
}
