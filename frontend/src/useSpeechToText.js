import { useEffect, useRef, useState } from 'react';

/**
 * Merge speech fragments without duplicating cumulative hypotheses.
 * Some browser SpeechRecognition implementations emit interim results like:
 *   "hello" -> "hello I" -> "hello I would".
 * Concatenating those fragments produces the repetition testers saw. This
 * helper keeps the longer cumulative hypothesis, while still joining genuinely
 * separate fragments when the browser returns them that way.
 */
function mergeSpeech(base, next) {
  const left = (base || '').trim();
  const right = (next || '').trim();
  if (!left) return right;
  if (!right) return left;

  const leftLower = left.toLowerCase();
  const rightLower = right.toLowerCase();
  if (rightLower === leftLower || rightLower.startsWith(leftLower + ' ')) return right;
  if (leftLower.startsWith(rightLower + ' ')) return left;

  const leftWords = left.split(/\s+/);
  const rightWords = right.split(/\s+/);
  const maxOverlap = Math.min(leftWords.length, rightWords.length);
  for (let overlap = maxOverlap; overlap > 0; overlap--) {
    const leftTail = leftWords.slice(-overlap).join(' ').toLowerCase();
    const rightHead = rightWords.slice(0, overlap).join(' ').toLowerCase();
    if (leftTail === rightHead) {
      return leftWords.concat(rightWords.slice(overlap)).join(' ');
    }
  }
  return `${left} ${right}`;
}

/**
 * Wraps the browser's native SpeechRecognition API (Chrome/Edge, and Safari
 * with the webkit prefix — Firefox has no implementation, hence `supported`).
 * `onTranscript` receives one de-duplicated transcript for the current
 * listening session on every result, including interim text.
 */
export function useSpeechToText({ onTranscript, lang = 'en-US' } = {}) {
  const [listening, setListening] = useState(false);
  const [supported] = useState(() => !!(window.SpeechRecognition || window.webkitSpeechRecognition));
  const recognitionRef = useRef(null);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;

  const finalTranscriptRef = useRef('');
  const lastFinalIndexRef = useRef(-1);
  const stoppingRef = useRef(false);

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
    stoppingRef.current = false;

    recognition.onresult = (e) => {
      if (stoppingRef.current) return;

      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const result = e.results[i];
        const transcript = result?.[0]?.transcript || '';
        if (!transcript.trim()) continue;

        if (result.isFinal) {
          if (i > lastFinalIndexRef.current) {
            finalTranscriptRef.current = mergeSpeech(finalTranscriptRef.current, transcript);
            lastFinalIndexRef.current = i;
          }
        } else {
          // Do not blindly concatenate interim entries. On affected browsers
          // each one can already contain the entire phrase heard so far.
          interim = mergeSpeech(interim, transcript);
        }
      }

      const combined = mergeSpeech(finalTranscriptRef.current, interim);
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
    stoppingRef.current = true;
    recognitionRef.current?.stop();
    setListening(false);
  };

  const toggle = () => (listening ? stop() : start());

  return { listening, supported, start, stop, toggle };
}
