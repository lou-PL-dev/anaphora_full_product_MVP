import { useEffect, useState } from 'react';
import FriendShell from './components/FriendShell';
import FriendLanding from './friend/FriendLanding';
import FriendAnswerReview from './friend/FriendAnswerReview';
import FriendDone from './friend/FriendDone';
import FriendError from './friend/FriendError';
import Discovery from './screens/Discovery';
import { apiCallPublic, TIMEOUT_QUICK, TIMEOUT_INSIGHT } from './api';

// A friend opening an invite link needs no account, no device identity and
// none of the main app's state machine — this is a small, fully separate
// flow (PRD sections 16-20), reusing the same brand screens/components
// throughout rather than inventing new ones.
export default function FriendFlow({ token }) {
  const [step, setStep] = useState('loading'); // loading | error | landing | questions | review | done
  const [errorMessage, setErrorMessage] = useState('');
  const [inviterName, setInviterName] = useState('');
  const [questions, setQuestions] = useState([]);
  const [friendName, setFriendName] = useState('');
  const [dqIdx, setDqIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [reachedReview, setReachedReview] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const r = await apiCallPublic('GET', '/friends/invite/' + token, undefined, TIMEOUT_QUICK);
      if (cancelled) return;
      if (r.status === 410) { setErrorMessage("This invite link has already been used — it only works once."); setStep('error'); return; }
      if (r.status === 404) { setErrorMessage("We couldn't find this invite link."); setStep('error'); return; }
      if (!r.ok || !r.data) { setErrorMessage("We couldn't reach Anaphora. Check your connection and try opening the link again."); setStep('error'); return; }
      setInviterName(r.data.inviter_name);
      setQuestions(r.data.questions);
      setStep('landing');
    })();
    return () => { cancelled = true; };
  }, [token]);

  const onFriendNameChange = (e) => setFriendName(e.target.value);
  const beginQuestions = () => { if (friendName.trim()) { setDqIdx(0); setStep('questions'); } };

  const q = questions[dqIdx] || { id: '_none', prompt: '', options: [] };
  const ans = answers[q.id];
  const isText = !!q.text;
  const otherSelected = ans === '__OTHER__' || String(ans || '').startsWith('Other: ');
  const otherValue = String(ans || '').startsWith('Other: ') ? String(ans).slice(7) : '';
  const answered = isText
    ? !!String(ans || '').trim()
    : otherSelected
      ? otherValue.trim().length > 0
      : ans !== undefined;
  const last = dqIdx === questions.length - 1;

  const pickOption = (qid, option) => () => setAnswers((prev) => ({ ...prev, [qid]: option.id === 'other' ? '__OTHER__' : option.label }));
  const onOtherAnswer = (e) => setAnswers((prev) => ({ ...prev, [q.id]: 'Other: ' + e.target.value }));
  const onTextAnswer = (e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }));

  const dqOptions = (q.options || []).map((o) => {
    const selected = o.id === 'other' ? otherSelected : ans === o.label;
    return { key: o.id, label: o.label, onPick: pickOption(q.id, o), border: selected ? '#A69ACD' : '#DDEAE6', bg: selected ? 'rgba(166,154,205,.1)' : '#FFFFFF' };
  });

  const discoveryBack = () => {
    if (dqIdx > 0) { setDqIdx(dqIdx - 1); return; }
    setStep(reachedReview ? 'review' : 'landing');
  };
  const discoveryNext = () => {
    if (!answered) return;
    if (dqIdx < questions.length - 1) { setDqIdx(dqIdx + 1); return; }
    setReachedReview(true);
    setStep('review');
  };
  const onEditQuestion = (questionId) => {
    const idx = questions.findIndex((item) => item.id === questionId);
    if (idx >= 0) setDqIdx(idx);
    setStep('questions');
  };

  const displayAnswer = (qid) => {
    const a = answers[qid];
    if (a === undefined) return '';
    if (String(a).startsWith('Other: ')) return String(a).slice(7);
    return String(a);
  };
  const answersByQuestion = Object.fromEntries(questions.map((item) => [item.id, displayAnswer(item.id)]));

  const submit = async () => {
    if (submitting) return;
    setSubmitting(true);
    setSubmitError(null);
    const payload = questions.map((item) => ({ question_id: item.id, response: displayAnswer(item.id) }));
    const r = await apiCallPublic('POST', '/friends/invite/' + token + '/respond', { friend_name: friendName.trim(), answers: payload }, TIMEOUT_INSIGHT);
    setSubmitting(false);
    if (r.status === 410) { setErrorMessage("This invite link has already been used — it only works once."); setStep('error'); return; }
    if (!r.ok) { setSubmitError("Couldn't send your answers — check your connection and try again."); return; }
    setStep('done');
  };

  let screenEl = null;
  if (step === 'loading') screenEl = null;
  else if (step === 'error') screenEl = <FriendError message={errorMessage} />;
  else if (step === 'landing') screenEl = <FriendLanding inviterName={inviterName} friendName={friendName} onFriendName={onFriendNameChange} onContinue={beginQuestions} canContinue={!!friendName.trim()} />;
  else if (step === 'questions') screenEl = (
    <Discovery
      discoveryUnavailable={false}
      discoveryBack={discoveryBack}
      discoveryProgress={questions.length ? Math.round(((dqIdx + (answered ? 1 : 0)) / questions.length) * 100) + '%' : '0%'}
      discoveryCounter={questions.length ? (dqIdx + 1) + '/' + questions.length : ''}
      discoveryTitle={`For ${inviterName}`}
      dqPrompt={q.prompt}
      dqIsChoice={!isText}
      dqOptions={dqOptions}
      dqIsSpectrum={false}
      dqLeft="" dqRight="" dqValue={50} onSpectrum={() => {}} dqReading=""
      dqIsText={isText}
      dqTextValue={isText ? String(ans || '') : ''}
      onTextAnswer={onTextAnswer}
      dqPlaceholder={q.placeholder}
      dqOtherSelected={otherSelected}
      dqOtherValue={otherValue}
      onOtherAnswer={onOtherAnswer}
      dqNextLabel={answered ? (last ? 'Review your answers' : 'Next') : 'Choose the most fitting'}
      dqNextBg={answered ? '#2F4A3F' : '#F2EDE6'}
      dqNextFg={answered ? '#FFFFFF' : '#2F4A3F'}
      dqNextDisabled={!answered}
      discoveryNext={discoveryNext}
      error={null}
    />
  );
  else if (step === 'review') screenEl = <FriendAnswerReview inviterName={inviterName} questions={questions} answers={answersByQuestion} onEditQuestion={onEditQuestion} onSubmit={submit} submitting={submitting} error={submitError} />;
  else if (step === 'done') screenEl = <FriendDone inviterName={inviterName} />;

  return <FriendShell>{screenEl}</FriendShell>;
}
