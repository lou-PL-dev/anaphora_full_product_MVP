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
              backgroundPosition: 'center 30%',
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
              width: '84%',
              height: '96%',
              objectFit: 'cover',
              objectPosition: 'center 28%',
              borderRadius: '44% 56% 50% 50% / 48% 48% 52% 52%',
            }}
          />
        </>
      ) : (
        <span style={{ fontSize: 11, letterSpacing: '.04em', opacity: 0.65, textAlign: 'center', padding: '0 12px' }}>{label}</span>
      )}
    </div>
  );
}
