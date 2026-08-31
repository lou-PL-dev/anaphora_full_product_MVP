import PortraitSlot from '../components/PortraitSlot';
import ErrorBanner from '../components/ErrorBanner';

// Real RAG-matched candidates (see anaphora_backend/app/chains/matching_chain.py)
// — a synthetic pool, not real users (see rag_demo/ingest_candidates.py).
// No numeric score is ever shown (PRD §26, Match Presentation: "Anaphora
// deliberately avoids presenting 92% compatible") — just a fit label and
// the genuine, grounded reasons behind it. A candidate with nothing
// genuine to say never reaches this screen at all (see matching_chain's
// has_genuine_match filter) — there's no generic fallback text here.
function initials(name) {
  return (name || '?').trim().split(/\s+/).map((w) => w[0]).slice(0, 2).join('').toUpperCase();
}

const FIT_LABEL = { strong_fit: 'Strong fit', worth_exploring: 'Worth exploring' };

function MatchCard({ match, primary }) {
  const { candidate, fit, sections } = match;
  const shownSections = primary ? sections : sections.slice(0, 1);

  return (
    <div style={{ padding: primary ? 18 : 14, borderRadius: primary ? 24 : 20, background: '#FFFFFF', border: '1px solid rgba(47,74,63,.08)', boxShadow: primary ? '0 8px 26px rgba(47,74,63,.06)' : 'none' }}>
      <div style={{ position: 'relative', height: primary ? 300 : 130 }}>
        <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', borderRadius: '56% 44% 48% 52% / 46% 50% 50% 54%', background: 'linear-gradient(140deg, rgba(166,154,205,.35), rgba(221,234,230,.6))' }}>
          <PortraitSlot src={candidate.photo_url || undefined} label={initials(candidate.name)} />
        </div>
        <div style={{ position: 'absolute', top: 12, right: 6, padding: '8px 14px', borderRadius: 999, background: 'rgba(166,154,205,.95)', color: '#FFFFFF', fontSize: 12, fontWeight: 500, pointerEvents: 'none' }}>{FIT_LABEL[fit] || FIT_LABEL.worth_exploring}</div>
      </div>
      <div style={{ marginTop: primary ? 16 : 12, display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: primary ? 26 : 17, color: '#2F4A3F' }}>{candidate.name}</div>
        {primary && <div style={{ fontSize: 13, color: '#94A09A' }}>{candidate.age}</div>}
      </div>
      {!primary && <div style={{ marginTop: 2, fontSize: 11, color: '#94A09A' }}>{candidate.age}</div>}

      {primary && (
        <div style={{ marginTop: 16, padding: 18, borderRadius: 18, background: '#F6F4FA' }}>
          <div style={{ fontSize: 10, letterSpacing: '.14em', color: '#8C7FBE' }}>WHY ANAPHORA THINKS YOU SHOULD MEET</div>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 14 }}>
            {shownSections.map((sec) => (
              <div key={sec.heading}>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#2F4A3F' }}>{sec.heading}</div>
                <div style={{ marginTop: 4, fontSize: 13, lineHeight: 1.6, color: '#4A5C53' }}>{sec.body}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid rgba(47,74,63,.08)', fontSize: 11.5, color: '#94A09A' }}>Explainable AI — we show you why, not just who.</div>
        </div>
      )}
      {!primary && shownSections.map((sec) => (
        <div key={sec.heading} style={{ marginTop: 10, fontSize: 12, lineHeight: 1.5, color: '#5C6B62' }}>{sec.body}</div>
      ))}

      {primary && (
        <div style={{ marginTop: 14, display: 'flex', gap: 10 }}>
          <button style={{ flex: 1, padding: 15, borderRadius: 999, border: '1px solid rgba(47,74,63,.14)', background: 'transparent', color: '#5C6B62', fontSize: 13.5, cursor: 'pointer' }}>Not now</button>
          <button style={{ flex: 2, padding: 15, border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 13.5, fontWeight: 500, cursor: 'pointer' }}>Say hello</button>
        </div>
      )}
    </div>
  );
}

export default function Matches({ matches, loading, ready, error, onRetry, goHome }) {
  const [primaryMatch, ...secondaryMatches] = matches;
  const notReady = ready === false;

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FBF9F6' }}>
      <div style={{ padding: '64px 22px 6px', display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>Matches</div>
          <div style={{ marginTop: 6, fontSize: 12.5, color: '#94A09A' }}>
            {matches.length ? "We don't believe in perfect matches. We believe in meaningful fit." : 'Quality over volume.'}
          </div>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={onRetry} />

      <div style={{ padding: '18px 22px 26px', display: 'flex', flexDirection: 'column', gap: 18 }}>
        {loading && (
          <div style={{ padding: 30, textAlign: 'center', fontSize: 13, color: '#94A09A' }}>Finding your matches…</div>
        )}

        {!loading && notReady && !error && (
          <div style={{ padding: 24, borderRadius: 20, background: '#DDEAE6', textAlign: 'center' }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, color: '#2F4A3F' }}>A good introduction starts with understanding.</div>
            <div style={{ marginTop: 8, fontSize: 12.5, lineHeight: 1.6, color: '#4A5C53' }}>Before Anaphora can start looking for your matches, there are a few things we still need to understand about you, who you're looking for, and the kind of relationship you want to build.</div>
            <button onClick={goHome} style={{ marginTop: 16, padding: '11px 20px', border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 13, cursor: 'pointer' }}>See what Anaphora still needs</button>
          </div>
        )}

        {!loading && ready === true && matches.length === 0 && !error && (
          <div style={{ padding: 20, borderRadius: 20, background: '#DDEAE6', textAlign: 'center' }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, color: '#2F4A3F' }}>We're still curating profiles for you</div>
            <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.6, color: '#4A5C53' }}>Good matches take a little patience — we'd rather wait for someone worth meeting than show you someone who isn't. Check back soon.</div>
          </div>
        )}

        {primaryMatch && <MatchCard match={primaryMatch} primary />}

        {secondaryMatches.length > 0 && (
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
            {secondaryMatches.map((m) => (
              <div key={m.candidate.id} style={{ flex: '1 1 45%', minWidth: 130 }}>
                <MatchCard match={m} />
              </div>
            ))}
          </div>
        )}

        {matches.length > 0 && (
          <div style={{ padding: 20, borderRadius: 20, background: '#DDEAE6', textAlign: 'center' }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, color: '#2F4A3F' }}>That's all for now</div>
            <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.6, color: '#4A5C53' }}>We'd rather show you a few people who make sense than hundreds who don't.</div>
          </div>
        )}
      </div>
    </div>
  );
}
