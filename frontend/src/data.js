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
  introduction_essentials: [20, 'Introduction essentials'],
  discovery_completed: [20, 'A Discovery completed'],
  me_profile: [30, 'About you'],
  ideal_partner_profile: [30, "Who you're looking for"],
};

export const BASE_CATEGORIES = [
  'me_personality', 'me_lifestyle', 'me_relationship_behavior', 'me_core_values',
  'ideal_partner_personality', 'ideal_partner_lifestyle', 'ideal_partner_physical_type',
  'us_relationship_shape', 'us_connection_affection', 'us_shared_direction', 'us_boundaries',
];

export const GROUP_DEFS = [
  ['IDEAL_PARTNER', 'personality', 'WHO THEY ARE', 'IDEAL PARTNER'],
  ['IDEAL_PARTNER', 'lifestyle', 'HOW THEY LIVE', 'IDEAL PARTNER'],
  ['IDEAL_PARTNER', 'physical_type', 'THE LOOK & PRESENCE YOU’RE DRAWN TO', 'IDEAL PARTNER'],
  ['US', 'relationship_shape', 'HOW WE WORK', 'YOUR RELATIONSHIP'],
  ['US', 'connection_affection', 'HOW WE CONNECT', 'YOUR RELATIONSHIP'],
  ['US', 'shared_direction', 'WHAT WE BUILD', 'YOUR RELATIONSHIP'],
  ['US', 'boundaries', 'WHAT I CAN’T COMPROMISE ON', 'YOUR RELATIONSHIP'],
  ['ME', 'personality', 'MY PERSONALITY', 'ABOUT YOU'],
  ['ME', 'lifestyle', 'HOW I LIVE', 'ABOUT YOU'],
  ['ME', 'relationship_behavior', 'HOW I SHOW UP IN LOVE', 'ABOUT YOU'],
  ['ME', 'core_values', 'WHAT GUIDES ME', 'ABOUT YOU'],
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
