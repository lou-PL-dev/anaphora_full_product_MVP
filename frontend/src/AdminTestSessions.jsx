import { useEffect, useState } from 'react';
import { adminApiCall } from './api';

const SAGE = '#2F4A3F';
const LAV = '#A69ACD';
const SAND = '#F2EDE6';
const SKY = '#DDEAE6';

function fmt(value) {
  if (!value) return '—';
  try { return new Date(value).toLocaleString(); } catch (e) { return value; }
}

function shortId(value) {
  return value ? value.slice(0, 8) : '—';
}

function Card({ children, style = {} }) {
  return <div style={{ background: '#fff', border: `1px solid ${SKY}`, borderRadius: 18, padding: 18, ...style }}>{children}</div>;
}

export default function AdminTestSessions() {
  const [secret, setSecret] = useState(() => sessionStorage.getItem('anaphora_admin_secret') || '');
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [error, setError] = useState('');

  const loadSessions = async (candidateSecret = secret) => {
    if (!candidateSecret) return;
    setLoading(true); setError('');
    const r = await adminApiCall(candidateSecret, '/admin/test-sessions');
    setLoading(false);
    if (!r.ok) {
      setError(r.status === 401 ? 'Wrong password.' : r.status === 503 ? 'ADMIN_SECRET is not configured on the backend.' : 'Could not load tester sessions.');
      return;
    }
    sessionStorage.setItem('anaphora_admin_secret', candidateSecret);
    setSessions(r.data?.sessions || []);
  };

  useEffect(() => { if (secret) loadSessions(secret); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  const openSession = async (userId) => {
    setLoading(true); setError('');
    const r = await adminApiCall(secret, '/admin/test-sessions/' + encodeURIComponent(userId));
    setLoading(false);
    if (!r.ok) { setError('Could not load this tester.'); return; }
    setSelected(r.data);
  };

  const clearTestData = async () => {
    const confirmed = window.confirm('Clear all tester data? This cannot be undone. Candidates and Discovery definitions will be kept.');
    if (!confirmed) return;
    setClearing(true); setError('');
    const r = await adminApiCall(secret, '/admin/test-sessions', 'DELETE');
    setClearing(false);
    if (!r.ok) {
      setError('Could not clear tester data.');
      return;
    }
    setSelected(null);
    setSessions([]);
  };

  if (!sessionStorage.getItem('anaphora_admin_secret') && !sessions.length) {
    return (
      <div style={{ minHeight: '100vh', background: SAND, display: 'grid', placeItems: 'center', padding: 24, fontFamily: 'Inter, sans-serif', color: SAGE }}>
        <form onSubmit={(e) => { e.preventDefault(); loadSessions(secret); }} style={{ width: '100%', maxWidth: 360 }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 30, marginBottom: 8 }}>Anaphora admin</div>
          <div style={{ fontSize: 13, marginBottom: 20, opacity: .75 }}>Private tester sessions</div>
          <input autoFocus type="password" value={secret} onChange={(e) => setSecret(e.target.value)} placeholder="Password" style={{ boxSizing: 'border-box', width: '100%', padding: '13px 15px', borderRadius: 12, border: `1px solid ${SKY}`, outline: 'none', fontSize: 14, marginBottom: 10 }} />
          <button disabled={loading || !secret} style={{ width: '100%', padding: 13, border: 0, borderRadius: 999, background: SAGE, color: '#fff', cursor: 'pointer' }}>{loading ? 'Opening…' : 'Open sessions'}</button>
          {error && <div style={{ marginTop: 12, fontSize: 12.5, color: '#8B3A3A' }}>{error}</div>}
        </form>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: SAND, fontFamily: 'Inter, sans-serif', color: SAGE, padding: '28px clamp(18px, 4vw, 52px) 60px' }}>
      <div style={{ maxWidth: 1180, margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 16, marginBottom: 24 }}>
          <div><div style={{ fontFamily: "'Playfair Display', serif", fontSize: 32 }}>Tester sessions</div><div style={{ marginTop: 5, fontSize: 12.5, opacity: .7 }}>{sessions.length} anonymous testers</div></div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => loadSessions()} style={{ border: `1px solid ${SKY}`, borderRadius: 999, padding: '8px 14px', background: '#fff', color: SAGE, cursor: 'pointer' }}>{loading ? 'Refreshing…' : 'Refresh'}</button>
            <button onClick={clearTestData} disabled={clearing || !sessions.length} style={{ border: `1px solid ${SKY}`, borderRadius: 999, padding: '8px 14px', background: 'transparent', color: SAGE, opacity: clearing || !sessions.length ? .45 : .8, cursor: clearing || !sessions.length ? 'default' : 'pointer' }}>{clearing ? 'Clearing…' : 'Clear test data'}</button>
          </div>
        </div>

        {error && <div style={{ marginBottom: 16, fontSize: 13, color: '#8B3A3A' }}>{error}</div>}

        {!selected ? (
          <div style={{ display: 'grid', gap: 10 }}>
            {sessions.map((s) => (
              <button key={s.user_id} onClick={() => openSession(s.user_id)} style={{ textAlign: 'left', border: 0, padding: 0, background: 'transparent', cursor: 'pointer' }}>
                <Card>
                  <div style={{ display: 'grid', gridTemplateColumns: 'minmax(110px,1.2fr) repeat(5,minmax(75px,.7fr))', gap: 14, alignItems: 'center' }}>
                    <div><div style={{ fontWeight: 600 }}>Tester {shortId(s.user_id)}</div><div style={{ fontSize: 11.5, opacity: .65, marginTop: 4 }}>{fmt(s.last_activity)}</div></div>
                    <div><b>{s.readiness}%</b><div style={{ fontSize: 10.5, opacity: .65 }}>readiness</div></div>
                    <div><b>{s.turn_count}</b><div style={{ fontSize: 10.5, opacity: .65 }}>turns</div></div>
                    <div><b>{s.discoveries_completed}</b><div style={{ fontSize: 10.5, opacity: .65 }}>discoveries</div></div>
                    <div><b>{s.signal_count}</b><div style={{ fontSize: 10.5, opacity: .65 }}>signals</div></div>
                    <div style={{ fontSize: 11.5, color: s.match_returned ? SAGE : LAV }}>{s.match_returned ? 'Intro ✓' : s.intros_opened ? 'Intros viewed' : 'No intro yet'}</div>
                  </div>
                </Card>
              </button>
            ))}
            {!sessions.length && !loading && <div style={{ opacity: .65 }}>No tester sessions yet.</div>}
          </div>
        ) : (
          <SessionDetail data={selected} onBack={() => setSelected(null)} secret={secret} />
        )}
      </div>
    </div>
  );
}

function SessionDetail({ data, onBack, secret }) {
  const [tab, setTab] = useState('journey');
  const [matches, setMatches] = useState(null);
  const [matchesLoading, setMatchesLoading] = useState(false);
  const [matchesError, setMatchesError] = useState('');
  const tabs = [['journey', 'Journey'], ['conversation', 'Conversation'], ['blueprint', 'Blueprint'], ['discoveries', 'Discoveries'], ['intros', 'Intros'], ['matches', 'Matches']];
  const introEvents = (data.events || []).filter((e) => e.event === 'intros_opened' || e.event === 'match_returned');

  const loadMatches = async () => {
    setMatchesLoading(true); setMatchesError('');
    const r = await adminApiCall(secret, '/admin/test-sessions/' + encodeURIComponent(data.user_id) + '/matches-debug');
    setMatchesLoading(false);
    if (!r.ok) { setMatchesError('Could not load match diagnostics for this tester.'); return; }
    setMatches(r.data);
  };

  useEffect(() => {
    if (tab === 'matches' && !matches && !matchesLoading) loadMatches();
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [tab]);

  return (
    <div>
      <button onClick={onBack} style={{ border: 0, background: 'transparent', color: SAGE, cursor: 'pointer', padding: '0 0 16px' }}>← All testers</button>
      <Card style={{ marginBottom: 16 }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 25 }}>Tester {shortId(data.user_id)}</div>
        <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', marginTop: 8, fontSize: 12.5 }}><span>{data.readiness}% readiness</span><span>Started {fmt(data.started_at)}</span><span style={{ opacity: .6 }}>{data.user_id}</span></div>
      </Card>

      <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap', marginBottom: 14 }}>
        {tabs.map(([key, label]) => <button key={key} onClick={() => setTab(key)} style={{ border: `1px solid ${key === tab ? LAV : SKY}`, background: key === tab ? '#fff' : 'transparent', color: SAGE, borderRadius: 999, padding: '8px 13px', cursor: 'pointer' }}>{label}</button>)}
      </div>

      {tab === 'journey' && <Card>{(data.events || []).length ? data.events.map((e, i) => <div key={i} style={{ padding: '10px 0', borderBottom: i < data.events.length - 1 ? `1px solid ${SKY}` : 'none' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}><b style={{ fontSize: 13 }}>{e.event.replaceAll('_', ' ')}</b><span style={{ fontSize: 11, opacity: .6 }}>{fmt(e.created_at)}</span></div>{Object.keys(e.metadata || {}).length > 0 && <div style={{ marginTop: 5, fontSize: 11.5, opacity: .7 }}>{JSON.stringify(e.metadata)}</div>}</div>) : <div style={{ opacity: .65 }}>No behavioural events recorded yet.</div>}</Card>}

      {tab === 'conversation' && <div style={{ display: 'grid', gap: 12 }}>{(data.conversations || []).map((c) => <Card key={c.id}><div style={{ fontSize: 11, opacity: .6, marginBottom: 12 }}>{fmt(c.created_at)} · {c.status} · {shortId(c.id)}</div>{(c.messages || []).map((m, i) => <div key={i} style={{ margin: '9px 0', padding: '10px 12px', borderRadius: 12, background: m.role === 'user' ? SAND : '#fff', border: m.role === 'assistant' ? `1px solid ${SKY}` : 'none' }}><b style={{ fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.08em', color: LAV }}>{m.role}</b><div style={{ fontSize: 13, lineHeight: 1.55, marginTop: 4 }}>{m.content}</div></div>)}</Card>)}</div>}

      {tab === 'blueprint' && <Card>{data.blueprint_narrative && <div style={{ marginBottom: 18, lineHeight: 1.6, fontSize: 13 }}>{data.blueprint_narrative}</div>}{(data.signals || []).map((s, i) => <div key={s.id || i} style={{ padding: '9px 0', borderTop: i ? `1px solid ${SKY}` : 'none' }}><div style={{ fontSize: 10.5, color: LAV }}>{s.perspective} · {s.category} · {s.strength}</div><div style={{ fontSize: 13, fontWeight: 600, marginTop: 3 }}>{s.label}</div>{s.evidence_text && <div style={{ fontSize: 11.5, opacity: .7, marginTop: 3 }}>{s.evidence_text}</div>}</div>)}</Card>}

      {tab === 'discoveries' && <Card>{(data.discoveries || []).length ? data.discoveries.map((d, i) => <div key={i} style={{ padding: '10px 0', borderTop: i ? `1px solid ${SKY}` : 'none' }}><div style={{ fontSize: 10.5, color: LAV }}>{d.discovery_id} · {d.question_id}</div><div style={{ fontSize: 13, marginTop: 4 }}>{d.response}</div></div>) : <div style={{ opacity: .65 }}>No Discovery answers yet.</div>}</Card>}

      {tab === 'intros' && <Card>{introEvents.length ? introEvents.map((e, i) => <div key={i} style={{ padding: '10px 0', borderTop: i ? `1px solid ${SKY}` : 'none' }}><div style={{ fontWeight: 600 }}>{e.event === 'match_returned' ? 'Match returned' : 'Intros opened'}</div><div style={{ fontSize: 12, marginTop: 4, opacity: .75 }}>{fmt(e.created_at)} · {JSON.stringify(e.metadata || {})}</div></div>) : <div style={{ opacity: .65 }}>No Intros activity yet.</div>}</Card>}

      {tab === 'matches' && (
        <Card>
          <div style={{ fontSize: 12.5, opacity: .75, marginBottom: 16, lineHeight: 1.5 }}>
            Why this tester did or didn't get a match — runs the same steps as the real Matches screen, but shows the count and score at every step instead of only the final result.
          </div>
          {matchesLoading && <div style={{ opacity: .65 }}>Checking…</div>}
          {!matchesLoading && matchesError && <div style={{ color: '#8B3A3A', fontSize: 13 }}>{matchesError}</div>}
          {!matchesLoading && !matchesError && matches && matches.error && (
            <div style={{ fontSize: 13 }}>{matches.error}{typeof matches.readiness === 'number' && <div style={{ marginTop: 6, opacity: .7 }}>Readiness: {matches.readiness}%</div>}</div>
          )}
          {!matchesLoading && !matchesError && matches && !matches.error && (
            <div style={{ display: 'grid', gap: 16 }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))', gap: 12 }}>
                <div><b>{matches.candidate_pool_total}</b><div style={{ fontSize: 10.5, opacity: .65 }}>total candidates in the pool</div></div>
                <div><b>{matches.after_direction1_demographic_filter}</b><div style={{ fontSize: 10.5, opacity: .65 }}>match this tester's stated preference</div></div>
                <div><b>{matches.after_direction2_reverse_eligibility}</b><div style={{ fontSize: 10.5, opacity: .65 }}>of those, are also open to this tester</div></div>
                <div><b>{matches.finalists_that_would_reach_relationship_reasoning}</b><div style={{ fontSize: 10.5, opacity: .65 }}>strong enough to be considered a real intro</div></div>
              </div>

              {matches.user_signal_counts && (
                <div style={{ fontSize: 12, opacity: .7 }}>
                  This tester's own Blueprint: {matches.user_signal_counts.me} ME signals · {matches.user_signal_counts.ideal_partner} IDEAL_PARTNER signals · {matches.user_signal_counts.us} US signals
                  {matches.user_signal_counts.us === 0 && ' — no US signals means less shared-vision evidence is possible against any candidate.'}
                </div>
              )}

              {(matches.finalists_after_reranking || []).length ? (
                <div>
                  <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.06em', color: LAV, marginBottom: 8 }}>Closest candidates</div>
                  <div style={{ display: 'grid', gap: 8 }}>
                    {matches.finalists_after_reranking.map((f) => (
                      <div key={f.candidate_id} style={{ padding: '10px 12px', borderRadius: 12, background: SAND, display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                        <div>
                          <b>{f.candidate_name || shortId(f.candidate_id)}</b>
                          <div style={{ fontSize: 11, opacity: .65, marginTop: 2 }}>{f.evidence_count} shared evidence points{!f.reciprocal_complete && ' · one-sided only'}</div>
                        </div>
                        <div style={{ textAlign: 'right', fontSize: 12.5 }}>
                          <div>overall {f.score}</div>
                          <div style={{ opacity: .65 }}>them→tester {f.reverse ?? '—'} · tester→them {f.forward}</div>
                          <div style={{ marginTop: 2, color: f.would_pass_deterministic_gate ? SAGE : '#8B3A3A', fontWeight: 600 }}>
                            {f.would_pass_deterministic_gate ? f.would_pass_deterministic_gate.replaceAll('_', ' ') : 'not close enough yet'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : <div style={{ opacity: .65, fontSize: 13 }}>No candidates were close enough to rank.</div>}

              <div style={{ fontSize: 11, opacity: .55 }}>Refreshed just now · readiness {matches.readiness}%</div>
            </div>
          )}
          <button onClick={loadMatches} disabled={matchesLoading} style={{ marginTop: 16, border: `1px solid ${SKY}`, borderRadius: 999, padding: '8px 14px', background: 'transparent', color: SAGE, cursor: matchesLoading ? 'default' : 'pointer' }}>{matchesLoading ? 'Checking…' : 'Re-check'}</button>
        </Card>
      )}
    </div>
  );
}
