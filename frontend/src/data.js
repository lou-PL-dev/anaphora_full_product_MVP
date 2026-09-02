// Fixed lookup tables the UI renders from. Friends and Matches are both
// REAL data (see App.jsx::fetchMatches and the /friends routes), not
// static content. There is deliberately no mock/demo fallback content
// here: if the backend or an LLM call is unreachable, the app surfaces a
// real error instead of substituting fabricated conversation, signals,
// insights, matches, or friend contributions.

export const DISCOVERY_LIBRARY = [
  { id: 'feel_at_home', title: 'What makes you feel at home?', note: 'Closeness, reassurance and emotional needs', questions: 4, minutes: 2 },
  { id: 'life_you_are_building', title: 'What kind of life are you building?', note: 'Lifestyle, future, roots and freedom', questions: 4, minutes: 2 },
  { id: 'chemistry', title: 'What creates chemistry?', note: 'Attraction, energy and what pulls you in', questions: 4, minutes: 2 },
  { id: 'how_you_love', title: 'How do you love?', note: 'Closeness, conflict and communication', questions: 4, minutes: 2 },
  { id: 'live_together', title: 'Could we actually live together?', note: 'Everyday compatibility, routines and money', questions: 4, minutes: 2 },
  { id: 'non_negotiables', title: "What can't you compromise on?", note: 'Must-haves, trade-offs and boundaries', questions: 4, minutes: 3 },
  { id: 'relationship_archaeology', title: 'Relationship Archaeology', note: 'A deeper look at patterns from past relationships', questions: 5, minutes: 6, deeper: true },
];

export const WEIGHTS = {
  ideal_partner_personality: [10, 'Who they are'],
  ideal_partner_lifestyle: [10, 'How they live'],
  ideal_partner_physical_type: [10, 'What draws you'],
  ideal_partner_relationship_dynamic: [10, 'What you need from a relationship'],
  ideal_partner_love_language: [10, 'How they connect'],
  ideal_partner_dealbreakers: [10, 'Dealbreakers'],
  about_you: [10, 'About you'],
  discovery_completed: [15, 'A Discovery completed'],
  basic_matching_preferences: [15, 'Basic matching preferences'],
};

export const BASE_CATEGORIES = [
  'personality', 'lifestyle', 'physical_type',
  'relationship_dynamic', 'love_language', 'dealbreakers', 'about_you',
];

export const GROUP_DEFS = [
  ['IDEAL_PARTNER', 'personality', 'PERSONALITY', 'Who they are'],
  ['IDEAL_PARTNER', 'lifestyle', 'LIFESTYLE', 'How they live'],
  ['IDEAL_PARTNER', 'physical_type', 'PHYSICAL TYPE', 'What draws you'],
  ['IDEAL_PARTNER', 'relationship_dynamic', 'RELATIONSHIP DYNAMIC', 'What you need'],
  ['IDEAL_PARTNER', 'love_language', 'LOVE LANGUAGE', 'How they connect'],
  ['IDEAL_PARTNER', 'dealbreakers', 'DEALBREAKERS', 'Non-negotiable'],
  ['IDEAL_PARTNER', 'values', 'VALUES', 'What matters'],
  ['ME', null, 'ABOUT YOU', 'What you revealed'],
];

export const STRENGTHS = [
  ['hard_requirement', 'Non-negotiable', "I'd walk away over this"],
  ['strong_preference', 'Strongly matters', 'A lot, but not everything'],
  ['preference', 'Nice to have', 'It would be good'],
  ['unknown', 'Not sure yet', 'Leave it open'],
];

export const STRENGTH_STYLE = {
  hard_requirement: { dot: '#2F4A3F', bg: '#DDEAE6', fg: '#2F4A3F', label: 'NON-NEGOTIABLE' },
  strong_preference: { dot: '#A69ACD', bg: 'rgba(166,154,205,.16)', fg: '#2F4A3F', label: 'STRONG' },
  preference: { dot: '#DDEAE6', bg: '#DDEAE6', fg: '#2F4A3F', label: 'PREFERENCE' },
  unknown: { dot: '#F2EDE6', bg: '#F2EDE6', fg: '#2F4A3F', label: 'OPEN' },
};

export const TABS = [
  ['home', 'Home', 'M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z'],
  ['convos', 'Conversations', 'M21 12a8 8 0 0 1-8 8H7l-4 3 1.2-4.4A8 8 0 1 1 21 12z'],
  ['matches', 'Intros', ''],
  ['friends', 'Friends', 'M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20M9.5 10.5a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4M21 20v-1.4a4 4 0 0 0-3-3.8'],
  ['profile', 'You', 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7'],
];

// PRD section: Free tier gets up to 3 friend invitations (Anaphora+ is
// unlimited — see PlansModal). Enforced authoritatively by the backend;
// mirrored here only to gate/label the "Share invite link" button.
export const FRIEND_INVITE_LIMIT = 3;
