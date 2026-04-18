import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/lib/api';
import { ChatBubble } from '@/components/chat/ChatBubble';
import { ChatComposer } from '@/components/chat/ChatComposer';
import { QuickReplyOptions } from '@/components/chat/QuickReplyOptions';
import { SlotChipRow } from '@/components/chat/SlotChipRow';
import { GlassCard } from '@/components/ui/GlassCard';
import { PillButton } from '@/components/ui/PillButton';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutGrid, Info, RotateCcw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { ChatMessage, SchemeResult } from '@/types';
import { TranslatedText, useI18n } from '@/lib/i18n';

const STORAGE_KEY = 'kalam_chat_state';

interface ChatState {
  sessionId: string | null;
  messages: ChatMessage[];
  slots: Record<string, any>;
  missingSlots: string[];
  readyToMatch: boolean;
  options: string[] | null;
  results: SchemeResult[] | null;
  totalKnown: number;
  totalPossible: number;
  eligibleCount: number;
}

const INITIAL_MESSAGE: ChatMessage = {
  id: '0',
  role: 'assistant',
  text: 'Namaste! 🙏 Main KALAM hoon — aapki sarkari yojanaon ke liye eligibility check karne wala AI engine. Kaunsi sarkari yojana aapke liye hai? Chaliye pata lagate hain.',
  timestamp: new Date(),
};

function loadState(): ChatState | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw);
    // Revive Date objects
    s.messages = s.messages.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) }));
    return s;
  } catch {
    return null;
  }
}

function saveState(state: ChatState) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch { /* quota exceeded — tolerable */ }
}

export default function ChatPage() {
  const navigate = useNavigate();
  const { lang, t } = useI18n();

  const saved = useRef(loadState());
  const [sessionId, setSessionId] = useState<string | null>(saved.current?.sessionId ?? null);
  const [messages, setMessages] = useState<ChatMessage[]>(saved.current?.messages ?? [INITIAL_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const [slots, setSlots] = useState<Record<string, any>>(saved.current?.slots ?? {});
  const [missingSlots, setMissingSlots] = useState<string[]>(saved.current?.missingSlots ?? []);
  const [readyToMatch, setReadyToMatch] = useState(saved.current?.readyToMatch ?? false);
  const [options, setOptions] = useState<string[] | null>(saved.current?.options ?? null);
  const [results, setResults] = useState<SchemeResult[] | null>(saved.current?.results ?? null);
  const [totalKnown, setTotalKnown] = useState(saved.current?.totalKnown ?? 0);
  const [totalPossible, setTotalPossible] = useState(saved.current?.totalPossible ?? 21);
  const [eligibleCount, setEligibleCount] = useState(saved.current?.eligibleCount ?? 0);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Persist chat state on every change
  useEffect(() => {
    saveState({ sessionId, messages, slots, missingSlots, readyToMatch, options, results, totalKnown, totalPossible, eligibleCount });
  }, [sessionId, messages, slots, missingSlots, readyToMatch, options, results, totalKnown, totalPossible, eligibleCount]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Create a session only if we don't already have one from storage
  useEffect(() => {
    if (sessionId) return;
    const init = async () => {
      try {
        const res = await api.startSession();
        setSessionId(res.session_id);
      } catch {
        setSessionId('demo-' + Date.now());
      }
    };
    init();
  }, [sessionId]);

  const addMessage = useCallback((role: 'user' | 'assistant', text: string) => {
    setMessages(prev => [...prev, {
      id: String(Date.now() + Math.random()),
      role,
      text,
      timestamp: new Date(),
    }]);
  }, []);

  const handleReset = async () => {
    // Reset backend session
    if (sessionId) {
      api.resetSession(sessionId).catch(() => {});
    }
    // Clear all state
    sessionStorage.removeItem(STORAGE_KEY);
    setMessages([INITIAL_MESSAGE]);
    setSlots({});
    setMissingSlots([]);
    setReadyToMatch(false);
    setOptions(null);
    setResults(null);
    setTotalKnown(0);
    setTotalPossible(21);
    setEligibleCount(0);
    // Start a fresh session
    try {
      const res = await api.startSession();
      setSessionId(res.session_id);
    } catch {
      setSessionId('demo-' + Date.now());
    }
  };

  const handleSend = async (text: string) => {
    if (!text.trim() || !sessionId) return;
    addMessage('user', text.trim());
    setLoading(true);
    setOptions(null);

    try {
      const data = await api.turn(sessionId, text.trim(), lang);
      addMessage('assistant', data.reply);
      setSlots(data.slots_known);
      setMissingSlots(data.slots_missing);
      setReadyToMatch(data.ready_to_match);
      setOptions(data.options);
      setTotalKnown(data.total_slots_known ?? Object.keys(data.slots_known).length);
      setTotalPossible(data.total_slots_possible ?? 21);
      setEligibleCount(data.eligible_count ?? 0);

      if (data.ready_to_match && !results) {
        handleMatch();
      }
    } catch (err) {
      addMessage('assistant', 'Maaf kijiye, connection error. Kripya dubara try karein.');
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const data = await api.match(sessionId);
      setResults(data);
      const qualCount = data.filter(r => r.status === 'QUALIFIES').length;
      const almostCount = data.filter(r => r.status === 'ALMOST_QUALIFIES').length;
      addMessage('assistant', `✅ Evaluation complete! Aap ${qualCount} yojanaon ke liye eligible hain${almostCount > 0 ? `, ${almostCount} ke liye almost eligible.` : ''} Results page par dekhein.`);
    } catch {
      addMessage('assistant', 'Engine matching mein error aaya. Kripya dubara try karein.');
    } finally {
      setLoading(false);
    }
  };

  const progressPct = totalPossible > 0 ? Math.round((totalKnown / totalPossible) * 100) : 0;

  return (
    <div className="flex gap-6 h-[calc(100dvh-32px)] max-w-6xl mx-auto overflow-hidden" style={{ maxHeight: 'calc(100dvh - 32px)' }}>
      {/* Chat Column */}
      <div className="flex-1 flex flex-col max-w-[680px] min-w-0 mx-auto">
        {/* Header */}
        <div className="mb-4 mt-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold tracking-widest uppercase" style={{
              background: 'linear-gradient(135deg, var(--accent-1), var(--accent-2))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>KALAM</span>
            <span className="w-1 h-1 rounded-full" style={{ background: 'var(--text-3)' }} />
            <span className="text-xs" style={{ color: 'var(--text-3)' }}>Welfare Eligibility Engine</span>
          </div>
          <div className="flex items-center justify-between">
            <h1 className="text-display" style={{ color: 'var(--text-1)' }}><TranslatedText>Eligibility Check</TranslatedText></h1>
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] text-xs font-medium transition-all hover:scale-105"
                style={{ background: 'rgba(239,68,68,0.08)', color: 'var(--status-no)' }}
                title="Reset conversation"
              >
                <RotateCcw size={13} /> <TranslatedText>Reset</TranslatedText>
              </button>
              {results && (
                <PillButton size="sm" onClick={() => navigate('/results', { state: { results } })}>
                  <LayoutGrid size={16} /> <TranslatedText>View Results</TranslatedText>
                </PillButton>
              )}
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-hide space-y-4 pb-4 pr-2" aria-live="polite">
          <AnimatePresence initial={false}>
            {messages.map(msg => (
              <ChatBubble key={msg.id} from={msg.role}>
                {msg.role === 'assistant' ? <TranslatedText>{msg.text}</TranslatedText> : msg.text}
              </ChatBubble>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
              <div className="w-8 h-8 rounded-full grid place-items-center text-white text-sm font-semibold" style={{ background: 'var(--surface-ink)' }}>K</div>
              <div className="glass glass-highlight px-5 py-3 rounded-3xl rounded-bl-lg flex gap-1.5 items-center">
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-1)', animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-1)', animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-1)', animationDelay: '300ms' }} />
              </div>
            </motion.div>
          )}

          {options && !loading && (
            <QuickReplyOptions options={options} onSelect={handleSend} />
          )}

          {readyToMatch && !results && !loading && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <GlassCard tone="raised" className="p-4 flex items-center justify-between">
                <span className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>
                  <TranslatedText>✅ Enough info collected. Ready to check eligibility!</TranslatedText>
                </span>
                <PillButton size="sm" onClick={handleMatch}><TranslatedText>Run Check</TranslatedText></PillButton>
              </GlassCard>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Composer */}
        <div className="mt-4">
          <ChatComposer onSend={handleSend} disabled={loading} />
        </div>
      </div>

      {/* Context Rail — desktop only */}
      <div className="hidden lg:flex flex-col gap-4 w-[320px] shrink-0">
        <GlassCard className="flex flex-col gap-3">
          <h3 className="text-sm uppercase tracking-wide font-semibold flex items-center gap-2" style={{ color: 'var(--text-2)' }}>
            <Info size={16} /> <TranslatedText>Your Information</TranslatedText>
          </h3>
          <SlotChipRow slots={slots} />
        </GlassCard>

        <GlassCard className="flex flex-col gap-3">
          <h3 className="text-sm uppercase tracking-wide font-semibold" style={{ color: 'var(--text-2)' }}>
            <TranslatedText>Progress</TranslatedText>
          </h3>
          <div className="h-2.5 w-full rounded-full overflow-hidden" style={{ background: 'rgba(0,0,0,0.05)' }}>
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%`, background: 'var(--accent-1)' }}
            />
          </div>
          <div className="text-caption"><TranslatedText>{`${totalKnown} of ${totalPossible} details known (${progressPct}%)`}</TranslatedText></div>
          {eligibleCount > 0 && (
            <div className="text-xs font-semibold" style={{ color: 'var(--status-yes)' }}>
              <TranslatedText>{`${eligibleCount} likely eligible schemes`}</TranslatedText>
            </div>
          )}
          {missingSlots.length > 0 && (
            <div className="text-xs" style={{ color: 'var(--text-3)' }}>
              <TranslatedText>{`Next: ${missingSlots.slice(0, 3).join(', ')}`}</TranslatedText>
            </div>
          )}
        </GlassCard>

        {readyToMatch && !results && (
          <GlassCard tone="raised" className="flex flex-col items-center gap-3 py-8">
            <div className="text-3xl">🎯</div>
            <div className="text-sm font-semibold text-center" style={{ color: 'var(--text-1)' }}><TranslatedText>Ready to Match!</TranslatedText></div>
            <PillButton onClick={handleMatch}><TranslatedText>Run Eligibility Engine</TranslatedText></PillButton>
          </GlassCard>
        )}

        {results && (
          <GlassCard tone="raised" className="flex flex-col items-center gap-3 py-6">
            <div className="text-3xl">✅</div>
            <div className="text-sm font-semibold text-center" style={{ color: 'var(--text-1)' }}>
              <TranslatedText>{String(results.filter(r => r.status === 'QUALIFIES' || r.status === 'ALMOST_QUALIFIES').length) + " schemes eligible"}</TranslatedText>
            </div>
            <PillButton size="sm" onClick={() => navigate('/results', { state: { results } })}>
              <TranslatedText>View Full Results</TranslatedText>
            </PillButton>
          </GlassCard>
        )}
      </div>
    </div>
  );
}
