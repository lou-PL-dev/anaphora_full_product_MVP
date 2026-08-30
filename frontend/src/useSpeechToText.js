import { useEffect, useRef, useState } from 'react';

/**
 * Wraps the browser's native SpeechRecognition API (Chrome/Edge, and Safari
 * with the webkit prefix — Firefox has no implementation, hence `supported`).
 * `onTranscript` receives the full accumulated transcript for the current
 * listening session on every result, including interim (not-yet-final) text,
 * so callers can show live feedback as the user speaks.
 */
export function useSpeechToText({ onTranscript, lang = 'en-US' } = {}) {
  const [listening, setListening] = useState(false);
  const [supported] = useState(() => !!(window.SpeechRecognition || window.webkitSpeechRecognition));
  const recognitionRef = useRef(null);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;

  // Finalized text accumulates here, one result index at a time, and is
  // never rebuilt from event.results[0..] on every event — some
  // Chrome/Android builds are known to re-fire onresult with resultIndex
  // pointing back at an already-finalized segment, and looping over the
  // full results list from scratch each time turns that browser quirk into
  // ever-growing, visibly repeated text. Tracking the highest result index
  // already committed makes a repeat firing a no-op instead.
  const finalTranscriptRef = useRef('');
  const lastFinalIndexRef = useRef(-1);

  // A fresh SpeechRecognition instance per listening session, created only
  // in start() rather than once and reused — some browsers don't reliably
  // reset their internal results list across stop()/start() on the SAME
  // instance, which would replay an earlier session's words at the start
  // of the next one no matter how the local accumulator above is reset.
  useEffect(() => () => recognitionRef.current?.stop(), []);

  const start = () => {
    if (!supported || listening) return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = lang;
    finalTranscriptRef.current = '';
    lastFinalIndexRef.current = -1;
    recognition.onresult = (e) => {
      let interim = '';
      // Only walk the results the browser flagged as new/changed since the
      // last event (resultIndex) — not the whole list from 0 every time.
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const result = e.results[i];
        if (result.isFinal) {
          if (i > lastFinalIndexRef.current) {
            finalTranscriptRef.current += (finalTranscriptRef.current ? ' ' : '') + result[0].transcript;
            lastFinalIndexRef.current = i;
          }
        } else {
          interim += result[0].transcript;
        }
      }
      const combined = interim ? `${finalTranscriptRef.current} ${interim}` : finalTranscriptRef.current;
      onTranscriptRef.current?.(combined.trim());
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  };
  const stop = () => {
    if (!listening) return;
    recognitionRef.current?.stop();
    setListening(false);
  };
  const toggle = () => (listening ? stop() : start());

  return { listening, supported, start, stop, toggle };
}
