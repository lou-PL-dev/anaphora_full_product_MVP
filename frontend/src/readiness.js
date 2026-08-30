import { WEIGHTS } from './data';

// Mirrors anaphora_backend/app/readiness.py's compute_readiness so demo mode
// (no backend) shows the same deterministic coverage % as the real one.
export function mockReadiness(signals, discoveryDone, gender) {
  const has = (p, c) => signals.some((s) => s.perspective === p && (!c || s.category === c));
  const met = {
    ideal_partner_personality: has('IDEAL_PARTNER', 'personality'),
    ideal_partner_lifestyle: has('IDEAL_PARTNER', 'lifestyle'),
    relationship_needs: has('IDEAL_PARTNER', 'relationship_dynamic'),
    attraction: has('IDEAL_PARTNER', 'attraction'),
    about_me: has('ME', null),
    values: has('IDEAL_PARTNER', 'values') || has('ME', 'values'),
    discovery_completed: !!discoveryDone,
    basic_matching_preferences: !!gender,
  };
  let total = 0;
  Object.keys(met).forEach((k) => { if (met[k]) total += WEIGHTS[k][0]; });
  return { total, met };
}
