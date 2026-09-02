export default function Friends({ invites, openFriendReview, openInvite, inviteCount, inviteLimit }) {
  const atLimit = inviteCount >= inviteLimit;
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#F2EDE6' }}>
      <div style={{ padding: '64px 22px 20px', background: 'linear-gradient(160deg, #F2EDE6, #FFFFFF)' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, lineHeight: 1.2, color: '#2F4A3F' }}>The people who<br />know you best</div>
        <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F', maxWidth: 290, textWrap: 'pretty' }}>What they see shapes who we look for.</div>
      </div>
      <div style={{ padding: '24px 22px 26px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        {invites.map((inv) => {
          const answered = inv.status === 'answered';
          const statusLabel = !answered ? 'Waiting' : inv.reviewed ? 'Reviewed ✓' : 'Ready to review';
          return (
            <button
              key={inv.id}
              onClick={answered ? () => openFriendReview(inv.id) : undefined}
              style={{ width: '100%', textAlign: 'left', padding: '18px 20px', borderRadius: 20, background: '#FFFFFF', border: '1px solid #DDEAE6', cursor: answered ? 'pointer' : 'default' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
                <span style={{ flex: 'none', width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(140deg, rgba(166,154,205,.35), #FFFFFF)', display: 'grid', placeItems: 'center', fontSize: 12, color: '#2F4A3F' }}>{(inv.friend_name || '?').charAt(0).toUpperCase()}</span>
                <span style={{ flex: 1, fontSize: 13.5, color: '#2F4A3F' }}>{inv.friend_name || 'Invited friend'}</span>
                <span style={{ flex: 'none', fontSize: 11, color: '#A69ACD' }}>{statusLabel}</span>
              </div>
              {answered && !inv.reviewed && (
                <div style={{ marginTop: 13, fontSize: 12.5, lineHeight: 1.5, color: '#2F4A3F' }}>They've answered — tap to see what Anaphora noticed.</div>
              )}
              {!answered && (
                <div style={{ marginTop: 13, fontSize: 12.5, lineHeight: 1.5, color: '#2F4A3F' }}>Their individual answers stay private, even from you.</div>
              )}
            </button>
          );
        })}

        <div style={{ padding: 20, borderRadius: 20, background: 'linear-gradient(145deg, #FFFFFF 0%, rgba(166,154,205,.14) 100%)', border: '1px solid rgba(166,154,205,.32)' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F' }}>{invites.length ? 'Invite one more' : 'Invite someone who knows you'}</div>
          <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.6, color: '#2F4A3F' }}>
            {atLimit ? `You've used all ${inviteLimit} invitations on the free plan.` : 'A couple of minutes of their time. Their individual answers stay private, even from you.'}
          </div>
          <button
            onClick={openInvite}
            disabled={atLimit}
            style={{ marginTop: 14, padding: '13px 22px', border: 'none', borderRadius: 999, background: atLimit ? '#DDEAE6' : '#2F4A3F', color: atLimit ? '#2F4A3F' : '#F2EDE6', fontSize: 13, fontWeight: 500, cursor: atLimit ? 'default' : 'pointer' }}
          >
            Share invite link
          </button>
        </div>
      </div>
    </div>
  );
}
