// Static stand-in for the prototype's <image-slot> (a Claude Design editor
// component with no equivalent outside that tool). Matches/Friends portraits
// are frontend-only per the PRD — this just renders the placeholder chrome;
// swap `src` in for a real photo URL once match photos exist.
export default function PortraitSlot({ src, label, style }) {
  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2F4A3F', ...style }}>
      {src ? (
        <img src={src} alt={label || ''} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      ) : (
        <span style={{ fontSize: 11, letterSpacing: '.04em', opacity: 0.65, textAlign: 'center', padding: '0 12px' }}>{label}</span>
      )}
    </div>
  );
}
