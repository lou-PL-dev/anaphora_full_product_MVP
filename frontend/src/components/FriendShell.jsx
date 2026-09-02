// Same mobile-web shell as PhoneFrame (identical background/sizing/colors)
// but without its developer-only toolbar (mode indicator, Device frame,
// Start over) — a friend opening an invite link should see a clean,
// branded mobile page, not internal demo controls.
//
// A ?f=<token> URL has no client-side way to clear itself, so every step
// of this flow (not just the error/done ends) needs a way back to the
// regular app — put it once here, in the shared shell, rather than on
// each individual screen (easy to miss one, as happened before).
export default function FriendShell({ children }) {
  const goApp = () => { window.location.href = window.location.origin; };
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(120% 90% at 20% 0%, #FFFFFF 0%, #F2EDE6 55%, #DDEAE6 100%)', fontFamily: 'Inter, system-ui, sans-serif', padding: 0 }}>
      <div style={{ position: 'relative', width: '100%', maxWidth: 430, height: '100vh' }}>
        <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', background: '#FFFFFF' }}>
          <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', background: '#FFFFFF' }}>
            {children}
          </div>
          <button
            onClick={goApp}
            style={{ position: 'absolute', top: 14, right: 14, zIndex: 50, padding: '7px 12px', borderRadius: 999, border: '1px solid #DDEAE6', background: 'rgba(255,255,255,.78)', color: '#A69ACD', fontSize: 10.5, letterSpacing: '.02em', cursor: 'pointer', backdropFilter: 'blur(8px)' }}
          >
            Not for you?
          </button>
        </div>
      </div>
    </div>
  );
}
