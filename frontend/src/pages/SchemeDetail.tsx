import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { GlassCard } from '@/components/ui/GlassCard';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ConfidenceMeter } from '@/components/scheme/ConfidenceMeter';
import { PillButton } from '@/components/ui/PillButton';
import { api } from '@/lib/api';
import { ArrowLeft, ExternalLink, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import type { SchemeResult, SchemeDetail as SchemeDetailType } from '@/types';
import { TranslatedText } from '@/lib/i18n';

export default function SchemeDetail() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [result] = useState<SchemeResult | null>(location.state?.result || null);
  const [detail, setDetail] = useState<SchemeDetailType | null>(null);

  useEffect(() => {
    if (id) {
      api.getScheme(id).then(setDetail).catch(console.error);
    }
  }, [id]);

  return (
    <div className="max-w-3xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 mb-6 text-sm font-medium hover:underline"
        style={{ color: 'var(--text-2)' }}
      >
        <ArrowLeft size={16} /> <TranslatedText>Back</TranslatedText>
      </button>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Header Card */}
        <GlassCard tone="raised" className="mb-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <div className="text-caption uppercase tracking-wide"><TranslatedText>{detail?.ministry || id}</TranslatedText></div>
              <h1 className="text-h1 mt-1" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>{result?.name || detail?.name || id}</TranslatedText>
              </h1>
            </div>
            {result && <StatusBadge status={result.status} />}
          </div>

          {result && (
            <ConfidenceMeter
              value={result.confidence}
              status={result.status}
              breakdown={result.confidence_breakdown}
            />
          )}

          {detail?.benefit && (
            <div className="mt-4 p-4 rounded-[var(--radius-sm)]" style={{ background: 'var(--status-qualifies-bg)' }}>
              <div className="text-sm font-semibold" style={{ color: 'var(--status-qualifies)' }}><TranslatedText>Benefit</TranslatedText></div>
              <div className="text-body mt-1" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>{`₹${detail.benefit.amount_inr?.toLocaleString('en-IN')}/${detail.benefit.frequency} (${detail.benefit.installments} installments) via ${detail.benefit.mode}`}</TranslatedText>
              </div>
            </div>
          )}
        </GlassCard>

        {/* Rules Evaluated */}
        {result && result.rules_evaluated.length > 0 && (
          <GlassCard className="mb-6">
            <h2 className="text-h3 mb-4" style={{ color: 'var(--text-1)' }}><TranslatedText>Rules Evaluated</TranslatedText></h2>
            <div className="space-y-3">
              {result.rules_evaluated.map(rule => (
                <div key={rule.rule_id} className="flex items-start gap-3 p-3 rounded-[var(--radius-sm)]" style={{ background: 'rgba(0,0,0,0.02)' }}>
                  <div className="mt-0.5">
                    {rule.result === true ? (
                      <CheckCircle2 size={18} style={{ color: 'var(--status-qualifies)' }} />
                    ) : rule.result === false ? (
                      <XCircle size={18} style={{ color: 'var(--status-no)' }} />
                    ) : (
                      <HelpCircle size={18} style={{ color: 'var(--status-uncertain)' }} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{rule.rule_id}</div>
                    <div className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}><TranslatedText>{rule.evidence}</TranslatedText></div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        )}

        {/* Gap Analysis */}
        {result && result.gap_analysis.length > 0 && (
          <GlassCard className="mb-6">
            <h2 className="text-h3 mb-3" style={{ color: 'var(--text-1)' }}><TranslatedText>What's Needed</TranslatedText></h2>
            <ul className="space-y-2">
              {result.gap_analysis.map((gap, i) => (
                <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--text-2)' }}>
                  <span className="text-base">→</span> <TranslatedText>{gap}</TranslatedText>
                </li>
              ))}
            </ul>
          </GlassCard>
        )}

        {/* Documents Checklist */}
        {result && result.documents_checklist.length > 0 && (
          <GlassCard className="mb-6">
            <h2 className="text-h3 mb-3" style={{ color: 'var(--text-1)' }}><TranslatedText>Documents Required</TranslatedText></h2>
            <ul className="space-y-2">
              {result.documents_checklist.map((doc, i) => (
                <li key={i} className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-2)' }}>
                  <CheckCircle2 size={14} style={{ color: 'var(--status-qualifies)' }} /> <TranslatedText>{doc.replace(/_/g, ' ')}</TranslatedText>
                </li>
              ))}
            </ul>
          </GlassCard>
        )}

        {/* Ambiguity Notes */}
        {result && result.ambiguity_notes.length > 0 && (
          <GlassCard className="mb-6">
            <h2 className="text-h3 mb-3" style={{ color: 'var(--status-uncertain)' }}>⚠️ <TranslatedText>Ambiguity Notes</TranslatedText></h2>
            <ul className="space-y-2">
              {result.ambiguity_notes.map((note, i) => (
                <li key={i} className="text-sm" style={{ color: 'var(--text-2)' }}>• <TranslatedText>{note}</TranslatedText></li>
              ))}
            </ul>
          </GlassCard>
        )}

        {/* Sources */}
        {detail && detail.sources && detail.sources.length > 0 && (
          <GlassCard className="mb-6">
            <h2 className="text-h3 mb-3" style={{ color: 'var(--text-1)' }}><TranslatedText>Sources</TranslatedText></h2>
            {detail.sources.map((src, i) => (
              <a
                key={i}
                href={src.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm py-2 hover:underline"
                style={{ color: 'var(--accent-1)' }}
              >
                <ExternalLink size={14} /> {src.url} <span className="text-caption">(fetched {src.fetched_on})</span>
              </a>
            ))}
          </GlassCard>
        )}
      </motion.div>
    </div>
  );
}
