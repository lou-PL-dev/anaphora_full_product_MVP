import { useEffect, useRef, useState } from 'react';

/**
 * Wraps the browser's native SpeechRecognition API (Chrome/Edge, and Safari
 * with the webkit prefix — Firefox has no implementation, hence `supported`).
 * The browser owns speech recognition; this hook only turns its current
 * result list into plain text for the textarea.
 */
export function useSpeechToText({ onTranscript, lang = 'en-US' } = {}) {
  const [listening, setListening] = useState(false);
  const [supported] = useState(() => !!(window.SpeechRecognition || window.webkitSpeechRecognition));
  const recognitionRef = useRef(null);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;
  const stoppingRef = useRef(false);

  useEffect(() => () => recognitionRef.current?.stop(), []);

  const start = () => {
    if (!supported || listening) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = lang;
    stoppingRef.current = false;

    recognition.onresult = (event) => {
      if (stoppingRef.current) return;

      const transcript = Array.from(event.results)
        .map((result) => result?.[0]?.transcript || '')
        .join(' ')
        .replace(/\s+/g, ' ')
        .trim();

      onTranscriptRef.current?.(transcript);
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
