// Same mobile-web shell as PhoneFrame (identical background/sizing/colors)
// but without its developer-only toolbar (mode indicator, Device frame,
// Start over) — a friend opening an invite link should see a clean,
// branded mobile page, not internal demo controls.
export default function FriendShell({ children }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(120% 90% at 20% 0%, #FFFFFF 0%, #F2EDE6 55%, #DDEAE6 100%)', fontFamily: 'Inter, system-ui, sans-serif', padding: 0 }}>
      <div style={{ position: 'relative', width: '100%', maxWidth: 430, height: '100vh' }}>
        <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', background: '#FFFFFF' }}>
          <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', background: '#FFFFFF' }}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
