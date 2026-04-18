import { Plus, Mic, Send, Square } from "lucide-react";
import { useState, useRef } from "react";
import { PillButton } from "@/components/ui/PillButton";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";

const LANG_TO_STT: Record<string, string> = {
  en: "en-IN", hinglish: "hi-IN", hi: "hi-IN", bn: "bn-IN", gu: "gu-IN",
  kn: "kn-IN", ml: "ml-IN", mr: "mr-IN", or: "or-IN", pa: "pa-IN",
  ta: "ta-IN", te: "te-IN", ur: "ur-IN",
};

export function ChatComposer({ onSend, disabled }: { onSend: (v: string) => void; disabled?: boolean }) {
  const [val, setVal] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const { lang, t } = useI18n();

  const startRecording = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert(t("Voice input is not supported in this browser."));
      return;
    }
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = LANG_TO_STT[lang] || "hi-IN";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setVal((prev) => prev + (prev ? " " : "") + transcript);
    };
    recognition.onend = () => {
      setIsRecording(false);
      recorderRef.current = null;
    };
    recognition.start();
    recorderRef.current = recognition as any;
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (recorderRef.current && typeof (recorderRef.current as any).stop === 'function') {
      (recorderRef.current as any).stop();
    }
    recorderRef.current = null;
    setIsRecording(false);
  };

  const browserFallback = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert(t("Voice input is not supported in this browser."));
      return;
    }
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = LANG_TO_STT[lang] || "hi-IN";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setVal((prev) => prev + (prev ? " " : "") + transcript);
    };
    recognition.start();
  };

  const submit = () => { if (val.trim() && !disabled) { onSend(val); setVal(""); } };

  return (
    <div className="glass glass-raised glass-highlight rounded-pill flex items-center gap-2 p-2">
      <button aria-label="Attach" className="w-10 h-10 rounded-full grid place-items-center hover:bg-black/5 text-text-2">
        <Plus size={20} />
      </button>
      <input
        value={val}
        onChange={(e) => setVal(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        disabled={disabled || isTranscribing}
        placeholder={isTranscribing ? t("Transcribing…") : t("Apna sawal likhein ya mic dabayein…")}
        aria-label="Your message"
        className="flex-1 bg-transparent border-0 outline-none text-body placeholder:text-text-3 px-2"
      />
      <button
        aria-label={isRecording ? "Stop recording" : "Start recording"}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isTranscribing}
        className="w-10 h-10 rounded-full grid place-items-center hover:bg-black/5 transition-colors"
        style={{ color: isRecording ? "var(--status-no)" : "var(--text-2)" }}
      >
        {isRecording ? <Square size={18} /> : <Mic size={20} />}
      </button>
      <PillButton onClick={submit} disabled={!val.trim() || disabled} size="md" aria-label="Send" className="w-11 h-11 p-0">
        <Send size={18} />
      </PillButton>
    </div>
  );
}
