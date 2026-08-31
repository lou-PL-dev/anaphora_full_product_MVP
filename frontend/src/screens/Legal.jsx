// Privacy Policy + Terms & Conditions — content reflects the actual current
// implementation (what's really collected, who really processes it, what
// rights actually work today) rather than generic boilerplate or promises
// the product doesn't yet keep. Not legal advice — have this reviewed
// before a real launch. See PLACEHOLDER_CONTACT_EMAIL below.
import { useEffect, useRef } from 'react';

const PLACEHOLDER_CONTACT_EMAIL = 'privacy@anaphora.app';

const h2 = { marginTop: 28, fontFamily: "'Playfair Display', serif", fontSize: 19, color: '#2F4A3F' };
const h3 = { marginTop: 18, fontSize: 13.5, fontWeight: 600, color: '#2F4A3F' };
const p = { marginTop: 8, fontSize: 13, lineHeight: 1.65, color: '#4A5C53' };
const li = { marginTop: 6, fontSize: 13, lineHeight: 1.6, color: '#4A5C53' };

export default function Legal({ goBack, section }) {
  const privacyRef = useRef(null);
  const termsRef = useRef(null);

  useEffect(() => {
    const target = section === 'terms' ? termsRef.current : privacyRef.current;
    if (target) target.scrollIntoView({ block: 'start' });
  }, [section]);

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#FBF9F6' }}>
      <div style={{ padding: '64px 22px 6px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={goBack} style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid rgba(47,74,63,.12)', background: 'transparent', color: '#2F4A3F', fontSize: 15, cursor: 'pointer', display: 'grid', placeItems: 'center' }}>←</button>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 24, color: '#2F4A3F' }}>Important Legalities</div>
      </div>

      <div style={{ padding: '18px 22px 60px', maxWidth: 520 }}>
        <div style={{ fontSize: 12.5, lineHeight: 1.6, color: '#94A09A' }}>
          Last updated 2026-08-31. Anaphora is a student capstone MVP — this describes what the product
          actually does today, not a finished commercial service. It's written to be honest and specific
          about our real setup, not to be exhaustive; get a lawyer's eyes on it before a real launch.
        </div>

        <div ref={privacyRef} style={h2}>Privacy Policy</div>

        <div style={h3}>What we collect</div>
        <div style={p}>You're identified by a random ID your device generates and stores locally — no
          name, email, or login is required. Tied to that ID, we collect what you tell Anaphora in
          conversation, the structured Blueprint signals and narrative portrait we extract from it,
          your answers to the Discovery questions, and basic matching preferences (gender you're
          interested in, age range) if you set them.</div>

        <div style={h3}>Sensitive information</div>
        <div style={p}>Describing who you'd love to meet naturally touches on things the law treats as
          sensitive — who you're attracted to, and sometimes values like religion or politics. By having
          the conversation, you're explicitly consenting to Anaphora processing that information for the
          one purpose of building your Blueprint and finding matches. We don't use it for anything else.</div>

        <div style={h3}>Why we collect it</div>
        <div style={p}>Solely to build your Relationship Blueprint, compute how complete it is, and — once
          it's complete — find and explain candidate matches. Nothing here is used for advertising or
          sold to anyone.</div>

        <div style={h3}>Who else processes it</div>
        <ul style={{ margin: '8px 0 0', paddingLeft: 18 }}>
          <li style={li}><strong>OpenAI</strong> — every conversation turn, extraction, and match
            explanation is processed by OpenAI's API to generate it. This is the core of how Anaphora
            works and can't be turned off.</li>
          <li style={li}><strong>LangSmith</strong> — only when we've turned on debugging traces during
            development; not active by default in production use.</li>
          <li style={li}><strong>Render</strong> — hosts our backend and database (in Frankfurt, Germany).</li>
          <li style={li}><strong>Netlify</strong> — hosts and serves this app itself.</li>
        </ul>
        <div style={p}>OpenAI and LangSmith are US-based and process data outside the EU under their own
          standard safeguards. Our own database lives in the EU (Frankfurt).</div>

        <div style={h3}>How long we keep it</div>
        <div style={p}>We keep your data for as long as your Blueprint is active. We don't yet have an
          automatic deletion schedule — this is a known gap for an MVP at this stage, not a deliberate
          choice to keep data indefinitely. See "Your rights" below for how to request deletion now.</div>

        <div style={h3}>Your rights</div>
        <ul style={{ margin: '8px 0 0', paddingLeft: 18 }}>
          <li style={li}><strong>Access</strong> — see everything Anaphora has inferred about you anytime
            on the Blueprint screen.</li>
          <li style={li}><strong>Correction</strong> — edit or correct any individual signal directly from
            the Blueprint screen.</li>
          <li style={li}><strong>Deletion and export</strong> — not yet available as a self-service button
            in the app. Email <strong>{PLACEHOLDER_CONTACT_EMAIL}</strong> with your device ID (visible in
            your browser's local storage) and we'll handle it manually.</li>
        </ul>

        <div style={h3}>Security</div>
        <div style={p}>Data is transmitted over HTTPS. As an active MVP, some hardening — like restricting
          which sites can call our API — is still on our list rather than done.</div>

        <div ref={termsRef} style={h2}>Terms & Conditions</div>

        <div style={h3}>What this is</div>
        <div style={p}>Anaphora is an early-stage matchmaking product. It doesn't promise a
          mathematically perfect match — it aims to identify people worth meeting and explain why.
          Match suggestions, narrative portraits, and explanations are AI-generated and may be
          imperfect or occasionally wrong.</div>

        <div style={h3}>Who can use it</div>
        <div style={p}>Intended for adults seeking a serious relationship. We don't currently verify
          identity or age — please don't use Anaphora if you're under 18.</div>

        <div style={h3}>Acceptable use</div>
        <div style={p}>Be honest about who you are. No impersonation, harassment, or using the product
          to harm someone else — including anyone who contributes a Friend perspective about you.</div>

        <div style={h3}>No warranty</div>
        <div style={p}>Provided "as is," as an active work in progress, with no guarantee of uptime,
          accuracy, or outcomes. We're not liable for decisions you make based on a match or insight
          Anaphora surfaces.</div>

        <div style={h3}>Changes</div>
        <div style={p}>We may update this page as the product changes — meaningfully faster than a
          mature company would, since this is still evolving day to day. Check back here for the current
          version.</div>

        <div style={h3}>Contact</div>
        <div style={p}>Questions, requests, or concerns: <strong>{PLACEHOLDER_CONTACT_EMAIL}</strong>.</div>
      </div>
    </div>
  );
}
