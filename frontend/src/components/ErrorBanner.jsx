// A real failure, surfaced plainly — never silently swapped for fabricated
// content. `onRetry` is only passed where there's no other visible control
// that already retries the same action (e.g. the send/submit button).
export default function ErrorBanner({ message, onRetry }) {
  if (!message) return null;
  return (
    <div style={{ margin: '0 20px 10px', padding: '11px 14px', borderRadius: 14, background: 'rgba(176,74,58,.08)', border: '1px solid rgba(176,74,58,.28)', display: 'flex', alignItems: 'center', gap: 10, animation: 'apRise .3s ease both' }}>
      <span style={{ flex: 1, fontSize: 12.5, lineHeight: 1.5, color: '#8C3A2A' }}>{message}</span>
      {onRetry && (
        <button onClick={onRetry} style={{ flex: 'none', padding: '7px 13px', borderRadius: 999, border: '1px solid rgba(176,74,58,.35)', background: '#FFFFFF', color: '#8C3A2A', fontSize: 11.5, cursor: 'pointer' }}>
          Retry
        </button>
      )}
    </div>
  );
}
