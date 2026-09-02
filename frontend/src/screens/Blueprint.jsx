import { useEffect, useRef } from 'react';

function cleanBlueprintText(value) {
  return String(value || '')
    .replace(/\s*\(\d+\/100 toward [^)]+\)\s*$/i, '')
    .trim();
}

function userFacingEvidence(value) {
  const cleaned = cleanBlueprintText(value);
  // Internal Discovery evidence such as "roots_freedom: Freedom" is useful
  // in the database/admin view, but not meaningful copy for the member.
  if (/^[a-z0-9_]+:\s/i.test(cleaned)) return '';
  return cleaned;
}

export default function Blueprint({ goHome, groups, signalCount, narrative, scrollToAboutYou, onScrolledAboutYou }) {
  const aboutYouRef = useRef(null);
  useEffect(() => {
    if (!scrollToAboutYou) return;
    aboutYouRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    onScrolledAboutYou?.();
  }, [scrollToAboutYou, onScrolledAboutYou]);

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#FFFFFF' }}>
      <div style={{ flex: 'none', zIndex: 10, padding: '58px 22px 12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, background: 'rgba(255,255,255,.97)', borderBottom: '1px solid #DDEAE6' }}>
        <button onClick={goHome} aria-label="Back to Home" style={{ width: 34, height: 34, borderRadius: '50%', border: '1px solid #DDEAE6', background: '#FFFFFF', color: '#2F4A3F', cursor: 'pointer', fontSize: 17 }}>←</button>
        <div style={{ flex: 1, textAlign: 'center', fontSize: 11, letterSpacing: '.16em', color: '#A69ACD' }}>YOUR BLUEPRINT</div>
        <button onClick={goHome} aria-label="Close Blueprint" style={{ width: 34, height: 34, borderRadius: '50%', border: '1px solid #DDEAE6', background: '#FFFFFF', color: '#2F4A3F', cursor: 'pointer', fontSize: 19, lineHeight: 1 }}>×</button>
      </div>

      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto' }}>
        <div style={{ padding: '22px 22px 18px', background: 'linear-gradient(160deg, #F2EDE6, #FFFFFF)' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 30, lineHeight: 1.2, color: '#2F4A3F' }}>What I understood</div>
        </div>

        {narrative && <div style={{ margin: '4px 22px 22px', padding: '22px 22px 24px', borderRadius: 22, background: '#FFFFFF', border: '1px solid #DDEAE6', boxShadow: '0 8px 26px rgba(166,154,205,.10)' }}><div style={{ fontSize: 10, letterSpacing: '.15em', color: '#A69ACD' }}>YOU, WHO YOU SEEK,<br />AND WHAT YOU WANT TO BUILD</div><div style={{ marginTop: 12, fontFamily: "'Playfair Display', serif", fontSize: 15.5, lineHeight: 1.75, color: '#2F4A3F', whiteSpace: 'pre-wrap' }}>{narrative}</div></div>}

        <div style={{ padding: '4px 22px 28px', display: 'flex', flexDirection: 'column', gap: 22 }}>
          {groups.map((g) => { const isMe = g.side === 'ME'; return <div key={g.title} ref={isMe ? aboutYouRef : null} style={{ padding: isMe ? '17px 16px 4px' : '0', margin: isMe ? '4px -2px 0' : '0', borderRadius: isMe ? 20 : 0, background: isMe ? '#DDEAE6' : 'transparent', border: isMe ? '1px solid #DDEAE6' : 'none' }}><div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, paddingBottom: 10, borderBottom: '1px solid #DDEAE6' }}><span style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F' }}>{g.title}</span><span style={{ padding: '4px 8px', borderRadius: 999, fontSize: 9.5, letterSpacing: '.08em', color: isMe ? '#2F4A3F' : '#A69ACD', background: isMe ? '#F2EDE6' : 'rgba(166,154,205,.13)', whiteSpace: 'nowrap' }}>{g.side}</span></div><div style={{ display: 'flex', flexDirection: 'column' }}>{g.items.map((s) => { const label = cleanBlueprintText(s.label); const evidence = userFacingEvidence(s.evidence); return <button key={s.id} onClick={s.onEdit} style={{ width: '100%', textAlign: 'left', display: 'flex', gap: 12, alignItems: 'flex-start', padding: '14px 4px', border: 'none', borderBottom: '1px solid #DDEAE6', background: 'transparent', cursor: 'pointer' }}><span style={{ flex: 'none', marginTop: 6, width: 7, height: 7, borderRadius: '50%', background: s.dot }} /><span style={{ flex: 1 }}><span style={{ display: 'block', fontSize: 14.5, color: '#2F4A3F', lineHeight: 1.4 }}>{label}</span>{evidence && <span style={{ display: 'block', marginTop: 5, fontSize: 12, color: '#A69ACD', fontStyle: 'italic', lineHeight: 1.5 }}>“{evidence}”</span>}</span><span style={{ flex: 'none', marginTop: 3, padding: '4px 9px', borderRadius: 999, background: s.pillBg, color: s.pillFg, fontSize: 10, letterSpacing: '.04em', whiteSpace: 'nowrap' }}>{s.strengthLabel}</span></button>; })}</div></div>; })}
          <div style={{ padding: 20, borderRadius: 20, background: '#DDEAE6' }}><div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F', lineHeight: 1.35 }}>This grows with you</div><div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>Every conversation, Discovery and friend contribution refines it. Nothing here is fixed.</div></div>
        </div>
      </div>

      <div style={{ flex: 'none', zIndex: 10, padding: '12px 22px 24px', background: 'rgba(255,255,255,.97)', borderTop: '1px solid #DDEAE6', boxShadow: '0 -8px 24px rgba(47,74,63,.06)' }}>
        <div style={{ marginBottom: 12, textAlign: 'center', fontSize: 12.5, lineHeight: 1.45, color: '#2F4A3F' }}>
          <div>{signalCount} signals, drawn from your own words.</div>
          <div style={{ color: '#A69ACD' }}>Tap to change what isn't quite right.</div>
        </div>
        <button onClick={goHome} style={{ width: '100%', padding: '15px 22px', border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 14, fontWeight: 500, cursor: 'pointer' }}>Looks good! Explore Anaphora →</button>
      </div>
    </div>
  );
}
