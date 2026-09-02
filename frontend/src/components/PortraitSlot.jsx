// Static stand-in for the prototype's <image-slot> (a Claude Design editor
// component with no equivalent outside that tool). Matches/Friends portraits
// are frontend-only per the PRD — this renders photos inside the existing
// organic frame without aggressively cropping portrait-oriented images.
export default function PortraitSlot({ src, label, style }) {
  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', color: '#2F4A3F', ...style }}>
      {src ? (
        <>
          <div
            aria-hidden="true"
            style={{
              position: 'absolute',
              inset: -18,
              backgroundImage: `url(${src})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              filter: 'blur(18px)',
              opacity: 0.28,
              transform: 'scale(1.08)',
            }}
          />
          <img
            src={src}
            alt={label || ''}
            style={{
              position: 'relative',
              zIndex: 1,
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              objectPosition: 'center',
            }}
          />
        </>
      ) : (
        <span style={{ fontSize: 11, letterSpacing: '.04em', opacity: 0.65, textAlign: 'center', padding: '0 12px' }}>{label}</span>
      )}
    </div>
  );
}
