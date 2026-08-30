import { useEffect, useRef, useState } from 'react';
import PhoneFrame from './components/PhoneFrame';
import TabBar from './components/TabBar';
import SignalEditSheet from './components/SignalEditSheet';
import PlansModal from './components/PlansModal';
import Welcome from './screens/Welcome';
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
import { apiCall, getOrCreateUserId } from './api';
import { mockReadiness } from './readiness';
import { FALLBACK_QUESTIONS, GROUP_DEFS, MOCK_REPLIES, MOCK_SIGNALS, STRENGTHS, STRENGTH_STYLE } from './data';
import { LAV, SAGE } from './theme';

const TAB_SCREENS = ['home', 'convos', 'matches', 'friends', 'profile'];

const initialState = {
  screen: 'welcome', framed: true, mode: 'checking',
  convoId: null, messages: [], draft: '', thinking: false,
  turnCount: 0, readyToComplete: false,
  signals: [], readiness: 0, insight: '', newSignals: [],
  questions: FALLBACK_QUESTIONS, dqIdx: 0, answers: {},
  discoveryDone: false, convoCompleted: false,
  editing: null, editLabel: '', editStrength: 'preference',
  plansOpen: false, whyOpen: false,
  gender: null, ageMax: 36,
};

export default function App() {
  const [s, setS] = useState(initialState);
  const uidRef = useRef(null);
  const chatEndRef = useRef(null);

  const patch = (update) => setS((prev) => ({ ...prev, ...(typeof update === 'function' ? update(prev) : update) }));
  const api = (method, path, body) => apiCall(uidRef.current, method, path, body);

  useEffect(() => {
    uidRef.current = getOrCreateUserId();
    api('GET', '/discovery/life_you_are_building').then((r) => {
      if (r && r.questions) patch({ questions: r.questions, mode: 'live' });
      else patch({ mode: 'demo' });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const el = chatEndRef.current;
    if (el && el.parentElement) el.parentElement.scrollTop = el.parentElement.scrollHeight;
  }, [s.messages, s.thinking]);

  // --- navigation ---
  const go = (screen) => () => patch({ screen, whyOpen: false });

  const beginConversation = async () => {
    patch({ screen: 'chat', messages: [], turnCount: 0, readyToComplete: false });
    const r = await api('POST', '/conversation/start');
    const opening = "Tell me about the person you'd love to meet.";
    patch({ convoId: r ? r.conversation_id : 'demo', messages: [{ role: 'assistant', content: r ? r.message : opening }] });
  };

  const resumeConversation = () => {
    if (s.messages.length) patch({ screen: 'chat' });
    else beginConversation();
  };

  const onDraft = (e) => patch({ draft: e.target.value });
  const onDraftKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

  const sendMessage = async () => {
    const text = s.draft.trim();
    if (!text || s.thinking) return;
    const msgs = s.messages.concat([{ role: 'user', content: text }]);
    const turns = s.turnCount + 1;
    patch({ messages: msgs, draft: '', thinking: true, turnCount: turns });
    const r = await api('POST', '/conversation/message', { conversation_id: s.convoId, message: text });
    const reply = r ? r.reply : MOCK_REPLIES[Math.min(turns - 1, MOCK_REPLIES.length - 1)];
    const ready = r ? r.ready_to_complete : turns >= 4;
    patch((prev) => ({ thinking: false, messages: prev.messages.concat([{ role: 'assistant', content: reply }]), readyToComplete: ready, turnCount: r ? r.turn_count : turns }));
  };

  const completeConversation = async () => {
    const r = await api('POST', '/conversation/complete', { conversation_id: s.convoId });
    let signals, readiness;
    if (r) {
      signals = r.signals; readiness = r.readiness_pct;
    } else {
      signals = MOCK_SIGNALS.map((m, i) => ({ id: 'm' + i, perspective: m[0], category: m[1], label: m[2], strength: m[3], evidence_text: m[4], source: 'conversation' }));
      readiness = mockReadiness(signals, s.discoveryDone, s.gender).total;
    }
    patch({ signals, readiness, convoCompleted: true, screen: 'enough' });
  };

  // --- blueprint editing ---
  const openEdit = (sig) => () => patch({ editing: sig, editLabel: sig.label, editStrength: sig.strength });
  const closeEdit = () => patch({ editing: null });
  const onEditLabel = (e) => patch({ editLabel: e.target.value });
  const pickStrength = (v) => () => patch({ editStrength: v });
  const saveEdit = async () => {
    const { editing, editLabel, editStrength } = s;
    patch((prev) => ({
      editing: null,
      signals: prev.signals.map((x) => (x.id === editing.id ? { ...x, label: editLabel, strength: editStrength } : x)),
    }));
    await api('PATCH', '/blueprint/signal/' + editing.id, { label: editLabel, strength: editStrength });
  };

  // --- discovery ---
  const startDiscovery = () => patch({ screen: 'discovery', dqIdx: 0, answers: {} });
  const discoveryBack = () => {
    if (s.dqIdx === 0) patch({ screen: 'home' });
    else patch((prev) => ({ dqIdx: prev.dqIdx - 1 }));
  };
  const pickOption = (qid, label) => () => patch((prev) => ({ answers: { ...prev.answers, [qid]: label } }));
  const onSpectrum = (e) => {
    const q = s.questions[s.dqIdx];
    const v = Number(e.target.value);
    patch((prev) => ({ answers: { ...prev.answers, [q.id]: v } }));
  };
  const discoveryNext = async () => {
    const { dqIdx, questions, answers } = s;
    const q = questions[dqIdx];
    if (answers[q.id] === undefined) return;
    if (dqIdx < questions.length - 1) { patch({ dqIdx: dqIdx + 1 }); return; }
    const payload = questions.map((qq) => {
      const a = answers[qq.id];
      let response = String(a);
      if (qq.spectrum) {
        const v = Number(a);
        response = v < 45 ? qq.spectrum[0] : (v > 55 ? qq.spectrum[1] : 'Balanced between ' + qq.spectrum[0] + ' and ' + qq.spectrum[1]);
        response = response + ' (' + v + '/100 toward ' + qq.spectrum[1] + ')';
      } else if (qq.options) {
        const o = qq.options.find((x) => x.label === a);
        response = o ? o.id : String(a);
      }
      return { user_id: uidRef.current, question_id: qq.id, response };
    });
    const r = await api('POST', '/discovery/life_you_are_building/respond', payload);
    if (r) {
      patch((prev) => ({ insight: r.insight_text, newSignals: r.new_signals, signals: prev.signals.concat(r.new_signals), readiness: r.readiness_pct, discoveryDone: true, screen: 'insight' }));
    } else {
      const mockNew = payload.map((p, i) => ({ id: 'd' + i, perspective: 'ME', category: 'lifestyle', source: 'discovery', strength: 'preference', label: p.question_id === 'saturday_2032' ? 'Home-oriented, family-centered' : 'Leans toward: ' + p.response.split(' (')[0], evidence_text: null }));
      const signals = s.signals.concat(mockNew);
      patch({ insight: 'You want strong roots without feeling stuck.', newSignals: mockNew, signals, readiness: mockReadiness(signals, true, s.gender).total, discoveryDone: true, screen: 'insight' });
    }
  };

  // --- profile ---
  const pickGender = (v) => patch((prev) => ({ gender: v, readiness: prev.mode === 'live' ? prev.readiness : mockReadiness(prev.signals, prev.discoveryDone, v).total }));
  const onAge = (e) => patch({ ageMax: Number(e.target.value) });
  const resetAll = () => patch({
    screen: 'welcome', messages: [], signals: [], readiness: 0, insight: '', newSignals: [],
    answers: {}, dqIdx: 0, discoveryDone: false, convoCompleted: false, turnCount: 0,
    readyToComplete: false, gender: null,
  });

  const toggleFrame = () => patch((prev) => ({ framed: !prev.framed }));
  const toggleWhy = () => patch((prev) => ({ whyOpen: !prev.whyOpen }));
  const openPlans = () => patch({ plansOpen: true });
  const closePlans = () => patch({ plansOpen: false });

  // --- derived render values (mirrors Component.renderVals in the prototype) ---
  const accent = LAV;

  const groups = GROUP_DEFS.map(([persp, cat, title, side]) => {
    const items = s.signals
      .filter((x) => x.perspective === persp && (cat ? x.category === cat : true))
      .map((x) => {
        const st = STRENGTH_STYLE[x.strength] || STRENGTH_STYLE.preference;
        return { id: x.id, label: x.label, evidence: x.evidence_text || '', strengthLabel: st.label, dot: st.dot, pillBg: st.bg, pillFg: st.fg, onEdit: openEdit(x) };
      });
    return { title, side, items };
  }).filter((g) => g.items.length);

  const br = mockReadiness(s.signals, s.discoveryDone, s.gender);
  const readiness = s.mode === 'live' && s.readiness ? s.readiness : br.total;

  const steps = [
    { key: 'convo', title: "Tell me who you're looking for", note: s.convoCompleted ? 'Blueprint created' : 'One conversation, about 3 minutes', done: s.convoCompleted, cta: s.convoCompleted ? 'Add more' : 'Start', onGo: s.convoCompleted ? go('convos') : beginConversation },
    { key: 'disc', title: 'What kind of life are you building?', note: s.discoveryDone ? 'Insight added to your Blueprint' : 'A Discovery — 4 questions', done: s.discoveryDone, cta: s.discoveryDone ? 'Done' : '2 min', onGo: s.discoveryDone ? go('insight') : startDiscovery },
    { key: 'prefs', title: 'Basic matching preferences', note: s.gender ? s.gender + ' · 24–' + s.ageMax : 'Who and what age range', done: !!s.gender, cta: s.gender ? 'Edit' : 'Set', onGo: go('profile') },
    { key: 'friends', title: 'Ask a friend to describe you', note: '3 friends have already answered', done: true, cta: 'View', onGo: go('friends') },
  ].map((st) => ({ ...st, mark: st.done ? '✓' : '', ring: st.done ? SAGE : 'rgba(47,74,63,.22)', fill: st.done ? SAGE : 'transparent' }));

  const q = s.questions[s.dqIdx] || FALLBACK_QUESTIONS[0];
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

  const readinessCopy = readiness >= 90
    ? ['Ready when you are', 'We know enough to look for people who actually fit.']
    : readiness >= 60
      ? ['Coming into focus', 'A little more and matches start making real sense.']
      : readiness > 0
        ? ['A good beginning', 'Every answer sharpens who we look for.']
        : ['Nothing yet', 'One conversation is all it takes to start.'];

  const dqOptions = (q.options || []).map((o) => ({
    key: o.id, label: o.label, onPick: pickOption(q.id, o.label),
    border: ans === o.label ? accent : 'rgba(47,74,63,.1)',
    bg: ans === o.label ? 'rgba(166,154,205,.1)' : '#FFFFFF',
  }));

  const strengthOptions = STRENGTHS.map(([v, label, note]) => ({
    key: v, label, note, onPick: pickStrength(v),
    border: s.editStrength === v ? accent : 'rgba(47,74,63,.12)',
    bg: s.editStrength === v ? 'rgba(166,154,205,.1)' : '#FFFFFF',
  }));

  const modeLabel = s.mode === 'live' ? 'Live backend' : (s.mode === 'demo' ? 'Demo data' : 'Connecting…');
  const modeDot = s.mode === 'live' ? '#4C8C6A' : (s.mode === 'demo' ? accent : '#C9C2B8');

  let screenEl = null;
  switch (s.screen) {
    case 'welcome':
      screenEl = <Welcome onBegin={beginConversation} />;
      break;
    case 'chat':
      screenEl = (
        <Chat
          goHome={go('home')} messages={s.messages} turnCount={s.turnCount} thinking={s.thinking}
          draft={s.draft} onDraft={onDraft} onDraftKey={onDraftKey} sendMessage={sendMessage}
          readyToComplete={s.readyToComplete} completeConversation={completeConversation} chatEndRef={chatEndRef}
        />
      );
      break;
    case 'enough':
      screenEl = <Enough signalCount={s.signals.length} goBlueprint={go('blueprint')} groups={groups} />;
      break;
    case 'blueprint':
      screenEl = <Blueprint goHome={go('home')} groups={groups} signalCount={s.signals.length} />;
      break;
    case 'home':
      screenEl = (
        <Home
          readiness={readiness} readinessHeadline={readinessCopy[0]} readinessSub={readinessCopy[1]}
          insight={s.insight} steps={steps} openPlans={openPlans} goBlueprint={go('blueprint')}
          signalCount={s.signals.length}
        />
      );
      break;
    case 'convos':
      screenEl = (
        <Convos
          convoStatus={s.convoCompleted ? 'Completed · ' + s.turnCount + ' turns' : (s.messages.length ? 'In progress' : 'Not started')}
          convoCta={s.convoCompleted ? 'Continue' : (s.messages.length ? 'Resume' : 'Start')}
          resumeConversation={resumeConversation}
          discoveryState={s.discoveryDone ? 'Completed — see your insight' : 'Not started yet'}
          startDiscovery={startDiscovery}
        />
      );
      break;
    case 'discovery':
      screenEl = (
        <Discovery
          discoveryBack={discoveryBack}
          discoveryProgress={Math.round(((s.dqIdx + (answered ? 1 : 0)) / s.questions.length) * 100) + '%'}
          discoveryCounter={(s.dqIdx + 1) + '/' + s.questions.length}
          dqPrompt={q.prompt} dqIsChoice={!isSpectrum} dqOptions={dqOptions} dqIsSpectrum={isSpectrum}
          dqLeft={isSpectrum ? q.spectrum[0] : ''} dqRight={isSpectrum ? q.spectrum[1] : ''}
          dqValue={sv} onSpectrum={onSpectrum} dqReading={reading}
          dqNextLabel={!answered ? (isSpectrum ? 'Move the slider' : 'Pick one') : (last ? 'See what I noticed' : 'Next')}
          dqNextBg={answered ? SAGE : 'rgba(47,74,63,.28)'}
          discoveryNext={discoveryNext}
        />
      );
      break;
    case 'insight':
      screenEl = <Insight insight={s.insight} newSignals={s.newSignals} readiness={readiness} goHome={go('home')} />;
      break;
    case 'matches':
      screenEl = <Matches whyOpen={s.whyOpen} toggleWhy={toggleWhy} />;
      break;
    case 'friends':
      screenEl = <Friends />;
      break;
    case 'profile':
      screenEl = (
        <Profile
          gender={s.gender} onPickGender={pickGender} ageMax={s.ageMax} onAge={onAge}
          breakdownMet={br.met} openPlans={openPlans} resetAll={resetAll}
        />
      );
      break;
    default:
      screenEl = null;
  }

  return (
    <PhoneFrame framed={s.framed} onToggleFrame={toggleFrame} modeLabel={modeLabel} modeDot={modeDot}>
      {screenEl}
      {TAB_SCREENS.includes(s.screen) && <TabBar activeScreen={s.screen} onGo={(key) => go(key)()} />}
      {s.editing && (
        <SignalEditSheet
          editLabel={s.editLabel} onEditLabel={onEditLabel}
          closeEdit={closeEdit} saveEdit={saveEdit} strengthOptions={strengthOptions}
        />
      )}
      {s.plansOpen && <PlansModal closePlans={closePlans} />}
    </PhoneFrame>
  );
}
