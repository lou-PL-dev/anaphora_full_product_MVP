import { useEffect, useState } from 'react';
import { apiCall, getOrCreateUserId } from '../api';

export default function Home({ readiness, readinessHeadline, readinessSub, insight, steps, openPlans, goBlueprint, goIntro, signalCount, discoverySaving, discoverySaveError, retryDiscovery, postMatchMode, refinementActions, nextDiscovery, startDiscovery }) {
  const [liveReadiness, setLiveReadiness] = useState(null);
  const [liveBreakdown, setLiveBreakdown] = useState(null);

  useEffect(() => {
    const uid = getOrCreateUserId();
    let cancelled = false;
    apiCall(uid, 'GET', '/readiness').then((r) => {
      if (!cancelled && r) {
        setLiveReadiness(r.readiness_pct);
        setLiveBreakdown(r.breakdown || {});
      }
    });
    const onReadiness = (event) => {
      const detail = event.detail || {};
      if (detail.readiness != null) setLiveReadiness(detail.readiness);
      if (detail.breakdown) setLiveBreakdown(detail.breakdown);
    };
    window.addEventListener('anaphora:readiness-updated', onReadiness);
    return () => {
      cancelled = true;
      window.removeEventListener('anaphora:readiness-updated', onReadiness);
    };
  }, []);

  // App receives fresh readiness values from conversation/discovery responses.
  // Keep the local display cache aligned so an older mount-time GET cannot
  // mask a newer 100% value while the Intro tab already sees backend readiness.
  useEffect(() => {
    if (readiness != null) setLiveReadiness(readiness);
  }, [readiness]);

  const shownReadiness = liveReadiness ?? readiness;
  const arcOffset = 427 - 427 * (shownReadiness / 100);
  const intro = liveBreakdown?.introduction_essentials;
  const introEarned = intro?.earned || 0;
  const introDone = !!intro?.met;

  const shownSteps = steps.map((st) => {
    if (st.key !== 'prefs') return st;
    if (!liveBreakdown) {
      return { ...st, title: 'Introduction essentials', note: st.done ? 'Your essentials and preferences are set' : 'Your essentials and who you’d like to meet' };
    }
    const partial = introEarned > 0 && !introDone;
    return {
      ...st,
      title: 'Introduction essentials',
      note: introDone ? 'Your essentials and preferences are set' : (partial ? `${introEarned} / 20% complete` : 'Your essentials and who you’d like to meet'),
      done: introDone,
      cta: introDone ? 'Edit' : (partial ? 'Complete' : 'Set'),
      mark: introDone ? '✓' : '',
      ring: introDone || partial ? '#2F4A3F' : '#DDEAE6',
      fill: introDone ? '#2F4A3F' : 'transparent',
    };
  });

  const liveCopy = shownReadiness >= 90
    ? ['Ready when you are', 'We know enough to look for people who actually fit.']
    : shownReadiness >= 60
      ? ['Coming into focus', 'A little more and intros start making real sense.']
      : shownReadiness > 0
        ? ['A good beginning', 'Every answer sharpens who we look for.']
        : ['Nothing yet', 'One conversation is all it takes to start.'];
  const shownHeadline = liveReadiness == null ? readinessHeadline : liveCopy[0];
  const shownSub = liveReadiness == null ? readinessSub : liveCopy[1];

  const refinementByKey = Object.fromEntries((refinementActions || []).map((action) => [action.key, action]));
  const conversationAction = refinementByKey.talk;
  const friendAction = refinementByKey.friend;

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: postMatchMode ? '#F2EDE6' : '#FFFFFF' }}>
      <div style={{ padding: postMatchMode ? '62px 22px 22px' : '62px 22px 26px', background: postMatchMode ? 'linear-gradient(165deg, #F2EDE6 0%, #F2EDE6 100%)' : 'linear-gradient(165deg, #F2EDE6 0%, #FFFFFF 100%)', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -110, right: -90, width: 250, height: 240, borderRadius: '55% 45% 48% 52% / 50% 52% 48% 50%', background: 'rgba(166,154,205,.18)' }} />
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 21, color: '#2F4A3F' }}>anaphora</div>
          <button onClick={openPlans} style={{ padding: '7px 13px', borderRadius: 999, border: '1px solid rgba(166,154,205,.5)', background: 'rgba(255,255,255,.7)', color: '#A69ACD', fontSize: 11, letterSpacing: '.04em', cursor: 'pointer' }}>Anaphora+</button>
        </div>

        {postMatchMode ? (
          <div style={{ position: 'relative', marginTop: 28, maxWidth: 330 }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 29, lineHeight: 1.18, color: '#2F4A3F' }}>Your Blueprint keeps evolving.</div>
            <div style={{ marginTop: 7, fontSize: 13, lineHeight: 1.5, color: '#2F4A3F' }}>There’s always more to discover.</div>
          </div>
        ) : (
          <>
            <div style={{ position: 'relative', marginTop: 24, display: 'flex', alignItems: 'center', gap: 20 }}>
              <div style={{ flex: 'none', position: 'relative', width: 152, height: 152 }}>
                <svg viewBox="0 0 160 160" style={{ width: 152, height: 152, transform: 'rotate(-90deg)' }}>
                  <circle cx="80" cy="80" r="68" fill="none" stroke="#DDEAE6" strokeWidth="9" />
                  <circle cx="80" cy="80" r="68" fill="none" stroke="#A69ACD" strokeWidth="9" strokeLinecap="round" strokeDasharray="427" strokeDashoffset={arcOffset} style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.2,.8,.2,1)' }} />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 44, lineHeight: 1, color: '#2F4A3F' }}>{shownReadiness}<span style={{ fontSize: 20, color: '#A69ACD' }}>%</span></div>
                  <div style={{ marginTop: 4, fontSize: 9.5, letterSpacing: '.14em', color: '#A69ACD' }}>READINESS</div>
                </div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, lineHeight: 1.3, color: '#2F4A3F' }}>{shownHeadline}</div>
                <div style={{ marginTop: 8, fontSize: 12.5, lineHeight: 1.55, color: '#2F4A3F', textWrap: 'pretty' }}>{shownSub}</div>
              </div>
            </div>
            {shownReadiness >= 100 && (
              <button onClick={goIntro} style={{ position: 'relative', width: '100%', marginTop: 18, padding: '15px 20px', border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#FFFFFF', fontSize: 14, fontWeight: 500, letterSpacing: '.01em', cursor: 'pointer', boxShadow: '0 9px 24px rgba(47,74,63,.20)' }}>See who Anaphora found →</button>
            )}
          </>
        )}
      </div>

      <div style={{ padding: '20px 22px 26px', display: 'flex', flexDirection: 'column', gap: postMatchMode ? 18 : 22 }}>
        {discoverySaving && (
          <div style={{ padding: '15px 18px', borderRadius: 18, background: '#DDEAE6', display: 'flex', alignItems: 'center', gap: 12, color: '#2F4A3F', fontSize: 12.5 }}>
            <span style={{ width: 15, height: 15, flex: 'none', borderRadius: '50%', border: '2px solid rgba(166,154,205,.25)', borderTopColor: '#A69ACD', animation: 'apSpin .8s linear infinite' }} />
            <span><strong style={{ color: '#2F4A3F', fontWeight: 500 }}>Adding your insight…</strong><br />Your Blueprint will update in a moment.</span>
          </div>
        )}

        {discoverySaveError && !discoverySaving && (
          <div style={{ padding: '15px 18px', borderRadius: 18, background: '#F2EDE6', color: '#2F4A3F', fontSize: 12.5, lineHeight: 1.5 }}>
            We couldn’t add this insight yet. Your answers are still here.
            <button onClick={retryDiscovery} style={{ marginLeft: 7, padding: 0, border: 'none', background: 'transparent', color: '#A69ACD', font: 'inherit', fontWeight: 600, cursor: 'pointer' }}>Try again</button>
          </div>
        )}

        {postMatchMode ? (
          <>
            {nextDiscovery && (
              <div>
                <div style={{ fontSize: 10.5, letterSpacing: '.15em', color: '#2F4A3F', marginBottom: 9 }}>DISCOVER SOMETHING NEW</div>
                <button onClick={() => startDiscovery(nextDiscovery.id, 'home')} style={{ position: 'relative', overflow: 'hidden', width: '100%', padding: '21px 21px 20px', border: 'none', borderRadius: 22, background: 'linear-gradient(145deg, #DDEAE6 0%, #F2EDE6 100%)', textAlign: 'left', cursor: 'pointer' }}>
                  <span style={{ position: 'absolute', width: 130, height: 130, right: -38, top: -52, borderRadius: '48% 52% 60% 40% / 52% 42% 58% 48%', background: 'rgba(166,154,205,.17)' }} />
                  <span style={{ position: 'relative', display: 'block', fontSize: 9.5, letterSpacing: '.15em', color: '#A69ACD' }}>{nextDiscovery.deeper ? 'DEEPER REFLECTION' : `${nextDiscovery.questions} QUESTIONS · ${nextDiscovery.minutes} MIN`}</span>
                  <span style={{ position: 'relative', display: 'block', marginTop: 9, maxWidth: 270, fontFamily: "'Playfair Display', serif", fontSize: 23, lineHeight: 1.25, color: '#2F4A3F' }}>{nextDiscovery.title}</span>
                  <span style={{ position: 'relative', display: 'block', marginTop: 9, fontSize: 12.5, lineHeight: 1.5, color: '#2F4A3F' }}>{nextDiscovery.note}</span>
                  <span style={{ position: 'relative', display: 'block', marginTop: 15, fontSize: 12, color: '#A69ACD' }}>Explore →</span>
                </button>
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <button onClick={conversationAction?.onGo} style={{ minHeight: 132, padding: '17px 16px', borderRadius: 20, border: '1px solid #DDEAE6', background: '#FFFFFF', textAlign: 'left', cursor: 'pointer', display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 18, color: '#A69ACD' }}>◌</span>
                <span style={{ marginTop: 12, fontFamily: "'Playfair Display', serif", fontSize: 17, lineHeight: 1.2, color: '#2F4A3F' }}>Add to your story</span>
                <span style={{ marginTop: 'auto', paddingTop: 10, fontSize: 11.5, color: '#A69ACD' }}>Share →</span>
              </button>
              <button onClick={friendAction?.onGo} style={{ minHeight: 132, padding: '17px 16px', borderRadius: 20, border: '1px solid #DDEAE6', background: '#FFFFFF', textAlign: 'left', cursor: 'pointer', display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 18, color: '#A69ACD' }}>◎</span>
                <span style={{ marginTop: 12, fontFamily: "'Playfair Display', serif", fontSize: 17, lineHeight: 1.2, color: '#2F4A3F' }}>Through their eyes</span>
                <span style={{ marginTop: 'auto', paddingTop: 10, fontSize: 11.5, color: '#A69ACD' }}>Invite →</span>
              </button>
            </div>

            <button onClick={goBlueprint} style={{ width: '100%', padding: '16px 2px', border: 'none', borderTop: '1px solid #DDEAE6', borderBottom: '1px solid #DDEAE6', background: 'transparent', cursor: 'pointer', display: 'flex', alignItems: 'center', textAlign: 'left' }}>
              <span style={{ flex: 1 }}>
                <span style={{ display: 'block', fontSize: 10, letterSpacing: '.14em', color: '#A69ACD' }}>YOUR BLUEPRINT</span>
                <span style={{ display: 'block', marginTop: 5, fontFamily: "'Playfair Display', serif", fontSize: 18, color: '#2F4A3F' }}>{signalCount} signals and growing</span>
              </span>
              <span style={{ fontSize: 12, color: '#A69ACD' }}>Explore →</span>
            </button>

            {insight && (
              <div style={{ padding: '17px 19px', borderRadius: 20, background: '#DDEAE6', animation: 'apRise .5s ease both' }}>
                <div style={{ fontSize: 9.5, letterSpacing: '.15em', color: '#2F4A3F' }}>ANAPHORA NOTICED</div>
                <div style={{ marginTop: 8, fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: 18, lineHeight: 1.4, color: '#2F4A3F' }}>“{insight}”</div>
              </div>
            )}
          </>
        ) : (
          <>
            {insight && (
              <div style={{ padding: '20px 22px', borderRadius: 20, background: 'linear-gradient(140deg, rgba(166,154,205,.18), #DDEAE6)', animation: 'apRise .5s ease both' }}>
                <div style={{ fontSize: 10, letterSpacing: '.15em', color: '#A69ACD' }}>FROM YOUR DISCOVERY</div>
                <div style={{ marginTop: 10, fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: 20, lineHeight: 1.4, color: '#2F4A3F' }}>“{insight}”</div>
              </div>
            )}

            <div>
              <div style={{ fontSize: 11, letterSpacing: '.14em', color: '#2F4A3F', paddingBottom: 6 }}>WHAT WOULD HELP MOST</div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {shownSteps.map((st) => (
                  <button key={st.key} onClick={st.onGo} style={{ width: '100%', textAlign: 'left', display: 'flex', alignItems: 'center', gap: 13, padding: '15px 4px', border: 'none', borderBottom: '1px solid #DDEAE6', background: 'transparent', cursor: 'pointer' }}>
                    <span style={{ flex: 'none', width: 22, height: 22, borderRadius: '50%', border: `1.5px solid ${st.ring}`, background: st.fill, display: 'grid', placeItems: 'center', color: '#FFFFFF', fontSize: 11 }}>{st.mark}</span>
                    <span style={{ flex: 1 }}>
                      <span style={{ display: 'block', fontSize: 14, color: '#2F4A3F' }}>{st.title}</span>
                      <span style={{ display: 'block', marginTop: 3, fontSize: 12, color: '#A69ACD' }}>{st.note}</span>
                    </span>
                    <span style={{ flex: 'none', fontSize: 11, color: '#A69ACD', letterSpacing: '.04em' }}>{st.cta}</span>
                  </button>
                ))}
              </div>
            </div>

            <div style={{ padding: 20, borderRadius: 20, border: '1px solid #DDEAE6', background: '#FFFFFF' }}>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F' }}>Your Blueprint</div>
              <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>{signalCount} signals, drawn from your own words.</div>
              <button onClick={goBlueprint} style={{ marginTop: 14, padding: '12px 20px', border: '1px solid #DDEAE6', borderRadius: 999, background: 'transparent', color: '#2F4A3F', fontSize: 13, cursor: 'pointer' }}>Review it</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
