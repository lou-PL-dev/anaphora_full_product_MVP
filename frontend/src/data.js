// Fixed lookup tables the UI renders from.

// Readiness is a matching gate, not Blueprint depth. The backend is the
// source of truth; these values are display labels for its four gates.
export const WEIGHTS = {
  basic_matching_preferences: [20, 'Basic matching preferences'],
  discovery_completed: [20, 'A Discovery completed'],
  me_profile: [30, 'Enough about you'],
  ideal_partner_profile: [30, 'Enough about who you want'],
};

// Shared Blueprint dimensions. Conversation coverage is symmetric: the API
// reports these separately for ME and IDEAL_PARTNER.
export const BASE_CATEGORIES = [
  'personality', 'lifestyle', 'physical_type',
  'relationship_dynamic', 'love_language', 'dealbreakers', 'values',
];

// [perspective, category|null, title, side]
export const GROUP_DEFS = [
  ['IDEAL_PARTNER', 'personality', 'PERSONALITY', 'Who they are'],
  ['IDEAL_PARTNER', 'lifestyle', 'LIFESTYLE', 'How they live'],
  ['IDEAL_PARTNER', 'physical_type', 'PHYSICAL TYPE', 'What draws you'],
  ['IDEAL_PARTNER', 'relationship_dynamic', 'RELATIONSHIP DYNAMIC', 'What you need'],
  ['IDEAL_PARTNER', 'love_language', 'LOVE & AFFECTION', 'How they connect'],
  ['IDEAL_PARTNER', 'dealbreakers', 'DEALBREAKERS', 'Non-negotiable'],
  ['IDEAL_PARTNER', 'values', 'VALUES', 'What matters'],
  ['ME', 'personality', 'YOUR PERSONALITY', 'Who you are'],
  ['ME', 'lifestyle', 'YOUR LIFESTYLE', 'How you live'],
  ['ME', 'physical_type', 'YOUR PHYSICAL SELF', 'How you present'],
  ['ME', 'relationship_dynamic', 'YOUR RELATIONSHIP STYLE', 'How you relate'],
  ['ME', 'love_language', 'YOUR LOVE & AFFECTION STYLE', 'How you connect'],
  ['ME', 'dealbreakers', 'YOUR CONTEXT', 'What materially matters'],
  ['ME', 'values', 'YOUR VALUES', 'What matters to you'],
];

export const STRENGTHS = [
  ['hard_requirement', 'Non-negotiable', "I'd walk away over this"],
  ['strong_preference', 'Strongly matters', 'A lot, but not everything'],
  ['preference', 'Nice to have', 'It would be good'],
  ['unknown', 'Not sure yet', 'Leave it open'],
];

export const STRENGTH_STYLE = {
  hard_requirement: { dot: '#2F4A3F', bg: 'rgba(47,74,63,.1)', fg: '#2F4A3F', label: 'NON-NEGOTIABLE' },
  strong_preference: { dot: '#A69ACD', bg: 'rgba(166,154,205,.16)', fg: '#7A6DAF', label: 'STRONG' },
  preference: { dot: '#DDEAE6', bg: 'rgba(47,74,63,.05)', fg: '#5C6B62', label: 'PREFERENCE' },
  unknown: { dot: '#E2DED8', bg: 'rgba(47,74,63,.04)', fg: '#94A09A', label: 'OPEN' },
};

export const TABS = [
  ['home', 'Home', 'M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z'],
  ['convos', 'Conversations', 'M21 12a8 8 0 0 1-8 8H7l-4 3 1.2-4.4A8 8 0 1 1 21 12z'],
  ['matches', 'Matches', 'M12 20s-7-4.6-7-9.4A4 4 0 0 1 12 8a4 4 0 0 1 7 2.6C19 15.4 12 20 12 20z'],
  ['friends', 'Friends', 'M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20M9.5 10.5a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4M21 20v-1.4a4 4 0 0 0-3-3.8'],
  ['profile', 'You', 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7'],
];

export const STATIC_FRIENDS = [
  { initial: 'L', name: 'Léa', rel: 'Sister', quote: "She's thoughtful, adventurous, and will make you laugh every day." },
  { initial: 'T', name: 'Thomas', rel: 'Friend, 12 years', quote: 'Needs someone who can keep up with her, and who reads.' },
  { initial: 'M', name: 'Marek', rel: 'Colleague', quote: 'Warmest person in any room, but she needs her quiet.' },
];