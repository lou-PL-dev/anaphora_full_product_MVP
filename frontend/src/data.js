// Ported from project/Anaphora.dc.html (Claude Design export) — demo-mode
// fallbacks and static content the prototype used when the backend is
// unreachable, plus the fixed lookup tables the UI renders from.

export const MOCK_REPLIES = [
  "That's a good start. When you say you want someone warm — what does warmth actually look like on an ordinary Tuesday?",
  "That lands. And how do you two spend a free weekend — is it out in the world, or slow and at home?",
  "Noted. What's something you'd need them to care about, even if you never talked about it directly?",
  "Last one for now: what's the thing that would make you quietly walk away, however good everything else was?",
];

// [perspective, category, label, strength, evidence_text]
export const MOCK_SIGNALS = [
  ['IDEAL_PARTNER', 'personality', 'Warm in small, ordinary ways', 'strong_preference', 'someone who checks in without being asked'],
  ['IDEAL_PARTNER', 'personality', 'Self-deprecating humour', 'preference', "can laugh at themselves"],
  ['IDEAL_PARTNER', 'personality', 'Genuinely curious', 'preference', 'asks the second question'],
  ['IDEAL_PARTNER', 'lifestyle', 'Weekends outdoors, not out late', 'preference', 'walks, not clubs'],
  ['IDEAL_PARTNER', 'lifestyle', 'Settled in or near a city', 'preference', null],
  ['IDEAL_PARTNER', 'relationship_dynamic', 'Real conversation over small talk', 'hard_requirement', "I can't do surface"],
  ['IDEAL_PARTNER', 'relationship_dynamic', 'Comfortable with independence', 'strong_preference', 'we both need our own evenings'],
  ['IDEAL_PARTNER', 'attraction', 'An easy laugh, expressive eyes', 'preference', null],
  ['IDEAL_PARTNER', 'values', 'Family matters to them', 'strong_preference', 'close to their people'],
  ['IDEAL_PARTNER', 'values', 'Honest, even when it costs something', 'preference', null],
  ['IDEAL_PARTNER', 'dealbreakers', 'Not looking for something casual', 'hard_requirement', null],
  ['ME', 'personality', 'Thoughtful, slow to open up', 'preference', 'I take a while'],
  ['ME', 'lifestyle', 'Quiet evenings, long weekends outside', 'preference', null],
  ['ME', 'relationship_style', 'Needs depth early on', 'strong_preference', null],
  ['ME', 'values', 'Personal growth', 'preference', null],
];

export const FALLBACK_QUESTIONS = [
  {
    id: 'saturday_2032', prompt: "It's 2032. Which Saturday sounds better?", options: [
      { id: 'a', label: 'Breakfast at home, kids running around, friends over later' },
      { id: 'b', label: 'Deciding spontaneously whether to take the train to Copenhagen' },
      { id: 'c', label: 'Slow morning, creative project, dinner with a few close friends' },
      { id: 'd', label: 'Hosting 20 people tonight' },
    ],
  },
  { id: 'roots_freedom', prompt: 'Which matters more to you?', spectrum: ['Roots', 'Freedom'] },
  { id: 'comfort_adventure', prompt: 'Which matters more to you?', spectrum: ['Comfort', 'Adventure'] },
  { id: 'togetherness_independence', prompt: 'Which matters more to you?', spectrum: ['Togetherness', 'Independence'] },
];

// key -> [weight, label] — mirrors backend CATEGORY_WEIGHTS (readiness.py)
export const WEIGHTS = {
  ideal_partner_personality: [15, 'Who they are'],
  ideal_partner_lifestyle: [15, 'How they live'],
  relationship_needs: [15, 'What you need from a relationship'],
  attraction: [10, 'Attraction'],
  about_me: [15, 'About you'],
  values: [10, 'Values'],
  discovery_completed: [10, 'A Discovery completed'],
  basic_matching_preferences: [10, 'Basic matching preferences'],
};

// [perspective, category|null, title, side]
export const GROUP_DEFS = [
  ['IDEAL_PARTNER', 'personality', 'PERSONALITY', 'Who they are'],
  ['IDEAL_PARTNER', 'lifestyle', 'LIFESTYLE', 'How they live'],
  ['IDEAL_PARTNER', 'relationship_dynamic', 'RELATIONSHIP DYNAMIC', 'What you need'],
  ['IDEAL_PARTNER', 'attraction', 'ATTRACTION', 'What draws you'],
  ['IDEAL_PARTNER', 'values', 'VALUES', 'What matters'],
  ['IDEAL_PARTNER', 'dealbreakers', 'DEALBREAKERS', 'Non-negotiable'],
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
  ['matches', 'Matches', 'M12 20s-7-4.6-7-9.4A4 4 0 0 1 12 8a4 4 0 0 1 7 2.6C19 15.4 12 20 12 20z'],
  ['friends', 'Friends', 'M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20M9.5 10.5a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4M21 20v-1.4a4 4 0 0 0-3-3.8'],
  ['profile', 'You', 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7'],
];

// Frontend-only static content (PRD §5 — no backend endpoints for these yet).
export const STATIC_MATCHES = {
  primary: {
    name: 'Camille, 32', location: 'Nantes, France · 40 min away', fit: '92% Fit',
    blurb: 'You value deep conversations and kindness. Camille does too.',
    tags: ['Curious', 'Mindful', 'Adventurous'],
  },
  secondary: [
    { name: 'Élise, 29', location: 'Rennes · 88% Fit' },
    { name: 'Marion, 34', location: 'Angers · 85% Fit' },
  ],
  whyItems: [
    { title: 'Shared values', body: 'Family, honesty, personal growth — three of your five value signals.' },
    { title: 'Life rhythm', body: 'You both described weekends outdoors and quiet weeknights.' },
    { title: 'What you need', body: 'Real conversation over small talk — you marked this non-negotiable.' },
    { title: 'Your friends agree', body: 'Léa said you need someone who can keep up with you.' },
  ],
};

export const STATIC_FRIENDS = [
  { initial: 'L', name: 'Léa', rel: 'Sister', quote: "She's thoughtful, adventurous, and will make you laugh every day." },
  { initial: 'T', name: 'Thomas', rel: 'Friend, 12 years', quote: 'Needs someone who can keep up with her, and who reads.' },
  { initial: 'M', name: 'Marek', rel: 'Colleague', quote: 'Warmest person in any room, but she needs her quiet.' },
];
