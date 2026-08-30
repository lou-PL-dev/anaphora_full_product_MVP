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
import { apiCall, getOrCreateUserId, TIMEOUT_CHAT_REPLY, TIMEOUT_EXTRACTION, TIMEOUT_INSIGHT } from './api';
import { mockReadiness } from './readiness';
import { GROUP_DEFS, STRENGTHS, STRENGTH_STYLE } from './data';
import { LAV, SAGE } from './theme';

const TAB_SCREENS = ['home', 'convos', 'matches', 'friends', 'profile'];

const initialState = {
  screen: 'welcome', framed: false, mode: 'checking',
  convoId: null, messages: [], draft: '', thinking: false,
  turnCount: 0, readyToComplete: false,
  signals: [], readiness: 0, insight: '', newSignals: [],
  questions: [], dqIdx: 0, answers: {},
  discoveryDone: false, convoCompleted: false,
  editing: null, editLabel: '', editStrength: 'preference',
  plansOpen: false, whyOpen: false,
  gender: null, ageMax: 36,
  // { screen: 'chat' | 'discovery', message: string } | null — a real
  // backend/LLM failure, surfaced in place rather than masked with
  // fabricated content.
  error: null,
};

export default function App() {
  const [s, setS] = useState(initialState);
  const uidRef = useRef(null);
  const chatEndRef = useRef(null);

  const patch = (update) => setS((prev) => ({ ...prev, ...(typeof update === 'function' ? update(prev) : update) }));
  // Central place that tracks real backend connectivity — `mode` reflects
  // whichever call most recently succeeded or failed. It's just the status
  // pill; it never decides what content to show (see the per-action error
  // handling below, which is what actually replaced the old silent
  // mock-data fallback).
  const api = async (method, path, body, timeoutMs) => {
    const r = await apiCall(uidRef.current, method, path, body, timeoutMs);
    patch({ mode: r === null ? 'offline' : 'live' });
    return r;
  };

  useEffect(() => {
    uidRef.current = getOrCreateUserId();
    api('GET', '/discovery/life_you_are_building').then((r) => {
      if (r && r.questions) patch({ questions: r.questions });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const el = chatEndRef.current;
    if (el && el.parentElement) el.parentElement.scrollTop = el.parentElement.scrollHeight;
  }, [s.messages, s.thinking]);

  // --- navigation ---
  const go = (screen) => () => patch({ screen, whyOpen: false, error: null });

  const beginConversation = async () => {
    patch({ screen: 'chat', messages: [], turnCount: 0, readyToComplete: false, convoId: null, error: null });
    const r = await api('POST', '/conversation/start');
    if (r) {
      patch({ convoId: r.conversation_id, messages: [{ role: 'assistant', content: r.message }] });
    } else {
      patch({ error: { screen: 'chat', message: "Couldn't reach the backend to start the conversation. Check it's running, then retry." } });
    }
  };

  const resumeConversation = () => {
    if (s.messages.length) patch({ screen: 'chat' });
    else beginConversation();
  };

  const onDraft = (e) => patch({ draft: e.target.value });
  const setDraft = (text) => patch({ draft: text });
  const onDraftKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

  const sendMessage = async () => {
    const text = s.draft.trim();
    if (!text || s.thinking) return;
    patch((prev) => ({ messages: prev.messages.concat([{ role: 'user', content: text }]), draft: '', thinking: true, error: null }));
    const r = await api('POST', '/conversation/message', { conversation_id: s.convoId, message: text }, TIMEOUT_CHAT_REPLY);
    if (r) {
      patch((prev) => ({ thinking: false, messages: prev.messages.concat([{ role: 'assistant', content: r.reply }]), readyToComplete: r.ready_to_complete, turnCount: r.turn_count }));
    } else {
      // Roll back the optimistic bubble — the backend never actually saw
      // this turn — and hand the text back to the draft box so retrying is
      // just hitting send again.
      patch((prev) => ({
        thinking: false,
        messages: prev.messages.slice(0, -1),
        draft: text,
        error: { screen: 'chat', message: "Anaphora didn't respond in time. Check the backend is running, then send again." },
      }));
    }
  };

  const completeConversation = async () => {
    patch({ error: null });
    const r = await api('POST', '/conversation/complete', { conversation_id: s.convoId }, TIMEOUT_EXTRACTION);
    if (r) {
      patch({ signals: r.signals, readiness: r.readiness_pct, convoCompleted: true, screen: 'enough' });
    } else {
      patch({ error: { screen: 'chat', message: "Couldn't build your Blueprint — the request timed out or the backend is unreachable. Tap “Create my Blueprint” to try again." } });
    }
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
  const startDiscovery = () => patch({ screen: 'discovery', dqIdx: 0, answers: {}, error: null });
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
    if (dqIdx < questions.length - 1) { patch({ dqIdx: dqIdx + 1, error: null }); return; }
    patch({ error: null });
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
    const r = await api('POST', '/discovery/life_you_are_building/respond', payload, TIMEOUT_INSIGHT);
    if (r) {
      patch((prev) => ({ insight: r.insight_text, newSignals: r.new_signals, signals: prev.signals.concat(r.new_signals), readiness: r.readiness_pct, discoveryDone: true, screen: 'insight' }));
    } else {
      patch({ error: { screen: 'discovery', message: "Couldn't generate your insight — check the backend is running, then try again." } });
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

  // Only a defensive placeholder for a stale render mid-navigation — the
  // Discovery screen itself refuses to render real question UI (see
  // discoveryUnavailable below) whenever s.questions is actually empty.
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

  const modeLabel = s.mode === 'live' ? 'Live backend' : (s.mode === 'offline' ? 'Backend offline' : 'Connecting…');
  const modeDot = s.mode === 'live' ? '#4C8C6A' : (s.mode === 'offline' ? '#B04A3A' : '#C9C2B8');

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
          setDraft={setDraft}
          error={s.error && s.error.screen === 'chat' ? s.error.message : null}
          onRetryStart={!s.convoId ? beginConversation : null}
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
          discoveryUnavailable={s.questions.length === 0}
          discoveryBack={discoveryBack}
          discoveryProgress={Math.round(((s.dqIdx + (answered ? 1 : 0)) / s.questions.length) * 100) + '%'}
          discoveryCounter={(s.dqIdx + 1) + '/' + s.questions.length}
          dqPrompt={q.prompt} dqIsChoice={!isSpectrum} dqOptions={dqOptions} dqIsSpectrum={isSpectrum}
          dqLeft={isSpectrum ? q.spectrum[0] : ''} dqRight={isSpectrum ? q.spectrum[1] : ''}
          dqValue={sv} onSpectrum={onSpectrum} dqReading={reading}
          dqNextLabel={!answered ? (isSpectrum ? 'Move the slider' : 'Pick one') : (last ? 'See what I noticed' : 'Next')}
          dqNextBg={answered ? SAGE : 'rgba(47,74,63,.28)'}
          discoveryNext={discoveryNext}
          error={s.error && s.error.screen === 'discovery' ? s.error.message : null}
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
