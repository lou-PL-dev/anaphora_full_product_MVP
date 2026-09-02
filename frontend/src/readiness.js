// Offline/demo fallback only. The live backend remains the source of truth.
// App.jsx currently only carries the legacy meeting-preference state, so this
// fallback deliberately awards at most that 10% half of Introduction
// essentials. It must never invent the missing Your essentials half offline.

const CORE_CATEGORIES = new Set([
  'personality',
  'lifestyle',
  'physical_type',
  'relationship_dynamic',
  'love_language',
  'dealbreakers',
  'values',
]);

const MANDATORY_CATEGORIES = [
  'personality',
  'lifestyle',
  'relationship_dynamic',
];

const MIN_CATEGORIES_PER_SIDE = 5;

function coveredCategories(signals, perspective) {
  return new Set(
    signals
      .filter((s) => s.perspective === perspective && CORE_CATEGORIES.has(s.category))
      .map((s) => s.category),
  );
}

function profileReady(covered) {
  return (
    MANDATORY_CATEGORIES.every((category) => covered.has(category))
    && covered.size >= MIN_CATEGORIES_PER_SIDE
  );
}

export function mockReadiness(signals, discoveryDone, meetingPreference) {
  const meCovered = coveredCategories(signals, 'ME');
  const idealPartnerCovered = coveredCategories(signals, 'IDEAL_PARTNER');

  const met = {
    introduction_essentials: false,
    meeting_preferences: !!meetingPreference,
    discovery_completed: !!discoveryDone,
    me_profile: profileReady(meCovered),
    ideal_partner_profile: profileReady(idealPartnerCovered),
  };

  const total =
    (met.meeting_preferences ? 10 : 0)
    + (met.discovery_completed ? 20 : 0)
    + (met.me_profile ? 30 : 0)
    + (met.ideal_partner_profile ? 30 : 0);

  return { total, met };
}
