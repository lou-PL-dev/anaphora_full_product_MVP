// Offline/demo fallback only. In live mode the backend /readiness result is
// the single source of truth. Keep this mirror deliberately small and aligned
// with anaphora_backend/app/readiness.py.
import { WEIGHTS } from './data';

const CORE = ['personality', 'lifestyle', 'physical_type', 'relationship_dynamic', 'love_language', 'dealbreakers', 'values'];
const REQUIRED = ['personality', 'lifestyle', 'relationship_dynamic'];

function sideReady(signals, perspective) {
  const covered = new Set(signals.filter((s) => s.perspective === perspective && CORE.includes(s.category)).map((s) => s.category));
  return REQUIRED.every((c) => covered.has(c)) && covered.size >= 5;
}

export function mockReadiness(signals, discoveryDone, basicPreferencesDone) {
  const met = {
    basic_matching_preferences: !!basicPreferencesDone,
    discovery_completed: !!discoveryDone,
    me_profile: sideReady(signals, 'ME'),
    ideal_partner_profile: sideReady(signals, 'IDEAL_PARTNER'),
  };
  const total = Object.keys(met).reduce((sum, key) => sum + (met[key] ? WEIGHTS[key][0] : 0), 0);
  return { total, met };
}
