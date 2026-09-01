export default function SignalEditSheet({ editLabel, onEditLabel, closeEdit, saveEdit, strengthOptions }) {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 30, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', background: 'rgba(166,154,205,.32)', animation: 'apFade .25s ease both' }}>
      <div onClick={closeEdit} style={{ flex: 1 }} />
      <div style={{ padding: '26px 24px 30px', borderRadius: '28px 28px 0 0', background: '#F2EDE6', animation: 'apRise .35s cubic-bezier(.2,.8,.2,1) both' }}>
        <div style={{ width: 38, height: 4, borderRadius: 2, background: '#DDEAE6', margin: '0 auto 20px' }} />
        <div style={{ fontSize: 10, letterSpacing: '.14em', color: '#A69ACD' }}>CHANGE SOMETHING</div>
        <div style={{ marginTop: 12, fontSize: 12.5, color: '#2F4A3F' }}>How would you put it?</div>
        <input
          value={editLabel}
          onChange={onEditLabel}
          style={{ marginTop: 9, width: '100%', padding: '15px 16px', borderRadius: 14, border: '1px solid #DDEAE6', background: '#FFFFFF', fontSize: 14.5, color: '#2F4A3F', outline: 'none' }}
        />
        <div style={{ marginTop: 20, fontSize: 12.5, color: '#2F4A3F' }}>How much does it matter?</div>
        <div style={{ marginTop: 9, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {strengthOptions.map((so) => (
            <button
              key={so.key}
              onClick={so.onPick}
              style={{ width: '100%', textAlign: 'left', padding: '14px 16px', borderRadius: 14, border: `1.5px solid ${so.border}`, background: so.bg, cursor: 'pointer' }}
            >
              <span style={{ display: 'block', fontSize: 13.5, color: '#2F4A3F' }}>{so.label}</span>
              <span style={{ display: 'block', marginTop: 3, fontSize: 11.5, color: '#A69ACD' }}>{so.note}</span>
            </button>
          ))}
        </div>
        <div style={{ marginTop: 22, display: 'flex', gap: 10 }}>
          <button onClick={closeEdit} style={{ flex: 1, padding: 15, borderRadius: 999, border: '1px solid #DDEAE6', background: 'transparent', color: '#2F4A3F', fontSize: 13.5, cursor: 'pointer' }}>Cancel</button>
          <button onClick={saveEdit} style={{ flex: 2, padding: 15, border: 'none', borderRadius: 999, background: '#2F4A3F', color: '#F2EDE6', fontSize: 13.5, fontWeight: 500, cursor: 'pointer' }}>Save</button>
        </div>
      </div>
    </div>
  );
}
