// Talks to the FastAPI backend (anaphora_backend). Every request carries the
// anonymous per-device identity header the backend expects (see
// anaphora_backend/app/auth.py). A failed call returns null — callers
// surface a real error rather than substituting fabricated content (see
// App.jsx).
//
// Defaults to the deployed Render backend so the Netlify build works with
// no env var configured. Override with VITE_API_BASE for local dev against
// `uvicorn app.main:app --reload` (defaults to :8000) — see .env.example.
export const API_BASE = import.meta.env.VITE_API_BASE || 'https://anaphora-app.onrender.com';

// Different endpoints need very different timeouts. A plain CRUD call
// (start a conversation, patch a signal, fetch the discovery structure) is
// normally fast, but any of these can be the FIRST request of a session —
// and the deployed backend (Render free tier) spins down after ~15 minutes
// idle and takes up to ~50s to wake back up on the next request. A short
// timeout here would misreport a waking-up backend as offline. A
// conversational turn is one LLM completion. Extraction
// (/conversation/complete) asks the LLM for STRUCTURED output across 10
// categories at once — noticeably slower than a normal chat reply — and
// needs the most headroom.
export const TIMEOUT_QUICK = 45000;
export const TIMEOUT_CHAT_REPLY = 20000;
export const TIMEOUT_INSIGHT = 20000;
export const TIMEOUT_EXTRACTION = 45000;
// /matches does one embedding call plus one structured-output LLM call
// (see matching_chain.generate_match_explanations) across several
// candidates at once — similar shape to extraction, same headroom.
export const TIMEOUT_MATCHES = 45000;

const UID_KEY = 'anaphora_uid';

export function getOrCreateUserId() {
  let uid = null;
  try { uid = localStorage.getItem(UID_KEY); } catch (e) { /* private mode etc. */ }
  if (!uid) {
    uid = crypto.randomUUID ? crypto.randomUUID() : 'u-' + Date.now();
    try { localStorage.setItem(UID_KEY, uid); } catch (e) { /* ignore */ }
  }
  return uid;
}

/**
 * Returns the parsed JSON body on success, or null on any failure (network
 * error, timeout, non-2xx) — callers surface a real error rather than
 * substituting fabricated content (see App.jsx).
 */
export async function apiCall(userId, method, path, body, timeoutMs = TIMEOUT_QUICK) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(API_BASE + path, {
      method,
      signal: ctrl.signal,
      headers: { 'Content-Type': 'application/json', 'X-Anaphora-User-Id': userId },
      body: body ? JSON.stringify(body) : undefined,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(String(res.status));
    return await res.json();
  } catch (e) {
    clearTimeout(timer);
    return null;
  }
}
