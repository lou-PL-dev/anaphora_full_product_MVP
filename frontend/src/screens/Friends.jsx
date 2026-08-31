import { STATIC_FRIENDS } from '../data';

export default function Friends() {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FFFFFF' }}>
      <div style={{ padding: '64px 22px 20px', background: 'linear-gradient(160deg, #F2EDE6, #FFFFFF)' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, lineHeight: 1.2, color: '#2F4A3F' }}>The people who<br />know you best</div>
        <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.6, color: '#5C6B62', maxWidth: 290, textWrap: 'pretty' }}>Three friends have described you. What they see shapes who we look for.</div>
      </div>
      <div style={{ padding: '4px 22px 26px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        {STATIC_FRIENDS.map((f) => (
          <div key={f.name} style={{ padding: '18px 20px', borderRadius: 20, background: '#FFFFFF', border: '1px solid rgba(47,74,63,.08)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
              <span style={{ flex: 'none', width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(140deg, #DDEAE6, #A69ACD)', display: 'grid', placeItems: 'center', fontSize: 12, color: '#2F4A3F' }}>{f.initial}</span>
              <span style={{ flex: 1, fontSize: 13.5, color: '#2F4A3F' }}>{f.name}</span>
              <span style={{ flex: 'none', fontSize: 11, color: '#94A09A' }}>{f.rel}</span>
            </div>
            <div style={{ marginTop: 13, fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: 16, lineHeight: 1.45, color: '#2F4A3F', textWrap: 'pretty' }}>“{f.quote}”</div>
          </div>
        ))}
        <div style={{ padding: 20, borderRadius: 20, background: 'linear-gradient(140deg, rgba(166,154,205,.18), #DDEAE6)' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F' }}>Invite one more</div>
          <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.6, color: '#4A5C53' }}>Two minutes of their time. They answer three questions — you see the answers.</div>
          <button style={{ marginTop: 14, padding: '13px 22px', border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>Share invite link</button>
        </div>
      </div>
    </div>
  );
}
