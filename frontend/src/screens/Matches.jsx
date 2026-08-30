import PortraitSlot from '../components/PortraitSlot';
import { STATIC_MATCHES } from '../data';

export default function Matches({ whyOpen, toggleWhy }) {
  const { primary, secondary, whyItems } = STATIC_MATCHES;
  const whyLabel = whyOpen ? 'Hide the reasoning' : 'Why this match?';

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FBF9F6' }}>
      <div style={{ padding: '64px 22px 6px', display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: '#2F4A3F' }}>Matches</div>
          <div style={{ marginTop: 6, fontSize: 12.5, color: '#94A09A' }}>Two new this week. Quality over volume.</div>
        </div>
        <button style={{ padding: '8px 12px', borderRadius: 999, border: '1px solid rgba(47,74,63,.12)', background: 'transparent', color: '#2F4A3F', fontSize: 11, cursor: 'pointer' }}>Filters</button>
      </div>

      <div style={{ padding: '18px 22px 26px', display: 'flex', flexDirection: 'column', gap: 18 }}>
        <div style={{ padding: 18, borderRadius: 24, background: '#FFFFFF', border: '1px solid rgba(47,74,63,.08)', boxShadow: '0 8px 26px rgba(47,74,63,.06)' }}>
          <div style={{ position: 'relative', height: 300 }}>
            <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', borderRadius: '56% 44% 48% 52% / 46% 50% 50% 54%', background: 'linear-gradient(140deg, rgba(166,154,205,.35), rgba(221,234,230,.6))' }}>
              <PortraitSlot label="Camille" />
            </div>
            <div style={{ position: 'absolute', top: 12, right: 6, padding: '8px 14px', borderRadius: 999, background: 'rgba(166,154,205,.95)', color: '#FFFFFF', fontSize: 12, fontWeight: 500, pointerEvents: 'none' }}>{primary.fit}</div>
          </div>
          <div style={{ marginTop: 16, display: 'flex', alignItems: 'baseline', gap: 8 }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 26, color: '#2F4A3F' }}>{primary.name}</div>
          </div>
          <div style={{ marginTop: 3, fontSize: 12.5, color: '#94A09A' }}>{primary.location}</div>
          <div style={{ marginTop: 12, fontSize: 14, lineHeight: 1.6, color: '#4A5C53', textWrap: 'pretty' }}>{primary.blurb}</div>
          <div style={{ marginTop: 14, display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            {primary.tags.map((tag) => (
              <span key={tag} style={{ padding: '7px 13px', borderRadius: 999, background: '#F2EDE6', color: '#5C6B62', fontSize: 11.5 }}>{tag}</span>
            ))}
          </div>
          <button onClick={toggleWhy} style={{ marginTop: 16, width: '100%', padding: 14, borderRadius: 999, border: '1px solid rgba(166,154,205,.5)', background: 'rgba(166,154,205,.09)', color: '#8C7FBE', fontSize: 13, cursor: 'pointer' }}>{whyLabel}</button>

          {whyOpen && (
            <div style={{ marginTop: 14, padding: 18, borderRadius: 18, background: '#F6F4FA', animation: 'apRise .4s ease both' }}>
              <div style={{ fontSize: 10, letterSpacing: '.14em', color: '#8C7FBE' }}>WE FOCUSED ON WHAT MATTERS TO YOU</div>
              <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 14 }}>
                {whyItems.map((w) => (
                  <div key={w.title} style={{ display: 'flex', gap: 11 }}>
                    <span style={{ flex: 'none', marginTop: 5, width: 7, height: 7, borderRadius: '50%', background: '#A69ACD' }} />
                    <span style={{ flex: 1 }}>
                      <span style={{ display: 'block', fontSize: 13, color: '#2F4A3F' }}>{w.title}</span>
                      <span style={{ display: 'block', marginTop: 3, fontSize: 12, lineHeight: 1.5, color: '#5C6B62' }}>{w.body}</span>
                    </span>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid rgba(47,74,63,.08)', fontSize: 11.5, color: '#94A09A' }}>Explainable AI — we show you why, not just who.</div>
            </div>
          )}

          <div style={{ marginTop: 14, display: 'flex', gap: 10 }}>
            <button style={{ flex: 1, padding: 15, borderRadius: 999, border: '1px solid rgba(47,74,63,.14)', background: 'transparent', color: '#5C6B62', fontSize: 13.5, cursor: 'pointer' }}>Not now</button>
            <button style={{ flex: 2, padding: 15, border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 13.5, fontWeight: 500, cursor: 'pointer' }}>Say hello</button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 14 }}>
          {secondary.map((m, i) => (
            <div key={m.name} style={{ flex: 1, padding: 14, borderRadius: 20, background: '#FFFFFF', border: '1px solid rgba(47,74,63,.08)' }}>
              <div style={{ position: 'relative', height: 130, overflow: 'hidden', borderRadius: i === 0 ? '52% 48% 46% 54% / 48% 52% 48% 52%' : '46% 54% 52% 48% / 52% 46% 54% 48%', background: i === 0 ? 'linear-gradient(140deg, rgba(166,154,205,.3), rgba(221,234,230,.55))' : 'linear-gradient(140deg, rgba(221,234,230,.6), rgba(166,154,205,.3))' }}>
                <PortraitSlot label="Portrait" />
              </div>
              <div style={{ marginTop: 12, fontFamily: "'Playfair Display', serif", fontSize: 17, color: '#2F4A3F' }}>{m.name}</div>
              <div style={{ marginTop: 2, fontSize: 11, color: '#94A09A' }}>{m.location}</div>
            </div>
          ))}
        </div>

        <div style={{ padding: 20, borderRadius: 20, background: '#DDEAE6', textAlign: 'center' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, color: '#2F4A3F' }}>That's all for now</div>
          <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.6, color: '#4A5C53' }}>We'd rather show you three people who make sense than three hundred who don't.</div>
        </div>
      </div>
    </div>
  );
}
