// Talks to the FastAPI backend (anaphora_backend). Every request carries the
// anonymous per-device identity header the backend expects (see
// anaphora_backend/app/auth.py) and fails soft — callers fall back to demo
// data when the backend is unreachable, exactly like the Claude Design
// prototype this was built from.

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

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
 * error, timeout, non-2xx) so callers can fall back to demo data.
 */
export async function apiCall(userId, method, path, body) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 6000);
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
