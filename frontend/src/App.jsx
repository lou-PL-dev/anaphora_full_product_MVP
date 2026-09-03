import { useEffect, useRef, useState } from 'react';
import PhoneFrame from './components/PhoneFrame';
import TabBar from './components/TabBar';
import SignalEditSheet from './components/SignalEditSheet';
import PlansModal from './components/PlansModal';
import InviteLinkSheet from './components/InviteLinkSheet';
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
import FriendReview from './screens/FriendReview';
import Profile from './screens/Profile';
import { apiCall, getOrCreateUserId, TIMEOUT_CHAT_REPLY, TIMEOUT_EXTRACTION, TIMEOUT_INSIGHT, TIMEOUT_MATCHES } from './api';
import { mockReadiness } from './readiness';
import { BASE_CATEGORIES, GROUP_DEFS, STRENGTHS, STRENGTH_STYLE, DISCOVERY_LIBRARY, FRIEND_INVITE_LIMIT } from './data';
import { LAV, SAGE } from './theme';

const TAB_SCREENS = ['home', 'convos', 'matches', 'friends', 'profile'];
const DEFAULT_DISCOVERY_ID = 'life_you_are_building';
const introVisitedStorageKey = (uid) => `anaphora:intro-visited:${uid}`;

const readIntroVisited = (uid) => {
  try {
    return localStorage.getItem(introVisitedStorageKey(uid)) === 'true';
  } catch {
    return false;
  }
};

const rememberIntroVisited = (uid) => {
  try {
    localStorage.setItem(introVisitedStorageKey(uid), 'true');
  } catch {
    // The in-memory state still keeps the transition working for this session.
  }
};

const initialState = {
  screen: 'welcome', framed: false, mode: 'checking',
  convoId: null, messages: [], draft: '', thinking: false,
  turnCount: 0, readyToComplete: false, categoriesCovered: [],
  signals: [], readiness: 0, narrative: '', insight: '', newSignals: [], hasExistingBlueprint: false, wasFollowUp: false,
  discoveryId: DEFAULT_DISCOVERY_ID, discoveryTitle: '', discoveryReturnScreen: 'home', discoveryLoading: false,
  questions: [], dqIdx: 0, answers: {}, completedDiscoveries: [], suggestedDiscoveryId: null,
  blueprintScrollAboutYou: false,
  discoveryDone: false, discoverySaving: false, discoverySaveError: false, convoCompleted: false,
  editing: null, editLabel: '', editStrength: 'preference',
  plansOpen: false, inviteOpen: false, copied: false,
  gender: null, ageMin: 18, ageMax: 99,
  preferencesSaved: false, preferencesSaving: false, preferencesError: null,
  matches: [], matchesLoading: false, matchesLoaded: false, matchesReady: null, hasVisitedReadyMatches: false,
  legalSection: 'privacy', error: null,
  friends: [], inviteCreating: false, inviteToken: null, inviteError: null,
  friendReviewInviteId: null, friendReview: null, friendReviewLoading: false, friendReviewSelected: [],
  friendCommitting: false, friendCommitted: false, friendAddedCount: 0,
};

export default function App() {
  const [s, setS] = useState(initialState);
  const uidRef = useRef(null);
  const chatEndRef = useRef(null);
  const copyTimerRef = useRef(null);
  const patch = (update) => setS((prev) => ({ ...prev, ...(typeof update === 'function' ? update(prev) : update) }));
  const api = async (method, path, body, timeoutMs) => {
    const r = await apiCall(uidRef.current, method, path, body, timeoutMs);
    patch({ mode: r === null ? 'offline' : 'live' });
    return r;
  };

  useEffect(() => {
    uidRef.current = getOrCreateUserId();
    if (readIntroVisited(uidRef.current)) patch({ hasVisitedReadyMatches: true });
    api('GET', '/discovery/' + DEFAULT_DISCOVERY_ID).then((r) => {
      if (r && r.questions) patch({ questions: r.questions, discoveryTitle: r.title || 'What kind of life are you building?' });
    });
    api('GET', '/blueprint').then((r) => {
      if (r) patch({ signals: r.signals || [], narrative: r.narrative || '', hasExistingBlueprint: !!(r.signals && r.signals.length) });
    });
    api('GET', '/readiness').then((r) => {
      if (!r) return;
      patch((prev) => ({ readiness: r.readiness_pct, screen: r.readiness_pct > 0 && prev.screen === 'welcome' ? 'home' : prev.screen }));
    });
    api('GET', '/preferences').then((r) => {
      if (r && r.gender_preference) patch({ gender: r.gender_preference, ageMin: r.age_min ?? 18, ageMax: r.age_max ?? 99, preferencesSaved: true });
    });
    api('GET', '/discovery').then((r) => {
      if (Array.isArray(r)) {
        const completed = r.filter((d) => d.completed).map((d) => d.id);
        patch({ completedDiscoveries: completed, discoveryDone: completed.includes(DEFAULT_DISCOVERY_ID) });
      }
    });
    api('GET', '/friends').then((r) => { if (Array.isArray(r)) patch({ friends: r }); });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const el = chatEndRef.current;
    if (el && el.parentElement) el.parentElement.scrollTop = el.parentElement.scrollHeight;
  }, [s.messages, s.thinking]);

  useEffect(() => {
    const notDone = DISCOVERY_LIBRARY.filter((d) => !s.completedDiscoveries.includes(d.id));
    if (notDone.length === 0) {
      if (s.suggestedDiscoveryId !== null) patch({ suggestedDiscoveryId: null });
      return;
    }
    if (s.suggestedDiscoveryId && notDone.some((d) => d.id === s.suggestedDiscoveryId)) return;
    const pick = notDone[Math.floor(Math.random() * notDone.length)];
    patch({ suggestedDiscoveryId: pick.id });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [s.completedDiscoveries]);

  const go = (screen) => () => patch({ screen, error: null });
  const goLegal = (legalSection) => () => patch({ screen: 'legal', legalSection, error: null });
  const goBlueprintAboutYou = () => patch({ screen: 'blueprint', blueprintScrollAboutYou: true, error: null });
  const clearBlueprintScroll = () => patch({ blueprintScrollAboutYou: false });

  const beginConversation = async () => {
    patch({ screen: 'chat', messages: [], turnCount: 0, readyToComplete: false, categoriesCovered: [], convoId: null, convoCompleted: false, error: null });
    const r = await api('POST', '/conversation/start');
    if (r) patch({ convoId: r.conversation_id, messages: [{ role: 'assistant', content: r.message }] });
    else patch({ error: { screen: 'chat', message: "Couldn't reach the backend to start the conversation. Check it's running, then retry." } });
  };
  const resumeConversation = () => { if (s.messages.length && !s.convoCompleted) patch({ screen: 'chat' }); else beginConversation(); };
  const onDraft = (e) => patch({ draft: e.target.value });
  const setDraft = (text) => patch({ draft: text });
  const onDraftKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };
  const sendMessage = async () => {
    const text = s.draft.trim();
    if (!text || s.thinking) return;
    patch((prev) => ({ messages: prev.messages.concat([{ role: 'user', content: text }]), draft: '', thinking: true, error: null }));
    const r = await api('POST', '/conversation/message', { conversation_id: s.convoId, message: text }, TIMEOUT_CHAT_REPLY);
    if (r) patch((prev) => ({ thinking: false, messages: prev.messages.concat([{ role: 'assistant', content: r.reply }]), readyToComplete: r.ready_to_complete, turnCount: r.turn_count, categoriesCovered: r.categories_covered }));
    else patch((prev) => ({ thinking: false, messages: prev.messages.slice(0, -1), draft: text, error: { screen: 'chat', message: "Anaphora didn't respond in time. Check the backend is running, then send again." } }));
  };
  const completeConversation = async () => {
    patch({ error: null });
    const wasFollowUp = s.hasExistingBlueprint;
    const r = await api('POST', '/conversation/complete', { conversation_id: s.convoId }, TIMEOUT_EXTRACTION);
    if (r) {
      const full = await api('GET', '/blueprint');
      patch({ signals: full ? full.signals || [] : r.signals, narrative: full ? full.narrative || '' : r.narrative, readiness: r.readiness_pct, convoCompleted: true, hasExistingBlueprint: true, wasFollowUp, screen: 'enough' });
    } else patch({ error: { screen: 'chat', message: "Couldn't build your Blueprint — the request timed out or the backend is unreachable. Tap the button to try again." } });
  };

  const fetchMatches = async () => {
    patch({ matchesLoading: true, error: null });
    const r = await api('GET', '/matches', undefined, TIMEOUT_MATCHES);
    if (r) {
      if (r.ready) rememberIntroVisited(uidRef.current);
      patch((prev) => ({ matches: r.matches, matchesReady: r.ready, matchesLoading: false, matchesLoaded: r.ready, hasVisitedReadyMatches: prev.hasVisitedReadyMatches || r.ready }));
    }
    else patch({ matchesLoading: false, error: { screen: 'matches', message: "Couldn't load your matches — check the backend is running, then try again." } });
  };
  const goMatches = () => {
    const shouldRememberVisit = s.readiness >= 100 || s.matchesReady === true;
    if (shouldRememberVisit) rememberIntroVisited(uidRef.current);
    patch((prev) => ({ screen: 'matches', error: null, hasVisitedReadyMatches: prev.hasVisitedReadyMatches || shouldRememberVisit }));
    if (!s.matchesLoaded && !s.matchesLoading) fetchMatches();
  };

  const openEdit = (sig) => () => patch({ editing: sig, editLabel: sig.label, editStrength: sig.strength });
  const closeEdit = () => patch({ editing: null });
  const onEditLabel = (e) => patch({ editLabel: e.target.value });
  const pickStrength = (v) => () => patch({ editStrength: v });
  const saveEdit = async () => {
    const { editing, editLabel, editStrength } = s;
    patch((prev) => ({ editing: null, signals: prev.signals.map((x) => (x.id === editing.id ? { ...x, label: editLabel, strength: editStrength } : x)) }));
    const saved = await api('PATCH', '/blueprint/signal/' + editing.id, { label: editLabel, strength: editStrength });
    if (saved) {
      const full = await api('GET', '/blueprint');
      if (full) patch({ signals: full.signals || [], narrative: full.narrative || '' });
    }
  };

  const startDiscovery = async (discoveryId = DEFAULT_DISCOVERY_ID, returnScreen = 'home') => {
    patch({ screen: 'discovery', discoveryId, discoveryReturnScreen: returnScreen, discoveryLoading: true, discoveryTitle: '', questions: [], dqIdx: 0, answers: {}, error: null, discoverySaveError: false });
    const r = await api('GET', '/discovery/' + discoveryId);
    if (r && r.questions) patch({ questions: r.questions, discoveryTitle: r.title || '', discoveryLoading: false });
    else patch({ discoveryLoading: false });
  };
  const discoveryBack = () => { if (s.dqIdx === 0) patch({ screen: s.discoveryReturnScreen || 'home' }); else patch((prev) => ({ dqIdx: prev.dqIdx - 1 })); };
  const pickOption = (qid, option) => () => patch((prev) => ({ answers: { ...prev.answers, [qid]: option.id === 'other' ? '__OTHER__' : option.label } }));
  const onOtherAnswer = (e) => { const q = s.questions[s.dqIdx]; patch((prev) => ({ answers: { ...prev.answers, [q.id]: 'Other: ' + e.target.value } })); };
  const onTextAnswer = (e) => { const q = s.questions[s.dqIdx]; patch((prev) => ({ answers: { ...prev.answers, [q.id]: e.target.value } })); };
  const onSpectrum = (e) => { const q = s.questions[s.dqIdx]; const v = Number(e.target.value); patch((prev) => ({ answers: { ...prev.answers, [q.id]: v } })); };

  const buildDiscoveryPayload = (questions, answers) => questions.map((qq) => {
    const a = answers[qq.id];
    let response = String(a);
    if (qq.spectrum) {
      const v = Number(a);
      response = v < 45 ? qq.spectrum[0] : (v > 55 ? qq.spectrum[1] : 'Balanced between ' + qq.spectrum[0] + ' and ' + qq.spectrum[1]);
      response += ' (' + v + '/100 toward ' + qq.spectrum[1] + ')';
    } else if (qq.options) {
      // Keep the human-readable choice in persistence/admin instead of the
      // internal option id ("a", "b", "hold_listen", etc.).
      if (String(a).startsWith('Other: ')) response = String(a).slice(7).trim();
      else response = String(a);
    }
    return { user_id: uidRef.current, question_id: qq.id, response };
  });

  const submitDiscoveryInBackground = async (questions, answers, discoveryId) => {
    const payload = buildDiscoveryPayload(questions, answers);
    patch({ discoverySaving: true, discoverySaveError: false, error: null });
    const r = await api('POST', '/discovery/' + discoveryId + '/respond', payload, TIMEOUT_INSIGHT);
    if (r) {
      const full = await api('GET', '/blueprint');
      patch((prev) => ({ insight: r.insight_text, newSignals: r.new_signals, signals: full ? full.signals || [] : prev.signals, narrative: full ? full.narrative || '' : prev.narrative, readiness: r.readiness_pct, discoveryDone: true, completedDiscoveries: prev.completedDiscoveries.includes(discoveryId) ? prev.completedDiscoveries : prev.completedDiscoveries.concat(discoveryId), discoverySaving: false, discoverySaveError: false }));
    } else patch({ discoverySaving: false, discoverySaveError: true });
  };

  const discoveryNext = () => {
    const { dqIdx, questions, answers, discoveryId, discoveryReturnScreen } = s;
    const q = questions[dqIdx];
    const answer = answers[q.id];
    const otherSelected = answer === '__OTHER__' || String(answer || '').startsWith('Other: ');
    const answered = q.text ? !!String(answer || '').trim() : otherSelected ? String(answer || '').replace(/^Other:\s*/, '').trim().length > 0 : answer !== undefined;
    if (!answered) return;
    if (dqIdx < questions.length - 1) { patch({ dqIdx: dqIdx + 1, error: null }); return; }
    patch({ screen: discoveryReturnScreen === 'convos' ? 'convos' : 'home', discoverySaving: true, discoverySaveError: false, error: null });
    submitDiscoveryInBackground(questions, answers, discoveryId);
  };
  const retryDiscovery = () => {
    if (s.discoverySaving || !s.questions.length || !Object.keys(s.answers).length) return;
    submitDiscoveryInBackground(s.questions, s.answers, s.discoveryId);
  };

  const pickGender = (v) => patch({ gender: v, preferencesSaved: false, preferencesError: null });
  const onAgeMin = (e) => { const value = Number(e.target.value); patch((prev) => ({ ageMin: Math.min(value, prev.ageMax), preferencesSaved: false, preferencesError: null })); };
  const onAgeMax = (e) => { const value = Number(e.target.value); patch((prev) => ({ ageMax: Math.max(value, prev.ageMin), preferencesSaved: false, preferencesError: null })); };
  const savePreferences = async () => {
    if (!s.gender || s.preferencesSaving) return;
    patch({ preferencesSaving: true, preferencesError: null });
    const r = await api('PATCH', '/preferences', { gender_preference: s.gender, age_min: s.ageMin, age_max: s.ageMax });
    if (r) patch({ preferencesSaving: false, preferencesSaved: true, readiness: r.readiness_pct, matches: [], matchesLoaded: false, matchesReady: null });
    else patch({ preferencesSaving: false, preferencesSaved: false, preferencesError: "We couldn't save your preferences. Please try again." });
  };

  const openFriendReview = async (inviteId) => {
    patch({ screen: 'friendReview', friendReviewInviteId: inviteId, friendReviewLoading: true, friendReview: null, friendReviewSelected: [], friendCommitted: false, friendAddedCount: 0, error: null });
    const r = await api('GET', '/friends/' + inviteId + '/review');
    if (r) patch({ friendReview: r, friendReviewLoading: false });
    else patch({ friendReviewLoading: false, error: { screen: 'friendReview', message: "Couldn't load this friend's answers." } });
  };
  const toggleFriendSignal = (signalId) => patch((prev) => ({ friendReviewSelected: prev.friendReviewSelected.includes(signalId) ? prev.friendReviewSelected.filter((id) => id !== signalId) : prev.friendReviewSelected.concat(signalId) }));
  const commitFriendReview = async () => {
    if (s.friendCommitting || !s.friendReviewInviteId) return;
    patch({ friendCommitting: true, error: null });
    const r = await api('POST', '/friends/' + s.friendReviewInviteId + '/commit', { accepted_signal_ids: s.friendReviewSelected });
    if (r) {
      const full = await api('GET', '/blueprint');
      patch((prev) => ({ friendCommitting: false, friendCommitted: true, friendAddedCount: r.added_signals.length, signals: full ? full.signals || [] : prev.signals, narrative: full ? full.narrative || '' : prev.narrative, readiness: r.readiness_pct, friends: prev.friends.map((f) => (f.id === prev.friendReviewInviteId ? { ...f, reviewed: true } : f)) }));
    }
    else patch({ friendCommitting: false, error: { screen: 'friendReview', message: "Couldn't save your choices. Please try again." } });
  };

  const resetAll = () => {
    const newUid = crypto.randomUUID ? crypto.randomUUID() : 'u-' + Date.now();
    try { localStorage.setItem('anaphora_uid', newUid); } catch (e) { /* ignore */ }
    uidRef.current = newUid;
    patch({ ...initialState, screen: 'welcome', framed: s.framed });
  };
  const toggleFrame = () => patch((prev) => ({ framed: !prev.framed }));
  const openPlans = () => patch({ plansOpen: true });
  const closePlans = () => patch({ plansOpen: false });
  const openInvite = async () => {
    patch({ inviteOpen: true, copied: false, inviteCreating: true, inviteToken: null, inviteError: null });
    const r = await api('POST', '/friends/invite');
    if (r) patch({ inviteCreating: false, inviteToken: r.token });
    else patch({ inviteCreating: false, inviteError: "Couldn't create your invite link. Please try again." });
  };
  const closeInvite = () => patch({ inviteOpen: false });
  const inviteLink = s.inviteToken ? window.location.origin + '/?f=' + s.inviteToken : '';
  const copyInvite = async () => {
    try { await navigator.clipboard.writeText(inviteLink); }
    catch (e) {
      const ta = document.createElement('textarea'); ta.value = inviteLink; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (e2) { /* clipboard unavailable */ }
      document.body.removeChild(ta);
    }
    patch({ copied: true }); clearTimeout(copyTimerRef.current); copyTimerRef.current = setTimeout(() => patch({ copied: false }), 2200);
  };

  const accent = LAV;
  const groups = GROUP_DEFS.map(([persp, cat, title, side]) => {
    const items = s.signals.filter((x) => x.perspective === persp && (cat ? x.category === cat : true)).map((x) => {
      const st = STRENGTH_STYLE[x.strength] || STRENGTH_STYLE.preference;
      return { id: x.id, label: x.label, evidence: x.evidence_text || '', strengthLabel: st.label, dot: st.dot, pillBg: st.bg, pillFg: st.fg, onEdit: openEdit(x) };
    });
    return { title, side, perspective: persp, items };
  }).filter((g) => g.items.length);
  const br = mockReadiness(s.signals, s.discoveryDone, s.preferencesSaved ? s.gender : null);
  const readiness = s.mode === 'live' ? s.readiness : br.total;
  const postMatchMode = readiness === 100 && s.hasVisitedReadyMatches;
  const idealPartnerReady = !!br.met.ideal_partner_profile;
  const aboutMeReady = !!br.met.me_profile;
  const lifeDone = s.completedDiscoveries.includes(DEFAULT_DISCOVERY_ID);
  const steps = [
    { key: 'ideal', title: "Tell me who you're looking for", note: idealPartnerReady ? 'Enough detail captured' : 'One conversation, about 3 minutes', done: idealPartnerReady, cta: idealPartnerReady ? 'Add more' : (s.messages.length ? 'Continue' : 'Start'), onGo: resumeConversation },
    { key: 'me', title: 'Tell me who you are', note: aboutMeReady ? 'Enough about you' : 'Help Anaphora understand you too', done: aboutMeReady, cta: aboutMeReady ? 'Add more' : (s.messages.length ? 'Continue' : 'Start'), onGo: resumeConversation },
    { key: 'disc', title: 'What kind of life are you building?', note: s.discoverySaving && s.discoveryId === DEFAULT_DISCOVERY_ID ? 'Adding insight to your Blueprint…' : (lifeDone ? 'Insight added to your Blueprint' : 'A Discovery — 4 questions'), done: lifeDone, cta: s.discoverySaving && s.discoveryId === DEFAULT_DISCOVERY_ID ? 'Adding…' : (lifeDone ? 'Done' : '2 min'), onGo: lifeDone ? go('insight') : (() => startDiscovery(DEFAULT_DISCOVERY_ID, 'home')) },
    { key: 'prefs', title: 'Basic matching preferences', note: s.preferencesSaved ? s.gender + ' · ' + s.ageMin + '–' + s.ageMax : 'Who and what age range', done: s.preferencesSaved, cta: s.preferencesSaved ? 'Edit' : 'Set', onGo: go('profile') },
  ].map((st) => ({ ...st, mark: st.done ? '✓' : '', ring: st.done ? SAGE : '#DDEAE6', fill: st.done ? SAGE : 'transparent' }));
  const refinementActions = [
    { key: 'talk', title: 'Talk to Anaphora', note: 'Add nuance about you or the person you’re looking for', cta: 'Continue', onGo: resumeConversation },
    { key: 'friend', title: 'Ask someone who knows you well', note: 'A different perspective can reveal patterns you might not notice', cta: 'Ask a friend', onGo: go('friends') },
  ];
  const discoveries = DISCOVERY_LIBRARY.map((d) => ({ ...d, done: s.completedDiscoveries.includes(d.id) }));
  const nextDiscovery = DISCOVERY_LIBRARY.find((d) => d.id === s.suggestedDiscoveryId) || null;

  const q = s.questions[s.dqIdx] || { id: '_none', prompt: '', options: [] };
  const ans = s.answers[q.id];
  const isSpectrum = !!q.spectrum;
  const isText = !!q.text;
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
  const otherSelected = ans === '__OTHER__' || String(ans || '').startsWith('Other: ');
  const otherValue = String(ans || '').startsWith('Other: ') ? String(ans).slice(7) : '';
  const answered = isText ? !!String(ans || '').trim() : otherSelected ? otherValue.trim().length > 0 : ans !== undefined;
  const last = s.dqIdx === s.questions.length - 1;
  const readinessCopy = readiness >= 90 ? ['Ready when you are', 'We know enough to look for people who actually fit.'] : readiness >= 60 ? ['Coming into focus', 'A little more and intros start making real sense.'] : readiness > 0 ? ['A good beginning', 'Every answer sharpens who we look for.'] : ['Nothing yet', 'One conversation is all it takes to start.'];
  const dqOptions = (q.options || []).map((o) => {
    const selected = o.id === 'other' ? otherSelected : ans === o.label;
    return { key: o.id, label: o.label, onPick: pickOption(q.id, o), border: selected ? accent : '#DDEAE6', bg: selected ? 'rgba(166,154,205,.1)' : '#FFFFFF' };
  });
  const strengthOptions = STRENGTHS.map(([v, label, note]) => ({ key: v, label, note, onPick: pickStrength(v), border: s.editStrength === v ? accent : '#DDEAE6', bg: s.editStrength === v ? 'rgba(166,154,205,.1)' : '#FFFFFF' }));
  const modeLabel = s.mode === 'live' ? 'Live backend' : (s.mode === 'offline' ? 'Backend offline' : 'Connecting…');
  const modeDot = s.mode === 'live' ? SAGE : (s.mode === 'offline' ? LAV : '#DDEAE6');

  let screenEl = null;
  switch (s.screen) {
    case 'welcome': screenEl = <Welcome onBegin={beginConversation} goPrivacy={goLegal('privacy')} goTerms={goLegal('terms')} />; break;
    case 'legal': screenEl = <Legal goBack={go('welcome')} section={s.legalSection} />; break;
    case 'chat': screenEl = <Chat goHome={go('home')} messages={s.messages} thinking={s.thinking} categoriesCoveredCount={s.categoriesCovered.length} totalCategories={BASE_CATEGORIES.length} draft={s.draft} onDraft={onDraft} onDraftKey={onDraftKey} sendMessage={sendMessage} turnCount={s.turnCount} readyToComplete={s.readyToComplete} isFollowUp={s.hasExistingBlueprint} completeConversation={completeConversation} chatEndRef={chatEndRef} setDraft={setDraft} error={s.error && s.error.screen === 'chat' ? s.error.message : null} onRetryStart={!s.convoId ? beginConversation : null} />; break;
    case 'enough': screenEl = <Enough signalCount={s.signals.length} goBlueprint={go('blueprint')} goHome={go('home')} groups={groups} isFollowUp={s.wasFollowUp} />; break;
    case 'blueprint': screenEl = <Blueprint goHome={go('home')} groups={groups} signalCount={s.signals.length} narrative={s.narrative} scrollToAboutYou={s.blueprintScrollAboutYou} onScrolledAboutYou={clearBlueprintScroll} />; break;
    case 'home': screenEl = <Home readiness={readiness} readinessHeadline={readinessCopy[0]} readinessSub={readinessCopy[1]} insight={s.insight} steps={steps} openPlans={openPlans} goBlueprint={go('blueprint')} goIntro={goMatches} signalCount={s.signals.length} discoverySaving={s.discoverySaving} discoverySaveError={s.discoverySaveError} retryDiscovery={retryDiscovery} postMatchMode={postMatchMode} refinementActions={refinementActions} nextDiscovery={nextDiscovery} startDiscovery={startDiscovery} />; break;
    case 'convos': screenEl = <Convos convoStatus={s.convoCompleted ? 'Completed · ' + s.turnCount + ' turns' : (s.messages.length ? 'In progress' : 'Not started')} convoCta={s.convoCompleted ? 'Continue' : (s.messages.length ? 'Resume' : 'Start')} resumeConversation={resumeConversation} discoveries={discoveries} startDiscovery={startDiscovery} />; break;
    case 'discovery': screenEl = <Discovery discoveryUnavailable={!s.discoveryLoading && s.questions.length === 0} discoveryBack={discoveryBack} discoveryProgress={s.questions.length ? Math.round(((s.dqIdx + (answered ? 1 : 0)) / s.questions.length) * 100) + '%' : '0%'} discoveryCounter={s.questions.length ? (s.dqIdx + 1) + '/' + s.questions.length : ''} discoveryTitle={s.discoveryTitle} dqPrompt={q.prompt} dqIsChoice={!isSpectrum && !isText} dqOptions={dqOptions} dqIsSpectrum={isSpectrum} dqLeft={isSpectrum ? q.spectrum[0] : ''} dqRight={isSpectrum ? q.spectrum[1] : ''} dqValue={sv} onSpectrum={onSpectrum} dqReading={reading} dqIsText={isText} dqTextValue={isText ? String(ans || '') : ''} onTextAnswer={onTextAnswer} dqPlaceholder={q.placeholder} dqOtherSelected={otherSelected} dqOtherValue={otherValue} onOtherAnswer={onOtherAnswer} dqNextLabel={answered ? (last ? 'Add to my Blueprint' : 'Next') : 'Choose the most fitting'} dqNextBg={answered ? SAGE : '#F2EDE6'} dqNextFg={answered ? '#FFFFFF' : '#2F4A3F'} dqNextDisabled={!answered} discoveryNext={discoveryNext} error={null} />; break;
    case 'insight': screenEl = <Insight insight={s.insight} newSignals={s.newSignals} readiness={readiness} goHome={go('home')} />; break;
    case 'matches': screenEl = <Matches matches={s.matches} loading={s.matchesLoading} ready={s.matchesReady} error={s.error && s.error.screen === 'matches' ? s.error.message : null} onRetry={fetchMatches} goHome={go('home')} />; break;
    case 'friends': screenEl = <Friends invites={s.friends} openFriendReview={openFriendReview} openInvite={openInvite} inviteCount={s.friends.length} inviteLimit={FRIEND_INVITE_LIMIT} />; break;
    case 'friendReview': screenEl = <FriendReview goBack={go('friends')} friendName={s.friendReview?.friend_name} narrative={s.friendReview?.narrative || ''} signals={s.friendReview?.signals || []} selectedIds={s.friendReviewSelected} onToggleSignal={toggleFriendSignal} onCommit={commitFriendReview} committing={s.friendCommitting} error={s.error && s.error.screen === 'friendReview' ? s.error.message : null} committed={s.friendCommitted} addedCount={s.friendAddedCount} loading={s.friendReviewLoading} />; break;
    case 'profile': screenEl = <Profile gender={s.gender} onPickGender={pickGender} ageMin={s.ageMin} ageMax={s.ageMax} onAgeMin={onAgeMin} onAgeMax={onAgeMax} onSavePreferences={savePreferences} preferencesSaving={s.preferencesSaving} preferencesSaved={s.preferencesSaved} preferencesError={s.preferencesError} readiness={readiness} breakdownMet={br.met} openPlans={openPlans} goPrivacy={goLegal('privacy')} goTerms={goLegal('terms')} signalCount={s.signals.length} goBlueprint={goBlueprintAboutYou} />; break;
    default: screenEl = null;
  }

  return (
    <PhoneFrame framed={s.framed} onToggleFrame={toggleFrame} modeLabel={modeLabel} modeDot={modeDot} onResetAll={resetAll}>
      {screenEl}
      {TAB_SCREENS.includes(s.screen) && <TabBar activeScreen={s.screen} onGo={(key) => (key === 'matches' ? goMatches() : go(key)())} />}
      {s.editing && <SignalEditSheet editLabel={s.editLabel} onEditLabel={onEditLabel} closeEdit={closeEdit} saveEdit={saveEdit} strengthOptions={strengthOptions} />}
      {s.plansOpen && <PlansModal closePlans={closePlans} />}
      {s.inviteOpen && <InviteLinkSheet closeInvite={closeInvite} copyInvite={copyInvite} inviteLink={inviteLink} copied={s.copied} creating={s.inviteCreating} error={s.inviteError} />}
    </PhoneFrame>
  );
}
