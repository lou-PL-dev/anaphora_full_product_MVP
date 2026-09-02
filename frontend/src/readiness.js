// Offline/demo mirror of the backend's ME / YOU / US readiness rules.
const ALLOWED = {
  ME: new Set(['personality', 'lifestyle', 'relationship_behavior', 'core_values']),
  IDEAL_PARTNER: new Set(['personality', 'lifestyle', 'physical_type']),
  US: new Set(['relationship_shape', 'connection_affection', 'shared_direction', 'boundaries']),
};

function coveredCategories(signals, perspective) {
  return new Set(signals
    .filter((signal) => signal.perspective === perspective && ALLOWED[perspective].has(signal.category))
    .map((signal) => signal.category));
}

export function mockReadiness(signals, discoveryDone, meetingPreference) {
  const me = coveredCategories(signals, 'ME');
  const ideal = coveredCategories(signals, 'IDEAL_PARTNER');
  const us = coveredCategories(signals, 'US');
  const met = {
    introduction_essentials: false,
    meeting_preferences: !!meetingPreference,
    discovery_completed: !!discoveryDone,
    me_profile: me.has('personality') && me.has('lifestyle') && me.size >= 3,
    ideal_partner_profile: ['personality', 'lifestyle', 'physical_type'].every((category) => ideal.has(category)),
    us_profile: us.has('relationship_shape') && us.size >= 3,
  };
  const total = (met.meeting_preferences ? 10 : 0)
    + (met.discovery_completed ? 20 : 0)
    + (met.me_profile ? 20 : 0)
    + (met.ideal_partner_profile ? 20 : 0)
    + (met.us_profile ? 20 : 0);
  return { total, met };
}
