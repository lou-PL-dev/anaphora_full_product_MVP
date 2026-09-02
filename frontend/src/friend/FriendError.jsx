// Reuses Discovery.jsx's "unavailable" empty-state layout for an invalid,
// used, or unreachable invite link. A friend-flow token in the URL has no
// client-side way to clear itself, so this is otherwise a dead end —
// always offer a way back to the regular app.
export default function FriendError({ message }) {
  const goApp = () => { window.location.href = window.location.origin; };
  return (
    <div className="ap-screen" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: 'linear-gradient(175deg, #FFFFFF, #F2EDE6)' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0 34px', textAlign: 'center' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#2F4A3F' }}>This link isn't available</div>
        <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>{message}</div>
        <button onClick={goApp} style={{ marginTop: 22, padding: '12px 22px', border: '1px solid #DDEAE6', borderRadius: 999, background: 'transparent', color: '#2F4A3F', fontSize: 13, cursor: 'pointer' }}>Go to Anaphora</button>
      </div>
    </div>
  );
}
