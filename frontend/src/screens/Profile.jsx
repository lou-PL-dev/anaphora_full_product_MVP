import { useEffect, useMemo, useState } from 'react';
import { apiCall, getOrCreateUserId } from '../api';
import { SAGE, LAV, SKY, SAND, CLOUD } from '../theme';

const IDENTITY_OPTIONS = [
  ['woman', 'Woman'],
  ['man', 'Man'],
  ['nonbinary', 'Non-binary'],
  ['other', 'Something else'],
];

const MEETING_OPTIONS = [
  ['women', 'Women'],
  ['men', 'Men'],
  ['nonbinary', 'Non-binary'],
  ['everyone', 'Everyone'],
  ['other', 'Something else'],
];

function yearsAgoIso(years) {
  const d = new Date();
  d.setHours(12, 0, 0, 0);
  d.setFullYear(d.getFullYear() - years);
  return d.toISOString().slice(0, 10);
}

export default function Profile({ openPlans, goPrivacy, goTerms, signalCount, goBlueprint }) {
  const [userGender, setUserGender] = useState(null);
  const [userGenderDetail, setUserGenderDetail] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [savedAge, setSavedAge] = useState(null);
  const [genderPreferences, setGenderPreferences] = useState([]);
  const [genderPreferenceDetail, setGenderPreferenceDetail] = useState('');
  const [ageMin, setAgeMin] = useState(18);
  const [ageMax, setAgeMax] = useState(99);
  const [readiness, setReadiness] = useState(0);
  const [breakdown, setBreakdown] = useState({});
  const [essentialsSaving, setEssentialsSaving] = useState(false);
  const [preferencesSaving, setPreferencesSaving] = useState(false);
  const [essentialsSaved, setEssentialsSaved] = useState(false);
  const [preferencesSaved, setPreferencesSaved] = useState(false);
  const [error, setError] = useState(null);

  const uid = useMemo(() => getOrCreateUserId(), []);
  const latestAdultBirthDate = useMemo(() => yearsAgoIso(18), []);
  const earliestBirthDate = useMemo(() => yearsAgoIso(99), []);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      apiCall(uid, 'GET', '/preferences'),
      apiCall(uid, 'GET', '/readiness'),
    ]).then(([profile, ready]) => {
      if (cancelled) return;
      if (profile) {
        setUserGender(profile.user_gender || null);
        setUserGenderDetail(profile.user_gender_detail || '');
        setBirthDate(profile.birth_date || '');
        setSavedAge(profile.user_age ?? null);
        setGenderPreferences(profile.gender_preferences || []);
        setGenderPreferenceDetail(profile.gender_preference_detail || '');
        setAgeMin(profile.age_min ?? 18);
        setAgeMax(profile.age_max ?? 99);
        setEssentialsSaved(!!(profile.user_gender && profile.birth_date));
        setPreferencesSaved(!!((profile.gender_preferences || []).length && profile.age_min != null && profile.age_max != null));
      }
      if (ready) {
        setReadiness(ready.readiness_pct || 0);
        setBreakdown(ready.breakdown || {});
      }
    });
    return () => { cancelled = true; };
  }, [uid]);

  const refreshReadiness = (response) => {
    if (!response) return;
    if (response.readiness_pct != null) setReadiness(response.readiness_pct);
    if (response.readiness_breakdown) setBreakdown(response.readiness_breakdown);
    window.dispatchEvent(new CustomEvent('anaphora:readiness-updated', {
      detail: {
        readiness: response.readiness_pct,
        breakdown: response.readiness_breakdown,
      },
    }));
  };

  const chooseIdentity = (value) => {
    setUserGender(value);
    if (value !== 'other') setUserGenderDetail('');
    setEssentialsSaved(false);
    setError(null);
  };

  const toggleMeetingPreference = (value) => {
    setGenderPreferences((prev) => {
      if (value === 'everyone') return prev.includes('everyone') ? [] : ['everyone'];
      const withoutEveryone = prev.filter((item) => item !== 'everyone');
      return withoutEveryone.includes(value)
        ? withoutEveryone.filter((item) => item !== value)
        : withoutEveryone.concat(value);
    });
    if (value === 'other' && genderPreferences.includes('other')) setGenderPreferenceDetail('');
    setPreferencesSaved(false);
    setError(null);
  };

  const saveEssentials = async () => {
    if (!userGender || !birthDate || essentialsSaving) return;
    if (userGender === 'other' && !userGenderDetail.trim()) {
      setError('Tell us more about your gender.');
      return;
    }
    setEssentialsSaving(true);
    setError(null);
    const response = await apiCall(uid, 'PATCH', '/preferences', {
      user_gender: userGender,
      user_gender_detail: userGender === 'other' ? userGenderDetail.trim() : null,
      birth_date: birthDate,
    });
    setEssentialsSaving(false);
    if (!response) {
      setError("We couldn't save your essentials. Please try again.");
      return;
    }
    setSavedAge(response.user_age ?? null);
    setEssentialsSaved(true);
    refreshReadiness(response);
  };

  const saveMeetingPreferences = async () => {
    if (!genderPreferences.length || preferencesSaving) return;
    if (genderPreferences.includes('other') && !genderPreferenceDetail.trim()) {
      setError("Tell us more about who else you're open to meeting.");
      return;
    }
    setPreferencesSaving(true);
    setError(null);
    const response = await apiCall(uid, 'PATCH', '/preferences', {
      gender_preferences: genderPreferences,
      gender_preference_detail: genderPreferences.includes('other') ? genderPreferenceDetail.trim() : null,
      age_min: ageMin,
      age_max: ageMax,
    });
    setPreferencesSaving(false);
    if (!response) {
      setError("We couldn't save who you'd like to meet. Please try again.");
      return;
    }
    setPreferencesSaved(true);
    refreshReadiness(response);
  };

  const essentials = breakdown.introduction_essentials || {};
  const introductionEarned = essentials.earned || 0;
  const readinessRows = [
    ['introduction_essentials', 'Introduction essentials', 20, introductionEarned],
    ['discovery_completed', 'A Discovery completed', 20, breakdown.discovery_completed?.earned || 0],
    ['me_profile', 'About you', 30, breakdown.me_profile?.earned || 0],
    ['ideal_partner_profile', "Who you're looking for", 30, breakdown.ideal_partner_profile?.earned || 0],
  ];

  const sliderLeft = ((ageMin - 18) / 81) * 100;
  const sliderRight = 100 - ((ageMax - 18) / 81) * 100;

  return (
    <div className="ap-screen" style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: CLOUD, padding: '64px 22px 26px' }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, color: SAGE }}>You</div>
      <div style={{ marginTop: 8, fontSize: 12.5, color: LAV }}>Anonymous session · your data stays yours</div>

      <div style={{ marginTop: 24, padding: 20, borderRadius: 20, background: 'linear-gradient(145deg, #FFFFFF 0%, rgba(166,154,205,.10) 100%)', border: '1px solid rgba(166,154,205,.34)' }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: SAGE }}>YOUR ESSENTIALS</div>
        <div style={{ marginTop: 16, fontSize: 12.5, color: SAGE }}>I describe myself as</div>
        <div style={{ marginTop: 9, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {IDENTITY_OPTIONS.map(([value, label]) => {
            const selected = userGender === value;
            return <button key={value} onClick={() => chooseIdentity(value)} style={{ padding: '10px 14px', borderRadius: 999, border: `1.5px solid ${selected ? LAV : SKY}`, background: selected ? 'rgba(166,154,205,.12)' : CLOUD, color: SAGE, fontSize: 12.5, cursor: 'pointer' }}>{label}</button>;
          })}
        </div>
        {userGender === 'other' && (
          <input value={userGenderDetail} onChange={(e) => { setUserGenderDetail(e.target.value); setEssentialsSaved(false); }} placeholder="Tell us more" style={{ marginTop: 10, width: '100%', padding: '11px 12px', borderRadius: 12, border: `1px solid ${SKY}`, color: SAGE, fontSize: 13, outline: 'none' }} />
        )}

        <div style={{ marginTop: 18, fontSize: 12.5, color: SAGE }}>Date of birth</div>
        <input type="date" min={earliestBirthDate} max={latestAdultBirthDate} value={birthDate} onChange={(e) => { setBirthDate(e.target.value); setEssentialsSaved(false); setSavedAge(null); }} style={{ marginTop: 9, width: '100%', padding: '11px 12px', borderRadius: 12, border: `1px solid ${SKY}`, color: SAGE, fontSize: 13, outline: 'none', background: CLOUD }} />
        {essentialsSaved && savedAge != null && (
          <div style={{ marginTop: 10, fontSize: 11.5, color: SAGE }}>Age {savedAge} · saved ✓</div>
        )}

        <button onClick={saveEssentials} disabled={!userGender || !birthDate || essentialsSaving} style={{ marginTop: 16, width: '100%', padding: '12px 16px', borderRadius: 999, border: 'none', background: userGender && birthDate && !essentialsSaving ? SAGE : SAND, color: userGender && birthDate && !essentialsSaving ? CLOUD : SAGE, fontSize: 13, cursor: userGender && birthDate && !essentialsSaving ? 'pointer' : 'default' }}>{essentialsSaving ? 'Saving…' : 'Save your essentials'}</button>
      </div>

      <div style={{ marginTop: 14, padding: 20, borderRadius: 20, background: CLOUD, border: `1px solid ${SKY}` }}>
        <div style={{ fontSize: 11, letterSpacing: '.14em', color: SAGE }}>WHO YOU'D LIKE TO MEET</div>
        <div style={{ marginTop: 16, fontSize: 12.5, color: SAGE }}>I'm open to meeting</div>
        <div style={{ marginTop: 9, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {MEETING_OPTIONS.map(([value, label]) => {
            const selected = genderPreferences.includes(value);
            return <button key={value} onClick={() => toggleMeetingPreference(value)} style={{ padding: '10px 14px', borderRadius: 999, border: `1.5px solid ${selected ? LAV : SKY}`, background: selected ? 'rgba(166,154,205,.12)' : CLOUD, color: SAGE, fontSize: 12.5, cursor: 'pointer' }}>{label}</button>;
          })}
        </div>
        {genderPreferences.includes('other') && (
          <input value={genderPreferenceDetail} onChange={(e) => { setGenderPreferenceDetail(e.target.value); setPreferencesSaved(false); }} placeholder="Tell us more" style={{ marginTop: 10, width: '100%', padding: '11px 12px', borderRadius: 12, border: `1px solid ${SKY}`, color: SAGE, fontSize: 13, outline: 'none' }} />
        )}

        <div style={{ marginTop: 20, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12.5, color: SAGE }}>Age range</span>
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, color: SAGE }}>{ageMin}–{ageMax}</span>
        </div>
        <div style={{ position: 'relative', height: 34, marginTop: 9 }}>
          <div style={{ position: 'absolute', top: 15, left: 0, right: 0, height: 5, borderRadius: 999, background: SKY }} />
          <div style={{ position: 'absolute', top: 15, left: `${sliderLeft}%`, right: `${sliderRight}%`, height: 5, borderRadius: 999, background: LAV }} />
          <input className="ap-dual-range" aria-label="Minimum age" type="range" min="18" max="99" step="1" value={ageMin} onChange={(e) => { setAgeMin(Math.min(Number(e.target.value), ageMax)); setPreferencesSaved(false); }} />
          <input className="ap-dual-range" aria-label="Maximum age" type="range" min="18" max="99" step="1" value={ageMax} onChange={(e) => { setAgeMax(Math.max(Number(e.target.value), ageMin)); setPreferencesSaved(false); }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10.5, color: LAV }}><span>18</span><span>99+</span></div>

        {preferencesSaved && <div style={{ marginTop: 12, fontSize: 11.5, color: SAGE }}>Preferences saved ✓</div>}
        <button onClick={saveMeetingPreferences} disabled={!genderPreferences.length || preferencesSaving} style={{ marginTop: 16, width: '100%', padding: '12px 16px', borderRadius: 999, border: 'none', background: genderPreferences.length && !preferencesSaving ? SAGE : SAND, color: genderPreferences.length && !preferencesSaving ? CLOUD : SAGE, fontSize: 13, cursor: genderPreferences.length && !preferencesSaving ? 'pointer' : 'default' }}>{preferencesSaving ? 'Saving…' : "Save who you'd like to meet"}</button>
      </div>

      {error && <div style={{ marginTop: 12, padding: '11px 14px', borderRadius: 14, background: SAND, color: '#B04A3A', fontSize: 12 }}>{error}</div>}

      <div style={{ marginTop: 14, padding: 20, borderRadius: 20, border: `1px solid ${SKY}`, background: CLOUD }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: SAGE }}>Your Blueprint</div>
        <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.6, color: SAGE }}>{signalCount} signals, drawn from your own words.</div>
        <button onClick={goBlueprint} style={{ marginTop: 14, padding: '12px 20px', border: `1px solid ${SKY}`, borderRadius: 999, background: 'transparent', color: SAGE, fontSize: 13, cursor: 'pointer' }}>Review it</button>
      </div>

      {readiness < 100 && (
        <div style={{ marginTop: 14, padding: 20, borderRadius: 20, background: SAND }}>
          <div style={{ fontSize: 11, letterSpacing: '.14em', color: SAGE }}>READY FOR INTRODUCTIONS</div>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 11 }}>
            {readinessRows.map(([key, title, weight, earned]) => {
              const met = breakdown[key]?.met;
              const partial = earned > 0 && !met;
              return (
                <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ flex: 'none', width: 16, height: 16, borderRadius: '50%', border: `1.5px solid ${met || partial ? SAGE : SKY}`, background: met ? SAGE : (partial ? `linear-gradient(90deg, ${SAGE} 50%, transparent 50%)` : 'transparent') }} />
                  <span style={{ flex: 1, fontSize: 12.5, color: SAGE }}>{title}</span>
                  <span style={{ flex: 'none', fontSize: 11.5, color: LAV }}>{partial ? `${earned} / ${weight}%` : `${weight}%`}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <button onClick={openPlans} style={{ marginTop: 14, width: '100%', textAlign: 'left', padding: 20, borderRadius: 20, border: 'none', background: 'linear-gradient(140deg, rgba(166,154,205,.18), #DDEAE6)', cursor: 'pointer' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 19, color: SAGE }}>Anaphora+</div>
        <div style={{ marginTop: 6, fontSize: 12.5, color: SAGE }}>More Discoveries, deeper match explanations.</div>
      </button>

      <div style={{ marginTop: 22, textAlign: 'center', fontSize: 11, color: LAV, letterSpacing: '.02em' }}>
        <button onClick={goPrivacy} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: LAV, textDecoration: 'underline', cursor: 'pointer' }}>Privacy by design</button>{' · '}<button onClick={goTerms} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', letterSpacing: 'inherit', color: LAV, textDecoration: 'underline', cursor: 'pointer' }}>The fine print</button>
      </div>
    </div>
  );
}
