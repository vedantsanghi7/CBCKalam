import { GlassCard } from '@/components/ui/GlassCard';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ConfidenceMeter } from '@/components/scheme/ConfidenceMeter';
import { ArrowUpRight } from 'lucide-react';
import type { SchemeResult } from '@/types';
import { motion } from 'framer-motion';
import { TranslatedText } from '@/lib/i18n';

interface Props {
  result: SchemeResult;
  index: number;
  onOpen: () => void;
}

export function SchemeCard({ result, index, onOpen }: Props) {
  const benefitLine = result.benefit_if_qualified
    ? `₹${result.benefit_if_qualified.amount?.toLocaleString('en-IN')}/${result.benefit_if_qualified.frequency} via ${result.benefit_if_qualified.mode}`
    : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <GlassCard
        tone="raised"
        className="flex flex-col gap-4 p-6 hover:-translate-y-0.5 transition-transform cursor-pointer"
        onClick={onOpen}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="text-caption uppercase tracking-wide text-xs"><TranslatedText>{result.scheme_id}</TranslatedText></div>
            <h3 className="text-h3 mt-1" style={{ color: 'var(--text-1)' }}><TranslatedText>{result.name}</TranslatedText></h3>
          </div>
          <StatusBadge status={result.status} />
        </div>

        {benefitLine && (
          <p className="text-body" style={{ color: 'var(--text-2)' }}><TranslatedText>{benefitLine}</TranslatedText></p>
        )}

        <ConfidenceMeter
          value={result.confidence}
          status={result.status}
          breakdown={result.confidence_breakdown}
        />

        <div className="flex items-center justify-between mt-2">
          {result.application_order ? (
            <span className="text-caption"><TranslatedText>Suggested order</TranslatedText>: <b>#{result.application_order}</b></span>
          ) : <span />}
          <button
            onClick={(e) => { e.stopPropagation(); onOpen(); }}
            className="inline-flex items-center gap-1 text-sm font-semibold hover:underline"
            style={{ color: 'var(--text-1)' }}
          >
            <TranslatedText>View details</TranslatedText> <ArrowUpRight size={14} />
          </button>
        </div>

        {result.ambiguity_notes.length > 0 && (
          <div className="mt-2 p-3 rounded-[var(--radius-sm)]" style={{ background: 'var(--status-uncertain-bg)', color: 'var(--status-uncertain)' }}>
            <div className="text-xs font-bold uppercase tracking-wider mb-1">⚠️ <TranslatedText>Ambiguity Flags</TranslatedText></div>
            {result.ambiguity_notes.map((note, i) => (
              <div key={i} className="text-xs mt-1">• <TranslatedText>{note}</TranslatedText></div>
            ))}
          </div>
        )}

        {result.missing_inputs.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1">
            {result.missing_inputs.slice(0, 5).map(m => (
              <span key={m} className="px-2 py-0.5 rounded-[9999px] text-xs" style={{ background: 'rgba(0,0,0,0.05)', color: 'var(--text-3)' }}>
                <TranslatedText>{m}</TranslatedText>
              </span>
            ))}
            {result.missing_inputs.length > 5 && (
              <span className="text-xs text-caption">+<TranslatedText>{String(result.missing_inputs.length - 5) + ' more'}</TranslatedText></span>
            )}
          </div>
        )}
      </GlassCard>
    </motion.div>
  );
}
