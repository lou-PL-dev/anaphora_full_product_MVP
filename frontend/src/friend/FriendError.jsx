// Reuses Discovery.jsx's "unavailable" empty-state layout for an invalid,
// used, or unreachable invite link.
export default function FriendError({ message }) {
  return (
    <div className="ap-screen" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: 'linear-gradient(175deg, #FFFFFF, #F2EDE6)' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0 34px', textAlign: 'center' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#2F4A3F' }}>This link isn't available</div>
        <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>{message}</div>
      </div>
    </div>
  );
}
