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
  const [supported, setSupported] = useState(true);
  const recognitionRef = useRef(null);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = lang;
    recognition.onresult = (e) => {
      let transcript = '';
      for (let i = 0; i < e.results.length; i++) transcript += e.results[i][0].transcript;
      onTranscriptRef.current?.(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    return () => recognition.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  const start = () => {
    if (!recognitionRef.current || listening) return;
    setListening(true);
    recognitionRef.current.start();
  };
  const stop = () => {
    if (!recognitionRef.current || !listening) return;
    recognitionRef.current.stop();
    setListening(false);
  };
  const toggle = () => (listening ? stop() : start());

  return { listening, supported, start, stop, toggle };
}
