# Anaphora — Product Requirements Document

**Product:** Anaphora  
**Category:** AI-native matchmaking / relationship technology  
**Market:** European Union  
**Initial audience:** Singles aged 30–45 seeking serious relationships  
**Platform:** Mobile app + mobile-web friend experience  
**Language:** English initially; multilingual architecture with French as the next language  
**Stage:** Pre-seed product vision / V1  
**Document status:** Product Vision PRD

---

# 1. Product Vision

## 1.1 The problem

Most dating products begin with the same assumption:

**People already know exactly what they are looking for.**

Users select a few filters, write a short bio, upload photos, and are presented with hundreds of profiles.

But choosing a life partner is considerably more complex.

What people say they want, what they are attracted to, what has worked for them in previous relationships, the life they want to build, and what people close to them observe may all be different.

At the same time, swipe-based dating products optimize heavily for browsing and engagement rather than understanding and intentional matchmaking.

Anaphora takes the opposite approach.

Instead of asking:

**“Who do you want to swipe on?”**

Anaphora asks:

**“Who would actually fit you?”**

---

# 2. Product Proposition

Anaphora is an AI-native matchmaking platform that builds a rich, evolving understanding of:

### The person I am

My personality, lifestyle, relationship needs, values, patterns and circumstances.

### The person I am looking for

My preferences, attraction patterns, desired relationship dynamic, lifestyle compatibility and non-negotiables.

### What the people who know me see

Anonymous perspectives from trusted friends about the kinds of partners and relationships in which I thrive.

These three sources form the user's:

# Relationship Blueprint

The Relationship Blueprint becomes the intelligence layer used by Anaphora to curate a small number of intentional matches.

Anaphora does not promise a mathematically “perfect match.”

Instead, it identifies people who appear worth meeting and explains why.

---

# 3. Product Principles

## Depth over volume

Anaphora optimizes for fewer, more intentional introductions rather than maximum browsing.

## Conversation over forms

Where possible, users should be able to explain themselves naturally rather than translating themselves into dozens of dropdown fields.

## Discovery over interrogation

Providing information should itself create value.

Users should regularly learn something interesting about themselves or their preferences while completing their profile.

## AI that explains itself

Anaphora should not present mysterious compatibility percentages.

Match recommendations should be expressed through understandable signals such as:

**Strong fit**

or

**Worth exploring**

followed by the reasons behind the recommendation.

## Humans know things algorithms don't

Friends are treated as an additional perspective rather than merely profile endorsers.

## Preferences are not facts

Something a user says they want is one signal, not necessarily an objective truth about compatibility.

Anaphora can surface contradictions and invite reflection rather than silently deciding which signal is correct.

## Privacy by design

Relationship preferences, friend observations and personal reflections can be highly intimate.

Users should understand what information is being collected, why it is collected and how it contributes to matchmaking.

---

# 4. Target User

## Primary persona

European singles aged approximately 30–45 who:

- are looking primarily for serious relationships;
- are tired of high-volume swipe-based dating;
- value compatibility and intentionality;
- are willing to invest more time upfront for better introductions;
- are comfortable interacting conversationally with AI;
- are interested in understanding themselves as part of finding a partner.

The initial product is inclusive of genders and sexual orientations.

Gender and orientation preferences act as eligibility criteria rather than compatibility scores.

---

# 5. Core Product Model

Anaphora maintains two distinct but related profiles.

## 5.1 ME

Information describing the user.

Examples:

- age
- gender
- orientation
- location
- photos
- relationship goals
- lifestyle
- values
- personality characteristics
- social preferences
- communication style
- emotional needs
- family aspirations
- interests
- habits
- self-described physical characteristics

## 5.2 MY IDEAL PARTNER

Information describing what the user is seeking.

Examples:

- preferred genders
- age range
- geographic constraints
- physical preferences
- lifestyle preferences
- personality preferences
- values
- relationship dynamics
- attraction signals
- desired family situation
- non-negotiables
- flexible preferences

Information can enter either model from several sources.

**Explicit information:** profile settings and structured questions.

**Conversational information:** extracted from conversations with Anaphora.

**Discovery information:** derived from interactive self-reflection modules.

**Friend signals:** themes extracted anonymously from invited friends.

Anaphora must retain the provenance of important signals rather than collapsing everything into one undifferentiated profile.

---

# 6. First-Time User Journey

## Step 1 — Welcome

The user enters Anaphora.

Authentication may occur before this experience in the production product but is not the focus of the current prototype.

The welcome experience explains the proposition briefly.

Example:

**Finding the right person starts with understanding who you're looking for.**

Tell Anaphora about them in your own words.

You don't need to know exactly what matters yet. We'll discover that together.

CTA:

**Tell me who you're looking for**

---

# 7. Conversational Ideal-Partner Intake

This is the signature onboarding experience.

The user enters an AI conversation centered around one initial prompt:

# “Tell me about the person you'd love to meet.”

The user can respond through:

- text;
- voice.

Voice is transcribed into text before being processed.

The conversation should feel closer to talking with a thoughtful matchmaker than completing a form.

### Example

**User**

I'm looking for someone warm and funny, probably around my age or a little older. I really like men who don't take themselves too seriously but still have some depth.

**Anaphora**

When you say funny, what kind of funny pulls you in?

**User**

Someone with dry humour. Someone who can make fun of himself. I really don't like people who are constantly performing.

**Anaphora**

And when life gets difficult, what would you want this person to be like beside you?

---

## 7.1 AI conversation objective

The AI should primarily explore the **ideal partner**.

It should:

- identify preferences;
- notice ambiguity;
- ask useful follow-up questions;
- explore important dimensions naturally;
- distinguish preferences from dealbreakers;
- capture physical attraction where voluntarily discussed;
- allow the user to elaborate rather than forcing categorical answers.

It should not systematically interrogate the user about themselves during this stage.

However, users will naturally reveal information about themselves.

Example:

> “I'm quite independent, so I couldn't be with someone who needs to do everything together.”

Anaphora should extract:

**ME → autonomy: high**

and

**IDEAL PARTNER → comfortable with partner independence**

without interrupting the conversation to explain the extraction.

---

# 8. Structured Signal Extraction

Behind the conversational interface, Anaphora transforms natural-language conversation into structured matching information.

Potential signal groups include:

### Eligibility

- gender preference
- age preference
- location/radius
- relationship intent
- children/family constraints

### Lifestyle

- social intensity
- travel
- work/life orientation
- activity level
- home orientation
- nightlife
- routines
- pets
- substance preferences
- cultural interests

### Relationship dynamics

- independence/togetherness
- communication
- affection
- emotional expressiveness
- conflict approach
- reassurance
- spontaneity/stability

### Values

- family
- ambition
- curiosity
- kindness
- creativity
- community
- stability
- openness
- growth

### Attraction

- physical preferences
- style
- energy/presence
- humour
- intellectual attraction
- emotional attraction

### Constraints

Signals should distinguish between:

**Hard requirement**

**Strong preference**

**Nice to have**

**Open / uncertain**

This distinction is critical for future matchmaking.

---

# 9. Conversation Completion

The AI determines when it has enough information to create an initial Ideal Partner Blueprint.

It should not attempt to exhaustively profile the user during onboarding.

Example completion:

**I think I'm starting to understand who you're looking for.**

You've given me enough to build your first Relationship Blueprint.

You can always tell me more later — and some things may become clearer as you explore.

CTA:

**See my Anaphora**

The user enters the main application.

---

# 10. Main Product Experience

The main application contains four primary areas:

## HOME / BLUEPRINT

## DISCOVER

## ASK FRIENDS

## MATCHES

An ongoing **Tell Anaphora** conversational entry point should remain accessible from Home.

---

# 11. Home — Relationship Blueprint

Home communicates one fundamental idea:

# Anaphora is getting to know you.

The user sees a profile-readiness indicator.

Example:

**Your Relationship Blueprint**

**62% ready**

*The more Anaphora understands, the better your introductions can become.*

Readiness is based on meaningful information coverage, not arbitrary completion.

The interface can identify missing dimensions:

**Ideal partner**  
Strong understanding

**About you**  
Add more about your lifestyle

**Relationship needs**  
Explore what makes you feel at home

**Friends' perspective**  
2 friends have contributed

---

# 12. Tell Anaphora

Users can reopen conversational input at any point.

Prompts might include:

**There's something else Anaphora should know.**

or

**Tell me more about who you're looking for.**

Users can type or speak freely.

Examples:

> “I've realised ambition actually matters much less to me than I thought.”

> “I really need someone who likes having people over.”

> “I forgot something superficial but important: I'm really attracted to beards.”

The AI extracts new information and updates the relevant structured signals.

Where information contradicts an existing signal, Anaphora should not silently overwrite important preferences.

It can ask:

**Earlier you described ambition as quite important. It sounds like you're reconsidering that. Should I make it less important?**

This keeps the user in control of their profile.

---

# 13. Discover

Discover contains short interactive modules designed to simultaneously:

1. teach the user something about themselves;
2. improve the Relationship Blueprint;
3. increase engagement;
4. collect better matching signals.

Discoveries should generally require approximately 2–5 minutes.

They should feel playful and reflective rather than clinical.

---

# 14. Discovery Library

## Discovery 1 — What makes you feel at home?

Focus:

- emotional needs
- intimacy
- autonomy
- reassurance
- communication

Example scenario:

**You've had a horrible day. What would you most want your partner to do?**

- Hold me and listen.
- Help me solve it.
- Make me laugh.
- Give me some space.
- It depends — let me explain.

---

## Discovery 2 — What kind of life are you building?

Focus:

- lifestyle
- future aspirations
- stability
- adventure
- ambition
- community
- family
- independence

Example:

**It's 2032. Which Saturday feels most like the life you want?**

Users select among scenario cards.

Additional trade-offs might include:

Roots ↔ Freedom

Comfort ↔ Adventure

Togetherness ↔ Independence

Ambition ↔ Time

Community ↔ Privacy

---

## Discovery 3 — What creates chemistry?

Focus:

- attraction
- personality energy
- physical preferences
- interpersonal chemistry

Possible dimensions:

Playful ↔ Serious

Gentle ↔ Intense

Grounded ↔ Wild

Elegant ↔ Unconventional

Quiet ↔ Magnetic

Predictable ↔ Spontaneous

---

## Discovery 4 — How do you love?

Focus:

- communication
- closeness
- conflict
- emotional dynamics

Example:

**Your partner seems distant for two days. What's your instinct?**

Users respond through scenarios rather than diagnostic labels.

Anaphora should avoid presenting clinical conclusions such as:

“You have an anxious attachment style.”

Instead:

**When connection feels uncertain, you seem to prefer clarity and reassurance rather than distance.**

---

## Discovery 5 — Could we actually live together?

Focus:

- everyday compatibility
- routines
- money
- cleanliness
- social life
- travel
- sleep
- family
- food
- pets
- work
- leisure

Questions should frequently use playful real-life scenarios.

---

## Discovery 6 — What can't you compromise on?

Users receive a limited number of “must-have” selections.

For example:

**You have five golden cards. What genuinely needs to be present for a relationship to work?**

Anaphora can subsequently test those choices through trade-offs.

This helps differentiate:

**non-negotiable**

from

**strong preference**

from

**ideal-world preference**

---

## Discovery 7 — Relationship Archaeology

A deeper optional reflection module about previous relationships.

Users can reflect on:

- what initially attracted them;
- what worked;
- what became difficult;
- what they repeatedly needed but did not receive;
- what partners needed from them;
- what they would choose differently today.

AI may surface possible patterns but must present them as hypotheses.

Example:

**Something worth exploring**

You often describe independence as attractive, while consistency appears repeatedly among the things you've missed in relationships.

Does that resonate?

**Yes**

**A little**

**Not really**

Relationship Archaeology is a future/deeper feature and is not required for the technical MVP.

---

# 15. Discovery Results

Every Discovery should produce a small moment of value.

The experience should not simply say:

**Completed ✓**

Instead:

**Something Anaphora learned about you**

> You seem to want a relationship with strong roots but plenty of room for spontaneity. Stability matters, but not if it turns into predictability.

User can respond:

**That sounds like me**

**Not quite**

Results update the Relationship Blueprint only according to clearly defined rules.

---

# 16. Ask Friends

Friend perspective is one of Anaphora's primary product differentiators.

Users can invite trusted friends to help Anaphora understand what kind of person might suit them.

The friend does NOT need:

- an Anaphora account;
- the Anaphora app;
- a subscription.

---

# 17. Invitation Flow

User selects:

**Ask someone who knows you**

Possible sharing mechanisms:

- WhatsApp
- Instagram
- SMS
- share sheet
- copy link

Each invitation generates a unique link.

The link opens a responsive mobile webpage.

---

# 18. Friend Landing Page

Example:

**Louise trusts your judgment ❤️**

She's asked you to help Anaphora understand who might genuinely suit her.

This takes about 5 minutes.

The friend is explicitly informed:

**Your individual answers are private. Louise will not see what you wrote. Anaphora uses your answers to identify broader themes that may help with matchmaking.**

Consent must occur before submission.

---

# 19. Friend Questions

The experience begins with several lightweight questions.

Examples:

### What kind of person brings out the best in Louise?

- Someone grounding
- Someone adventurous
- Someone intellectually challenging
- Someone affectionate
- Someone independent
- Something else

### What does Louise think she wants that you're not convinced she actually needs?

Free text.

### Think about someone Louise dated who you weren't crazy about.

**What did you see that perhaps she didn't?**

No names should be requested.

### What have you seen work particularly well for Louise?

Free text.

---

# 20. Friend AI Conversation

The final stage moves from structured questions into conversation.

Prompt:

# Imagine you're setting Louise up with someone.

Tell Anaphora about them.

Who are they?

What are they like?

Why would they work together?

The friend can:

**Speak**

or

**Type**

Anaphora may ask contextual follow-up questions.

Example:

**Friend**

She needs someone funny, but not someone constantly performing.

**Anaphora**

What kind of humour works particularly well with her?

**Friend**

Dry humour. Someone ridiculous sometimes. Someone who can laugh at himself.

**Anaphora**

And when things get difficult, what kind of person do you think she needs beside her?

The conversation should remain short and enjoyable.

Target duration:

**2–4 minutes.**

---

# 21. Friend Signal Processing

Individual friend responses remain private.

Anaphora extracts structured themes from each contribution.

When several friends identify similar needs, confidence in the signal can increase.

Example internal signal:

**Partner emotional availability**

User preference: strong

Discovery evidence: strong

Friend evidence: 3/3

Confidence: high

The product should communicate convergence without revealing individual friend answers.

Example:

**People who know you consistently see emotional openness as important for you.**

---

# 22. Three-Perspective Intelligence Model

The Relationship Blueprint can distinguish three perspectives.

## WHAT I SAY I WANT

Explicit preferences and conversational information.

## WHAT I DISCOVER

Signals emerging from Discoveries and reflection.

## WHAT MY PEOPLE SEE

Aggregated themes from friends.

The system should look for both:

**convergence**

and

**tension.**

---

# 23. Productive Contradictions

Contradictions should become opportunities for reflection rather than algorithmic decisions.

Example:

**Something interesting emerged**

You describe highly social partners as attractive.

But your lifestyle choices suggest you prefer substantial quiet time, and your friends consistently describe you as happiest with calmer people.

**Worth thinking about?**

This interaction may itself generate another user-confirmed signal.

Anaphora should never treat friend opinions as more authoritative than the user's own choices.

---

# 24. Profile & Eligibility Information

In addition to the AI intelligence layer, matchmaking requires conventional profile information.

This includes:

- name
- age
- gender
- gender(s) sought
- sexual orientation where relevant
- location
- dating radius
- relationship intent
- age range sought
- profile photographs
- selected personal information

These elements are assumed to exist in the broader Anaphora product and are not the primary technical focus of the current MVP.

No identity verification system is required for the current MVP.

---

# 25. Matching

Matching is intentionally low-volume.

Anaphora does not provide an infinite profile catalogue.

Potential future matching architecture combines:

### Layer 1 — Eligibility

Hard constraints.

Examples:

- compatible gender/orientation
- age constraints
- geographic constraints
- relationship intent

Candidates failing hard eligibility criteria are excluded.

### Layer 2 — Non-negotiables

Explicitly confirmed dealbreakers.

### Layer 3 — Relationship compatibility

Comparison of structured Relationship Blueprint dimensions.

### Layer 4 — Preference relevance

Comparison with desired-partner signals.

### Layer 5 — Semantic/contextual compatibility

Richer qualitative signals may contribute to candidate evaluation.

The final model should not pretend compatibility is scientifically deterministic.

---

# 26. Match Presentation

Anaphora deliberately avoids presenting:

**92% compatible**

Instead:

# Strong fit

or

# Worth exploring

The product explains why.

Example:

**Why Anaphora thinks you should meet**

**The life you're building**

You both want strong roots, close friendships and enough flexibility to travel regularly.

**How you connect**

You value direct emotional communication. Camille describes herself similarly.

**Something you might enjoy**

You both mentioned long dinners, absurd humour and disappearing into nature for weekends.

Potential tensions may also be presented honestly.

**Something to explore**

You're more spontaneous with money, while Camille values financial planning.

The explanation should only reference information legitimately available for matchmaking and should avoid unnecessarily exposing sensitive friend commentary.

---

# 27. Monetisation

Anaphora uses a subscription model designed around increasing depth and access rather than unlimited browsing.

## FREE

Purpose:

**Experience Anaphora and start understanding what you're looking for.**

Includes:

- initial AI ideal-partner conversation;
- limited ongoing AI conversation;
- basic Relationship Blueprint;
- limited Discoveries;
- ability to complete core personal/profile preferences.

Does NOT include:

- friend invitations;
- matches.

---

## LIGHT

Purpose:

**Turn your Blueprint into introductions.**

Includes:

- expanded AI conversations;
- expanded preference/profile depth;
- additional Discoveries;
- up to 3 friend invitations;
- **1 curated match per month.**

---

## PREMIUM

Purpose:

**Give Anaphora the fullest possible picture.**

Includes:

- full Discovery library;
- expanded/unlimited conversational profiling within reasonable usage limits;
- unlimited friend invitations;
- **2 curated matches per month.**

Exact pricing is outside the scope of this PRD.

---

# 28. AI System Responsibilities

The AI layer performs four primary functions.

## Conversational exploration

Conduct natural conversations about partner preferences.

## Structured extraction

Convert free text or transcripts into defined Relationship Blueprint fields.

## Reflective synthesis

Generate user-facing observations from Discoveries and conversations.

## Friend synthesis

Convert friend feedback into private structured signals and aggregate themes.

Matching itself may later use a combination of deterministic filters, structured scoring, embeddings and LLM reasoning.

The LLM should not be the sole authority determining compatibility.

---

# 29. AI Guardrails

Anaphora should distinguish between:

**User-stated facts**

**User-stated preferences**

**Friend observations**

**AI-derived hypotheses**

AI-generated interpretations must never silently become factual profile attributes.

Sensitive inferred characteristics should be minimized.

The system should avoid inferring characteristics such as:

- medical or mental-health conditions;
- ethnicity;
- religion where not explicitly volunteered for a legitimate matching purpose;
- political ideology;
- sexual information beyond what is legitimately required for the dating service.

Where Anaphora identifies a potentially meaningful psychological pattern, it should present it as something to explore rather than a diagnosis.

---

# 30. Data Provenance

Each important Relationship Blueprint signal should ideally contain:

**Dimension**

e.g. partner_independence

**Value**

e.g. high

**Strength**

e.g. strong preference

**Perspective**

ME / IDEAL_PARTNER

**Source**

conversation / discovery / profile / friend

**Confidence**

low / medium / high

**User confirmed**

true / false

This enables explainability and future correction.

---

# 31. Profile Readiness

Profile readiness represents information coverage rather than match quality.

Potential dimensions:

- eligibility information
- ideal-partner understanding
- personal lifestyle
- relationship needs
- attraction
- values
- non-negotiables
- Discovery coverage
- friend perspective

Example:

# 62% ready

**Anaphora already understands**

✓ Who you're looking for  
✓ Your relationship intent  
✓ Your lifestyle priorities

**Help me understand**

○ What creates chemistry for you  
○ Your relationship must-haves  
○ What your friends see

Readiness should encourage meaningful actions rather than completion for its own sake.

---

# 32. Success Metrics

## Activation

Percentage of users completing initial AI conversation.

## Conversational depth

Meaningful partner-preference signals extracted per completed onboarding.

## Blueprint progression

Percentage of users who increase profile readiness after initial onboarding.

## Discovery engagement

Discovery start and completion rates.

## Reflection quality

Percentage of AI-generated Discovery insights confirmed by users as accurate/useful.

## Friend invitation rate

Percentage of eligible users inviting ≥1 friend.

## Friend response rate

Percentage of invitations resulting in completed contributions.

## Friend depth

Average number of useful structured signals extracted per contribution.

## Monetisation

Free → Light conversion.

Light → Premium conversion.

## Future matchmaking metrics

Match acceptance.

Mutual match acceptance.

Conversation initiation.

Conversation continuation.

Reported date/meeting.

Longer-term match quality.

---

# 33. V1 Product Scope

The envisioned V1 product includes:

- account/profile infrastructure;
- conversational ideal-partner onboarding;
- text and voice input;
- Relationship Blueprint;
- ongoing Tell Anaphora conversation;
- several Discoveries;
- profile readiness;
- friend invitations;
- friend mobile-web flow;
- friend AI conversation;
- structured signal extraction;
- subscription tiers;
- curated matches;
- explainable match recommendations.

---

# 34. Current Technical MVP / POC

The prototype does NOT need to implement the complete V1.

Its objective is to prove:

# Can conversational AI turn natural descriptions and lightweight self-discovery into useful structured matchmaking intelligence?

The prototype should visually communicate the broader Anaphora product while technically implementing only the core intelligence loop.

## Functional MVP

### 1. Welcome experience

Brief Anaphora introduction.

CTA into conversational onboarding.

### 2. Ideal-partner conversation

User describes desired partner.

Required:

- text conversation;
- AI follow-up questions;
- structured preference extraction.

Desirable if time permits:

- voice input;
- speech-to-text.

### 3. Relationship Blueprint generation

Conversation produces structured information.

The prototype should visibly demonstrate:

**What the user said**

→

**What Anaphora understood**

For example:

**Humour**  
Dry / self-deprecating  
Strong preference

**Relationship energy**  
Warm + independent

**Lifestyle**  
Values travel and curiosity

**Physical attraction**  
Dark hair / beard  
Preference, not requirement

### 4. Main-product shell

The prototype should show the intended future product navigation even where features are not technically functional.

Primary areas:

**Home**

**Discover**

**Ask Friends**

**Matches**

### 5. Home / readiness

Show:

- Relationship Blueprint;
- readiness percentage;
- captured signals;
- missing information;
- recommended next action.

### 6. One functional Discovery

Implement:

# What kind of life are you building?

Approximately 5–8 scenario/trade-off questions.

Answers generate structured lifestyle/value signals.

Those signals update the Relationship Blueprint/readiness state.

### 7. Discover library

Other planned Discoveries should appear in the UI but can be marked as upcoming/locked/not implemented.

### 8. Ask Friends

The product UI should demonstrate:

- invitation concept;
- up-to-3-friends Light tier;
- sharing mechanisms;
- conceptual friend contribution status.

The full friend AI journey may be represented as UI rather than technically implemented in the initial POC.

### 9. Matches

The Matches area exists visually to communicate the end-state proposition.

No functional matching algorithm is required.

Example placeholder:

**Your first introduction is being prepared.**

Complete more of your Relationship Blueprint to help Anaphora understand who might genuinely fit.

---

# 35. MVP Explicitly Out of Scope

The initial technical prototype does not require:

- real user-to-user matching;
- production recommendation engine;
- identity verification;
- moderation infrastructure;
- payment processing;
- production subscription enforcement;
- unlimited Discoveries;
- full friend-response processing;
- production push notifications;
- sophisticated trust-and-safety systems;
- custom ML models;
- proprietary recommendation models.

---

# 36. MVP Technical Hypothesis

Anaphora does not require a proprietary machine-learning model to demonstrate its central product proposition.

A credible MVP can use:

**Hosted LLM**

for conversation, follow-up questions, extraction and synthesis.

**Structured schema**

for Relationship Blueprint data.

**Application database**

for user profile and extracted signals.

**Speech-to-text API**

for optional voice interaction.

A vector database is not required for the first Relationship Blueprint MVP because actual candidate retrieval/matching is not being implemented.

This deliberately keeps the technical architecture proportional to the product hypothesis being tested.

---

# 37. Core MVP AI Flow

**User natural-language input**

↓

**Conversational LLM**

asks relevant follow-up

↓

**Conversation transcript**

↓

**Structured extraction**

↓

**Relationship Blueprint schema**

↓

**Profile readiness calculation**

↓

**User-facing insight**

↓

**User confirms / corrects / adds information**

↓

**Blueprint evolves**

This is the primary end-to-end capability the technical MVP must demonstrate.

---

# 38. Strategic Product Hypothesis

Anaphora's core hypothesis is not:

> AI can calculate who you should fall in love with.

It is:

> **AI can understand nuanced human descriptions well enough to build a richer model of relationship preferences than conventional dating profiles — and use that understanding to make fewer, more meaningful introductions.**

The MVP should prove the first half of that hypothesis.

Future matchmaking proves the second.

---

# 39. Anaphora's Product Moat

The long-term defensibility is not the LLM itself.

Foundation models are accessible to competitors.

The differentiated asset becomes the evolving structured relationship intelligence Anaphora builds through:

**Conversation**

+

**Self-discovery**

+

**Observed preferences**

+

**Friend perspective**

+

**Eventually, real match outcomes**

Over time, Anaphora can learn not simply what users claim to want, but which signals correlate with introductions they actually choose to pursue and relationships that continue.

That learning loop — built transparently and with appropriate user control — is the long-term product opportunity.

---

# 40. Product Promise

Anaphora should leave users with the feeling:

**“This understands what I'm looking for better than a dating profile ever could.”**

And eventually:

**“I understand why Anaphora thinks I should meet this person.”**