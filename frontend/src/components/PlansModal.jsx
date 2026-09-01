export default function PlansModal({ closePlans }) {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 30, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', background: 'rgba(166,154,205,.32)', animation: 'apFade .25s ease both' }}>
      <div onClick={closePlans} style={{ flex: 1 }} />
      <div style={{ padding: '26px 24px 30px', borderRadius: '28px 28px 0 0', background: 'linear-gradient(170deg, #FFFFFF, #F2EDE6)', animation: 'apRise .35s cubic-bezier(.2,.8,.2,1) both' }}>
        <div style={{ width: 38, height: 4, borderRadius: 2, background: '#DDEAE6', margin: '0 auto 20px' }} />
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 26, color: '#2F4A3F' }}>Go deeper</div>
        <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>Anaphora works fully on free. Plus is for people who want more of it.</div>
        <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 11 }}>
          <div style={{ padding: '18px 20px', borderRadius: 18, border: '1px solid #DDEAE6', background: '#FFFFFF' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 14, color: '#2F4A3F' }}>Free</span>
              <span style={{ fontSize: 12, color: '#A69ACD' }}>Current</span>
            </div>
            <div style={{ marginTop: 8, fontSize: 12.5, lineHeight: 1.6, color: '#2F4A3F' }}>One conversation, one Discovery, three intros a week.</div>
          </div>
          <div style={{ padding: '18px 20px', borderRadius: 18, border: '1.5px solid #A69ACD', background: 'rgba(166,154,205,.09)' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 14, color: '#2F4A3F' }}>Anaphora+</span>
              <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#2F4A3F' }}>€12<span style={{ fontSize: 12, color: '#A69ACD' }}> / mo</span></span>
            </div>
            <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 7 }}>
              <span style={{ fontSize: 12.5, color: '#2F4A3F' }}>Unlimited Discoveries</span>
              <span style={{ fontSize: 12.5, color: '#2F4A3F' }}>Full intro explanations</span>
              <span style={{ fontSize: 12.5, color: '#2F4A3F' }}>Invite unlimited friends</span>
            </div>
          </div>
        </div>
        <button onClick={closePlans} style={{ marginTop: 20, width: '100%', padding: 17, border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>Try Plus free for 14 days</button>
        <button onClick={closePlans} style={{ marginTop: 10, width: '100%', padding: 12, border: 'none', background: 'transparent', color: '#A69ACD', fontSize: 12.5, cursor: 'pointer' }}>Maybe later</button>
      </div>
    </div>
  );
}
