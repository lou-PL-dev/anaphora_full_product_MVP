import ErrorBanner from '../components/ErrorBanner';

// Reuses Blueprint.jsx's header pattern and Convos.jsx's list-card
// styling — lets the friend see and edit their own answers (PRD section
// 18's "friend can add more/change things") before anything is sent.
export default function FriendAnswerReview({ questions, answers, onEditQuestion, onSubmit, submitting, error }) {
  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', display: 'flex', flexDirection: 'column', background: '#FFFFFF' }}>
      <div style={{ padding: '62px 22px 18px', background: 'linear-gradient(160deg, #F2EDE6, #FFFFFF)' }}>
        <div style={{ fontSize: 11, letterSpacing: '.16em', color: '#A69ACD' }}>BEFORE YOU SEND</div>
        <div style={{ marginTop: 14, fontFamily: "'Playfair Display', serif", fontSize: 27, lineHeight: 1.25, color: '#2F4A3F' }}>Take a look at what you shared</div>
        <div style={{ marginTop: 12, fontSize: 13, lineHeight: 1.6, color: '#2F4A3F' }}>Tap anything you'd like to change.</div>
      </div>
      <div style={{ flex: 1, padding: '4px 22px 24px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {questions.map((q) => (
          <button key={q.id} onClick={() => onEditQuestion(q.id)} style={{ width: '100%', textAlign: 'left', padding: 18, borderRadius: 20, border: 'none', background: '#F2EDE6', cursor: 'pointer' }}>
            <div style={{ fontSize: 12, lineHeight: 1.5, color: '#A69ACD' }}>{q.prompt}</div>
            <div style={{ marginTop: 7, fontSize: 14.5, lineHeight: 1.5, color: '#2F4A3F' }}>{answers[q.id] || '—'}</div>
          </button>
        ))}
      </div>
      <ErrorBanner message={error} />
      <div style={{ padding: '12px 22px 26px' }}>
        <button disabled={submitting} onClick={onSubmit} style={{ width: '100%', padding: 17, border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#FFFFFF', fontSize: 15, fontWeight: 500, cursor: submitting ? 'default' : 'pointer' }}>
          {submitting ? 'Sending…' : 'Send to Anaphora'}
        </button>
      </div>
    </div>
  );
}
