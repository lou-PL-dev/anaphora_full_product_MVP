import { WEIGHTS } from './data';

// Mirrors anaphora_backend/app/readiness.py's compute_readiness so the UI
// can show a readiness breakdown locally (the Profile screen's "READINESS
// BREAKDOWN" list) without a round trip for every render.
export function mockReadiness(signals, discoveryDone, gender) {
  const has = (p, c) => signals.some((s) => s.perspective === p && (!c || s.category === c));
  const met = {
    ideal_partner_personality: has('IDEAL_PARTNER', 'personality'),
    ideal_partner_lifestyle: has('IDEAL_PARTNER', 'lifestyle'),
    ideal_partner_physical_type: has('IDEAL_PARTNER', 'physical_type'),
    ideal_partner_relationship_dynamic: has('IDEAL_PARTNER', 'relationship_dynamic'),
    ideal_partner_love_language: has('IDEAL_PARTNER', 'love_language'),
    ideal_partner_dealbreakers: has('IDEAL_PARTNER', 'dealbreakers'),
    about_you: has('ME', null),
    discovery_completed: !!discoveryDone,
    basic_matching_preferences: !!gender,
  };
  let total = 0;
  Object.keys(met).forEach((k) => { if (met[k]) total += WEIGHTS[k][0]; });
  return { total, met };
}
