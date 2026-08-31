// Fixed lookup tables the UI renders from, plus STATIC_FRIENDS (the Friends
// tab is frontend-only per the PRD — no backend endpoint). Matches is REAL
// data now (see App.jsx::fetchMatches / anaphora_backend's /matches RAG
// endpoint), not static content. There is deliberately no mock/demo
// fallback content here: if the backend or an LLM call is unreachable, the
// app surfaces a real error instead of substituting fabricated
// conversation, signals, insights, or matches.

// key -> [weight, label] — mirrors backend CATEGORY_WEIGHTS (readiness.py)
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

// The 7 base categories the conversation steers toward — mirrors
// BASE_CATEGORIES in anaphora_backend/app/chains/conversation_chain.py.
// Used to turn `categories_covered` from /conversation/message into a
// real progress readout instead of a raw turn count.
export const BASE_CATEGORIES = [
  'personality', 'lifestyle', 'physical_type',
  'relationship_dynamic', 'love_language', 'dealbreakers', 'about_you',
];

// [perspective, category|null, title, side] — both perspectives share the
// same 7 categories (schemas.PerspectiveBlueprint); ME's are shown as one
// combined "About you" section rather than 7 separate subsections.
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

// [value, label, note]
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

// [key, label, svg path]
export const TABS = [
  ['home', 'Home', 'M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z'],
  ['convos', 'Conversations', 'M21 12a8 8 0 0 1-8 8H7l-4 3 1.2-4.4A8 8 0 1 1 21 12z'],
  ['matches', 'Intros', ''],
  ['friends', 'Friends', 'M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20M9.5 10.5a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4M21 20v-1.4a4 4 0 0 0-3-3.8'],
  ['profile', 'You', 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7'],
];

// Frontend-only static content (PRD §5 — no backend endpoint for this).
export const STATIC_FRIENDS = [
  { initial: 'L', name: 'Léa', rel: 'Sister', quote: "She's thoughtful, adventurous, and will make you laugh every day." },
  { initial: 'T', name: 'Thomas', rel: 'Friend, 12 years', quote: 'Needs someone who can keep up with her, and who reads.' },
  { initial: 'M', name: 'Marek', rel: 'Colleague', quote: 'Warmest person in any room, but she needs her quiet.' },
];
