export default function InviteLinkSheet({ closeInvite, copyInvite, inviteLink, copied, creating, error }) {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 30, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', background: 'rgba(166,154,205,.32)', animation: 'apFade .25s ease both' }}>
      <div onClick={closeInvite} style={{ flex: 1 }} />
      <div style={{ padding: '26px 24px 30px', borderRadius: '28px 28px 0 0', background: '#FFFFFF', animation: 'apRise .35s cubic-bezier(.2,.8,.2,1) both' }}>
        <div style={{ width: 38, height: 4, borderRadius: 2, background: '#DDEAE6', margin: '0 auto 20px' }} />
        <div style={{ fontSize: 10, letterSpacing: '.14em', color: '#A69ACD' }}>YOUR INVITE LINK</div>
        <div style={{ marginTop: 12, fontFamily: "'Playfair Display', serif", fontSize: 24, lineHeight: 1.3, color: '#2F4A3F' }}>Send this to one person who knows you well</div>
        <div style={{ marginTop: 10, fontSize: 12.5, lineHeight: 1.6, color: '#2F4A3F' }}>This link is for one friend only — no account needed. Once they respond, it stops working. Inviting someone else? Come back here for their own link.</div>
        {error ? (
          <div style={{ marginTop: 18, padding: '14px 16px', borderRadius: 16, background: '#F2EDE6', fontSize: 12.5, color: '#2F4A3F' }}>{error}</div>
        ) : (
          <div style={{ marginTop: 18, display: 'flex', alignItems: 'center', gap: 10, padding: '14px 16px', borderRadius: 16, border: '1px dashed rgba(47,74,63,.22)', background: '#FFFFFF' }}>
            <span style={{ flex: 1, fontSize: 13.5, color: creating ? '#A69ACD' : '#2F4A3F', wordBreak: 'break-all' }}>{creating ? 'Generating your link…' : inviteLink}</span>
          </div>
        )}
        <button onClick={copyInvite} disabled={creating || !!error || !inviteLink} style={{ marginTop: 12, width: '100%', padding: 16, border: 'none', borderRadius: 999, background: (creating || !!error || !inviteLink) ? '#F2EDE6' : '#2F4A3F', color: (creating || !!error || !inviteLink) ? '#2F4A3F' : '#F2EDE6', fontSize: 14.5, fontWeight: 500, cursor: (creating || !!error || !inviteLink) ? 'default' : 'pointer', transition: 'background .3s' }}>{copied ? 'Copied' : 'Copy link'}</button>
        <button onClick={closeInvite} style={{ marginTop: 10, width: '100%', padding: 12, border: 'none', background: 'transparent', color: '#A69ACD', fontSize: 12.5, cursor: 'pointer' }}>Done</button>
      </div>
    </div>
  );
}
