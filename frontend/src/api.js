// Talks to the FastAPI backend (anaphora_backend). Every request carries the
// anonymous per-device identity header the backend expects.
export const API_BASE = import.meta.env.VITE_API_BASE || 'https://anaphora-app.onrender.com';

export const TIMEOUT_QUICK = 45000;
export const TIMEOUT_CHAT_REPLY = 20000;
export const TIMEOUT_INSIGHT = 45000;
export const TIMEOUT_EXTRACTION = 45000;
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
    return res.status === 204 ? {} : await res.json();
  } catch (e) {
    clearTimeout(timer);
    return null;
  }
}

// Fire-and-forget product-research event. A tracking failure must never block
// or alter the tester's actual product flow.
export function trackEvent(userId, event, metadata = {}) {
  if (!userId || !event) return;
  fetch(API_BASE + '/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Anaphora-User-Id': userId },
    body: JSON.stringify({ event, metadata }),
  }).catch(() => {});
}

export async function adminApiCall(secret, path) {
  try {
    const res = await fetch(API_BASE + path, {
      headers: { 'X-Admin-Secret': secret },
    });
    const data = await res.json().catch(() => null);
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    return { ok: false, status: 0, data: null };
  }
}

export async function apiCallPublic(method, path, body, timeoutMs = TIMEOUT_QUICK) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(API_BASE + path, {
      method,
      signal: ctrl.signal,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    clearTimeout(timer);
    const data = res.status === 204 ? null : await res.json().catch(() => null);
    return { status: res.status, ok: res.ok, data };
  } catch (e) {
    clearTimeout(timer);
    return { status: 0, ok: false, data: null };
  }
}
