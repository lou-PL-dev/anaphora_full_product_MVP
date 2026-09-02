import ErrorBanner from '../components/ErrorBanner';

// Reuses Blueprint.jsx's exact header/narrative-card/item-row structure,
// and Chat.jsx's "Add to my Blueprint" CTA styling verbatim — nothing from
// a friend ever reaches the Blueprint until the user explicitly commits it
// here (PRD section 21).
export default function FriendReview({ goBack, friendName, narrative, signals, selectedIds, onToggleSignal, onCommit, committing, error, committed, addedCount, loading }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', display: 'flex', flexDirection: 'column', background: '#FFFFFF' }}>
      <div style={{ padding: '62px 22px 18px', background: 'linear-gradient(160deg, #F2EDE6, #FFFFFF)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button onClick={goBack} style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid #DDEAE6', background: 'transparent', color: '#2F4A3F', cursor: 'pointer' }}>←</button>
          <div style={{ fontSize: 11, letterSpacing: '.16em', color: '#A69ACD' }}>FRIEND'S PERSPECTIVE</div>
        </div>
        <div style={{ marginTop: 14, fontFamily: "'Playfair Display', serif", fontSize: 27, lineHeight: 1.25, color: '#2F4A3F' }}>What {friendName ? `${friendName} sees` : 'they see'}</div>
        <div style={{ marginTop: 12, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>Their exact words stay private — only these themes reached you. Pick what to add.</div>
      </div>

      {loading && <div style={{ padding: '20px 22px', fontSize: 13, color: '#A69ACD' }}>Loading…</div>}

      {narrative && (
        <div style={{ margin: '4px 22px 22px', padding: '22px 22px 24px', borderRadius: 22, background: '#FFFFFF', border: '1px solid #DDEAE6', boxShadow: '0 8px 26px rgba(166,154,205,.10)' }}>
          <div style={{ fontSize: 10, letterSpacing: '.15em', color: '#A69ACD' }}>WHAT {(friendName || 'THEY').toUpperCase()} SHARED</div>
          <div style={{ marginTop: 12, fontFamily: "'Playfair Display', serif", fontSize: 15.5, lineHeight: 1.75, color: '#2F4A3F', whiteSpace: 'pre-wrap' }}>{narrative}</div>
        </div>
      )}

      <div style={{ flex: 1, padding: '4px 22px 24px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {signals.map((sig) => {
          const selected = selectedIds.includes(sig.id);
          return (
            <button
              key={sig.id}
              onClick={() => onToggleSignal(sig.id)}
              disabled={committed}
              style={{ width: '100%', textAlign: 'left', display: 'flex', gap: 12, alignItems: 'flex-start', padding: '15px 16px', borderRadius: 18, border: `1.5px solid ${selected ? '#A69ACD' : '#DDEAE6'}`, background: selected ? 'rgba(166,154,205,.1)' : '#FFFFFF', cursor: committed ? 'default' : 'pointer' }}
            >
              <span style={{ flex: 'none', marginTop: 4, width: 16, height: 16, borderRadius: '50%', border: `1.5px solid ${selected ? '#A69ACD' : '#DDEAE6'}`, background: selected ? '#A69ACD' : 'transparent', display: 'grid', placeItems: 'center', color: '#FFFFFF', fontSize: 10 }}>{selected ? '✓' : ''}</span>
              <span style={{ flex: 1 }}>
                <span style={{ display: 'block', fontSize: 14.5, color: '#2F4A3F', lineHeight: 1.4 }}>{sig.label}</span>
                {sig.evidence_text && <span style={{ display: 'block', marginTop: 5, fontSize: 12, color: '#A69ACD', fontStyle: 'italic', lineHeight: 1.5 }}>“{sig.evidence_text}”</span>}
              </span>
              <span style={{ flex: 'none', marginTop: 3, padding: '4px 9px', borderRadius: 999, background: '#F2EDE6', color: '#2F4A3F', fontSize: 10, letterSpacing: '.04em', whiteSpace: 'nowrap' }}>{sig.perspective === 'ME' ? 'ABOUT YOU' : 'IDEAL PARTNER'}</span>
            </button>
          );
        })}
      </div>

      <ErrorBanner message={error} />
      <div style={{ padding: '12px 22px 26px' }}>
        {committed ? (
          <div style={{ textAlign: 'center', fontSize: 13, color: '#2F4A3F' }}>{addedCount} signal{addedCount === 1 ? '' : 's'} added to your Blueprint ✓</div>
        ) : (
          <button disabled={committing || loading} onClick={onCommit} style={{ width: '100%', padding: 15, border: 'none', borderRadius: 999, background: '#A69ACD', color: '#FFFFFF', fontSize: 14, fontWeight: 500, cursor: committing ? 'default' : 'pointer', boxShadow: '0 8px 22px rgba(166,154,205,.28)' }}>
            {committing ? 'Adding…' : 'Add to my Blueprint'}
          </button>
        )}
      </div>
    </div>
  );
}
