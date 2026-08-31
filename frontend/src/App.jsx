import { useEffect, useRef, useState } from 'react';
import PhoneFrame from './components/PhoneFrame';
import TabBar from './components/TabBar';
import SignalEditSheet from './components/SignalEditSheet';
import PlansModal from './components/PlansModal';
import Welcome from './screens/Welcome';
import Legal from './screens/Legal';
import Chat from './screens/Chat';
import Enough from './screens/Enough';
import Blueprint from './screens/Blueprint';
import Home from './screens/Home';
import Convos from './screens/Convos';
import Discovery from './screens/Discovery';
import Insight from './screens/Insight';
import Matches from './screens/Matches';
import Friends from './screens/Friends';
import Profile from './screens/Profile';
import { apiCall, getOrCreateUserId, TIMEOUT_CHAT_REPLY, TIMEOUT_EXTRACTION, TIMEOUT_INSIGHT, TIMEOUT_MATCHES } from './api';
import { mockReadiness } from './readiness';
import { BASE_CATEGORIES, GROUP_DEFS, STRENGTHS, STRENGTH_STYLE } from './data';
import { LAV, SAGE } from './theme';

const TAB_SCREENS = ['home', 'convos', 'matches', 'friends', 'profile'];
const EMPTY_COVERAGE = { me: [], ideal_partner: [] };

const initialState = {
  screen: 'welcome', framed: false, mode: 'checking',
  convoId: null, messages: [], draft: '', thinking: false,
  turnCount: 0, readyToComplete: false, coverage: EMPTY_COVERAGE,
  signals: [], readiness: 0, readinessLoaded: false, readinessBreakdown: {}, narrative: '', insight: '', newSignals: [],
  questions: [], dqIdx: 0, answers: {},
  discoveryDone: false, discoverySaving: false, discoverySaveError: false, convoCompleted: false,
  editing: null, editLabel: '', editStrength: 'preference',
  plansOpen: false,
  gender: null, ageMax: 36,
  matches: [], matchesLoading: false, matchesLoaded: false, matchesReady: null,
  legalSection: 'privacy', error: null,
};

export default function App() {
  const [s, setS] = useState(initialState);
  const uidRef = useRef(null);
  const chatEndRef = useRef(null);
  const patch = (update) => setS((prev) => ({ ...prev, ...(typeof update === 'function' ? update(prev) : update) }));
  const api = async (method, path, body, timeoutMs) => {
    const r = await apiCall(uidRef.current, method, path, body, timeoutMs);
    patch({ mode: r === null ? 'offline' : 'live' });
    return r;
  };

  const refreshReadiness = async () => {
    const r = await api('GET', '/readiness');
    if (r) patch({
      readiness: r.readiness_pct,
      readinessLoaded: true,
      readinessBreakdown: r.breakdown || {},
      discoveryDone: !!r.breakdown?.discovery_completed?.met,
    });
    return r;
  };

  useEffect(() => {
    uidRef.current = getOrCreateUserId();
    api('GET', '/discovery/life_you_are_building').then((r) => { if (r?.questions) patch({ questions: r.questions }); });
    api('GET', '/blueprint').then((r) => { if (r) patch({ signals: r.signals || [], narrative: r.narrative || '' }); });
    refreshReadiness();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    const el = chatEndRef.current;
    if (el?.parentElement) el.parentElement.scrollTop = el.parentElement.scrollHeight;
  }, [s.messages, s.thinking]);

  const go = (screen) => () => patch({ screen, error: null });
  const goLegal = (legalSection) => () => patch({ screen: 'legal', legalSection, error: null });

  const beginConversation = async () => {
    patch({ screen: 'chat', messages: [], turnCount: 0, readyToComplete: false, coverage: EMPTY_COVERAGE, convoId: null, error: null });
    const r = await api('POST', '/conversation/start');
    if (r) patch({ convoId: r.conversation_id, messages: [{ role: 'assistant', content: r.message }] });
    else patch({ error: { screen: 'chat', message: "Couldn't reach the backend to start the conversation. Check it's running, then retry." } });
  };
  const resumeConversation = () => { if (s.messages.length) patch({ screen: 'chat' }); else beginConversation(); };
  const onDraft = (e) => patch({ draft: e.target.value });
  const setDraft = (text) => patch({ draft: text });
  const onDraftKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };
  const sendMessage = async () => {
    const text = s.draft.trim();
    if (!text || s.thinking) return;
    patch((prev) => ({ messages: prev.messages.concat([{ role: 'user', content: text }]), draft: '', thinking: true, error: null }));
    const r = await api('POST', '/conversation/message', { conversation_id: s.convoId, message: text }, TIMEOUT_CHAT_REPLY);
    if (r) patch((prev) => ({ thinking: false, messages: prev.messages.concat([{ role: 'assistant', content: r.reply }]), readyToComplete: r.ready_to_complete, turnCount: r.turn_count, coverage: r.coverage || EMPTY_COVERAGE }));
    else patch((prev) => ({ thinking: false, messages: prev.messages.slice(0, -1), draft: text, error: { screen: 'chat', message: "Anaphora didn't respond in time. Check the backend is running, then send again." } }));
  };
  const completeConversation = async () => {
    patch({ error: null });
    const r = await api('POST', '/conversation/complete', { conversation_id: s.convoId }, TIMEOUT_EXTRACTION);
    if (r) {
      patch((prev) => ({
        signals: prev.signals.filter((x) => x.source !== 'conversation').concat(r.signals),
        narrative: r.narrative, readiness: r.readiness_pct, readinessLoaded: true,
        convoCompleted: true, screen: 'enough',
      }));
      refreshReadiness();
    } else patch({ error: { screen: 'chat', message: "Couldn't build your Blueprint — the request timed out or the backend is unreachable. Tap “Create my Blueprint” to try again." } });
  };

  const fetchMatches = async () => {
    patch({ matchesLoading: true, error: null });
    const r = await api('GET', '/matches', undefined, TIMEOUT_MATCHES);
    if (r) patch({ matches: r.matches, matchesReady: r.ready, matchesLoading: false, matchesLoaded: r.ready });
    else patch({ matchesLoading: false, error: { screen: 'matches', message: "Couldn't load your matches — check the backend is running, then try again." } });
  };
  const goMatches = () => { patch({ screen: 'matches', error: null }); if (!s.matchesLoaded && !s.matchesLoading) fetchMatches(); };

  const openEdit = (sig) => () => patch({ editing: sig, editLabel: sig.label, editStrength: sig.strength });
  const closeEdit = () => patch({ editing: null });
  const onEditLabel = (e) => patch({ editLabel: e.target.value });
  const pickStrength = (v) => () => patch({ editStrength: v });
  const saveEdit = async () => {
    const { editing, editLabel, editStrength } = s;
    patch((prev) => ({ editing: null, signals: prev.signals.map((x) => (x.id === editing.id ? { ...x, label: editLabel, strength: editStrength } : x)) }));
    await api('PATCH', '/blueprint/signal/' + editing.id, { label: editLabel, strength: editStrength });
    refreshReadiness();
  };

  const startDiscovery = () => patch({ screen: 'discovery', dqIdx: 0, answers: {}, error: null, discoverySaveError: false });
  const discoveryBack = () => { if (s.dqIdx === 0) patch({ screen: 'home' }); else patch((prev) => ({ dqIdx: prev.dqIdx - 1 })); };
  const pickOption = (qid, label) => () => patch((prev) => ({ answers: { ...prev.answers, [qid]: label } }));
  const onSpectrum = (e) => { const q = s.questions[s.dqIdx]; const v = Number(e.target.value); patch((prev) => ({ answers: { ...prev.answers, [q.id]: v } })); };

  const buildDiscoveryPayload = (questions, answers) => questions.map((qq) => {
    const a = answers[qq.id];
    let response = String(a);
    if (qq.spectrum) {
      const v = Number(a);
      response = v < 45 ? qq.spectrum[0] : (v > 55 ? qq.spectrum[1] : 'Balanced between ' + qq.spectrum[0] + ' and ' + qq.spectrum[1]);
      response += ' (' + v + '/100 toward ' + qq.spectrum[1] + ')';
    } else if (qq.options) {
      const o = qq.options.find((x) => x.label === a);
      response = o ? o.id : String(a);
    }
    return { user_id: uidRef.current, question_id: qq.id, response };
  });

  const submitDiscoveryInBackground = async (questions, answers) => {
    const payload = buildDiscoveryPayload(questions, answers);
    patch({ discoverySaving: true, discoverySaveError: false, error: null });
    const r = await api('POST', '/discovery/life_you_are_building/respond', payload, TIMEOUT_INSIGHT);
    if (r) {
      patch((prev) => ({ insight: r.insight_text, newSignals: r.new_signals, signals: prev.signals.concat(r.new_signals), readiness: r.readiness_pct, readinessLoaded: true, discoveryDone: true, discoverySaving: false, discoverySaveError: false }));
      refreshReadiness();
    } else patch({ discoverySaving: false, discoverySaveError: true });
  };

  const discoveryNext = () => {
    const { dqIdx, questions, answers } = s;
    const q = questions[dqIdx];
    if (answers[q.id] === undefined) return;
    if (dqIdx < questions.length - 1) { patch({ dqIdx: dqIdx + 1, error: null }); return; }
    patch({ screen: 'home', discoverySaving: true, discoverySaveError: false, error: null });
    submitDiscoveryInBackground(questions, answers);
  };
  const retryDiscovery = () => {
    if (s.discoverySaving || !s.questions.length || !Object.keys(s.answers).length) return;
    submitDiscoveryInBackground(s.questions, s.answers);
  };

  const savePreferences = async (gender, ageMax) => {
    const r = await api('PATCH', '/profile/matching-preferences', { gender_preference: gender, preferred_age_range: `24-${ageMax}` });
    if (r) patch({ readiness: r.readiness_pct, readinessLoaded: true, readinessBreakdown: r.breakdown || {} });
  };
  const pickGender = (v) => { patch({ gender: v }); savePreferences(v, s.ageMax); };
  const onAge = (e) => { const ageMax = Number(e.target.value); patch({ ageMax }); if (s.gender) savePreferences(s.gender, ageMax); };
  const resetAll = () => patch({ ...initialState, screen: 'welcome', mode: s.mode, framed: s.framed });
  const toggleFrame = () => patch((prev) => ({ framed: !prev.framed }));
  const openPlans = () => patch({ plansOpen: true });
  const closePlans = () => patch({ plansOpen: false });

  const accent = LAV;
  const groups = GROUP_DEFS.map(([persp, cat, title, side]) => {
    const items = s.signals.filter((x) => x.perspective === persp && (cat ? x.category === cat : true)).map((x) => {
      const st = STRENGTH_STYLE[x.strength] || STRENGTH_STYLE.preference;
      return { id: x.id, label: x.label, evidence: x.evidence_text || '', strengthLabel: st.label, dot: st.dot, pillBg: st.bg, pillFg: st.fg, onEdit: openEdit(x) };
    });
    return { title, side, items };
  }).filter((g) => g.items.length);

  const offlineBr = mockReadiness(s.signals, s.discoveryDone, !!s.gender);
  const readiness = s.readinessLoaded ? s.readiness : offlineBr.total;
  const breakdownMet = Object.fromEntries(Object.entries(s.readinessBreakdown).map(([k, v]) => [k, !!v.met]));
  const steps = [
    { key: 'convo', title: 'Build both sides of your Blueprint', note: s.convoCompleted ? 'First Blueprint created — keep refining anytime' : 'Tell Anaphora who you want and naturally reveal who you are', done: !!s.readinessBreakdown.me_profile?.met && !!s.readinessBreakdown.ideal_partner_profile?.met, cta: s.convoCompleted ? 'Add more' : 'Start', onGo: s.convoCompleted ? go('convos') : beginConversation },
    { key: 'disc', title: 'Complete your first Discovery', note: s.discoverySaving ? 'Adding insight to your Blueprint…' : (s.discoveryDone ? 'Insight added to your Blueprint' : 'What kind of life are you building? · 4 questions'), done: s.discoveryDone, cta: s.discoverySaving ? 'Adding…' : (s.discoveryDone ? 'Done' : '2 min'), onGo: s.discoveryDone ? go('insight') : (s.discoverySaving ? () => {} : startDiscovery) },
    { key: 'prefs', title: 'Basic matching preferences', note: s.gender ? s.gender + ' · 24–' + s.ageMax : 'Who and what age range', done: !!s.readinessBreakdown.basic_matching_preferences?.met, cta: s.gender ? 'Edit' : 'Set', onGo: go('profile') },
  ].map((st) => ({ ...st, mark: st.done ? '✓' : '', ring: st.done ? SAGE : 'rgba(47,74,63,.22)', fill: st.done ? SAGE : 'transparent' }));

  const q = s.questions[s.dqIdx] || { id: '_none', prompt: '', options: [] };
  const ans = s.answers[q.id];
  const isSpectrum = !!q.spectrum;
  const sv = isSpectrum ? (ans === undefined ? 50 : Number(ans)) : 50;
  let reading = '';
  if (isSpectrum) {
    if (ans === undefined) reading = '';
    else if (sv <= 20) reading = 'Firmly ' + q.spectrum[0].toLowerCase();
    else if (sv < 45) reading = 'Leaning ' + q.spectrum[0].toLowerCase();
    else if (sv <= 55) reading = 'Both, honestly';
    else if (sv < 80) reading = 'Leaning ' + q.spectrum[1].toLowerCase();
    else reading = 'Firmly ' + q.spectrum[1].toLowerCase();
  }
  const answered = ans !== undefined;
  const last = s.dqIdx === s.questions.length - 1;
  const readinessCopy = readiness === 100 ? ['Ready for introductions', 'We know enough to start matching responsibly. Your Blueprint can keep growing.'] : readiness >= 60 ? ['Coming into focus', 'A little more and Anaphora will know enough to make introductions.'] : readiness > 0 ? ['A good beginning', 'Complete the essentials so matching can begin.'] : ['Start your Blueprint', 'A few thoughtful steps are enough to get ready for introductions.'];
  const dqOptions = (q.options || []).map((o) => ({ key: o.id, label: o.label, onPick: pickOption(q.id, o.label), border: ans === o.label ? accent : 'rgba(47,74,63,.1)', bg: ans === o.label ? 'rgba(166,154,205,.1)' : '#FFFFFF' }));
  const strengthOptions = STRENGTHS.map(([v, label, note]) => ({ key: v, label, note, onPick: pickStrength(v), border: s.editStrength === v ? accent : 'rgba(47,74,63,.12)', bg: s.editStrength === v ? 'rgba(166,154,205,.1)' : '#FFFFFF' }));
  const modeLabel = s.mode === 'live' ? 'Live backend' : (s.mode === 'offline' ? 'Backend offline' : 'Connecting…');
  const modeDot = s.mode === 'live' ? '#4C8C6A' : (s.mode === 'offline' ? '#B04A3A' : '#C9C2B8');
  const coverageCount = (s.coverage?.me?.length || 0) + (s.coverage?.ideal_partner?.length || 0);

  let screenEl = null;
  switch (s.screen) {
    case 'welcome': screenEl = <Welcome onBegin={beginConversation} goPrivacy={goLegal('privacy')} goTerms={goLegal('terms')} />; break;
    case 'legal': screenEl = <Legal goBack={go('welcome')} section={s.legalSection} />; break;
    case 'chat': screenEl = <Chat goHome={go('home')} messages={s.messages} thinking={s.thinking} categoriesCoveredCount={coverageCount} totalCategories={BASE_CATEGORIES.length * 2} draft={s.draft} onDraft={onDraft} onDraftKey={onDraftKey} sendMessage={sendMessage} readyToComplete={s.readyToComplete} completeConversation={completeConversation} chatEndRef={chatEndRef} setDraft={setDraft} error={s.error && s.error.screen === 'chat' ? s.error.message : null} onRetryStart={!s.convoId ? beginConversation : null} />; break;
    case 'enough': screenEl = <Enough signalCount={s.signals.length} goBlueprint={go('blueprint')} groups={groups} />; break;
    case 'blueprint': screenEl = <Blueprint goHome={go('home')} groups={groups} signalCount={s.signals.length} narrative={s.narrative} />; break;
    case 'home': screenEl = <Home readiness={readiness} ready={readiness === 100} readinessHeadline={readinessCopy[0]} readinessSub={readinessCopy[1]} insight={s.insight} steps={steps} openPlans={openPlans} goBlueprint={go('blueprint')} goTalk={beginConversation} goDiscover={startDiscovery} signalCount={s.signals.length} discoverySaving={s.discoverySaving} discoverySaveError={s.discoverySaveError} retryDiscovery={retryDiscovery} />; break;
    case 'convos': screenEl = <Convos convoStatus={s.convoCompleted ? 'Completed · ' + s.turnCount + ' turns' : (s.messages.length ? 'In progress' : 'Not started')} convoCta={s.convoCompleted ? 'Continue' : (s.messages.length ? 'Resume' : 'Start')} resumeConversation={resumeConversation} discoveryState={s.discoveryDone ? 'Completed — see your insight' : (s.discoverySaving ? 'Adding to your Blueprint…' : 'Not started yet')} startDiscovery={startDiscovery} />; break;
    case 'discovery': screenEl = <Discovery discoveryUnavailable={s.questions.length === 0} discoveryBack={discoveryBack} discoveryProgress={Math.round(((s.dqIdx + (answered ? 1 : 0)) / s.questions.length) * 100) + '%'} discoveryCounter={(s.dqIdx + 1) + '/' + s.questions.length} dqPrompt={q.prompt} dqIsChoice={!isSpectrum} dqOptions={dqOptions} dqIsSpectrum={isSpectrum} dqLeft={isSpectrum ? q.spectrum[0] : ''} dqRight={isSpectrum ? q.spectrum[1] : ''} dqValue={sv} onSpectrum={onSpectrum} dqReading={reading} dqNextLabel={!answered ? (isSpectrum ? 'Move the slider' : 'Pick one') : (last ? 'Add to my Blueprint' : 'Next')} dqNextBg={answered ? SAGE : 'rgba(47,74,63,.28)'} discoveryNext={discoveryNext} error={null} />; break;
    case 'insight': screenEl = <Insight insight={s.insight} newSignals={s.newSignals} readiness={readiness} goHome={go('home')} />; break;
    case 'matches': screenEl = <Matches matches={s.matches} loading={s.matchesLoading} ready={s.matchesReady} error={s.error && s.error.screen === 'matches' ? s.error.message : null} onRetry={fetchMatches} goHome={go('home')} />; break;
    case 'friends': screenEl = <Friends />; break;
    case 'profile': screenEl = <Profile gender={s.gender} onPickGender={pickGender} ageMax={s.ageMax} onAge={onAge} breakdownMet={breakdownMet} openPlans={openPlans} resetAll={resetAll} />; break;
    default: screenEl = null;
  }

  return (
    <PhoneFrame framed={s.framed} onToggleFrame={toggleFrame} modeLabel={modeLabel} modeDot={modeDot}>
      {screenEl}
      {TAB_SCREENS.includes(s.screen) && <TabBar activeScreen={s.screen} onGo={(key) => (key === 'matches' ? goMatches() : go(key)())} />}
      {s.editing && <SignalEditSheet editLabel={s.editLabel} onEditLabel={onEditLabel} closeEdit={closeEdit} saveEdit={saveEdit} strengthOptions={strengthOptions} />}
      {s.plansOpen && <PlansModal closePlans={closePlans} />}
    </PhoneFrame>
  );
}
