import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { GlassCard } from '@/components/ui/GlassCard';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ConfidenceMeter } from '@/components/scheme/ConfidenceMeter';
import { PillButton } from '@/components/ui/PillButton';
import { api } from '@/lib/api';
import {
  ArrowLeft, ExternalLink, CheckCircle2, XCircle, HelpCircle,
  FileText, Shield, IndianRupee, Calendar, Building2, ClipboardList,
  AlertTriangle, BookOpen, Link2, Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import type { SchemeResult, SchemeDetail as SchemeDetailType } from '@/types';
import { TranslatedText } from '@/lib/i18n';

export default function SchemeDetail() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [result] = useState<SchemeResult | null>(location.state?.result || null);
  const [detail, setDetail] = useState<SchemeDetailType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      setLoading(true);
      api.getScheme(id)
        .then(setDetail)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--accent-1)' }} />
      </div>
    );
  }

  const benefit = detail?.benefit || {};
  const hasMonetaryBenefit = benefit.amount_inr && benefit.amount_inr > 0;

  return (
    <div className="max-w-3xl mx-auto pb-20">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 mb-6 text-sm font-medium hover:underline"
        style={{ color: 'var(--text-2)' }}
      >
        <ArrowLeft size={16} /> <TranslatedText>Back</TranslatedText>
      </button>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>

        {/* ─── Header Card ─── */}
        <GlassCard tone="raised" className="mb-6">
          <div className="flex items-start justify-between gap-4 mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Building2 size={14} style={{ color: 'var(--text-3)' }} />
                <span className="text-caption uppercase tracking-wide">
                  <TranslatedText>{detail?.ministry || id || ''}</TranslatedText>
                </span>
              </div>
              <h1 className="text-h1" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>{result?.name || detail?.name || id || ''}</TranslatedText>
              </h1>
              {detail?.category && (
                <span
                  className="inline-block text-xs px-2.5 py-0.5 mt-2 rounded-[9999px] capitalize"
                  style={{ background: 'rgba(110,108,255,0.08)', color: 'var(--accent-1)' }}
                >
                  <TranslatedText>{detail.category}</TranslatedText>
                </span>
              )}
            </div>
            {result && <StatusBadge status={result.status} />}
          </div>

          {/* Launched date */}
          {detail?.launched && (
            <div className="flex items-center gap-2 text-xs mt-2" style={{ color: 'var(--text-3)' }}>
              <Calendar size={13} />
              <span>Launched: {detail.launched}</span>
            </div>
          )}

          {/* Confidence meter (if coming from results) */}
          {result && (
            <div className="mt-4">
              <ConfidenceMeter
                value={result.confidence}
                status={result.status}
                breakdown={result.confidence_breakdown}
              />
            </div>
          )}
        </GlassCard>

        {/* ─── Description ─── */}
        {detail?.description && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen size={18} style={{ color: 'var(--accent-1)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>About this Scheme</TranslatedText>
              </h2>
            </div>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)' }}>
              <TranslatedText>{detail.description}</TranslatedText>
            </p>
          </GlassCard>
        )}

        {/* ─── Benefit ─── */}
        {detail?.benefit && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <IndianRupee size={18} style={{ color: 'var(--status-qualifies)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>Benefit Details</TranslatedText>
              </h2>
            </div>
            <div className="p-4 rounded-[var(--radius-sm)]" style={{ background: 'var(--status-qualifies-bg)' }}>
              {hasMonetaryBenefit && (
                <div className="text-2xl font-bold mb-1" style={{ color: 'var(--status-qualifies)' }}>
                  ₹{benefit.amount_inr?.toLocaleString('en-IN')}
                  {benefit.frequency && <span className="text-sm font-normal"> / {benefit.frequency}</span>}
                </div>
              )}
              <div className="space-y-1.5 mt-2">
                {benefit.type && (
                  <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-2)' }}>
                    <span className="font-medium" style={{ color: 'var(--text-1)' }}>Type:</span>
                    {benefit.type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                  </div>
                )}
                {benefit.mode && (
                  <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-2)' }}>
                    <span className="font-medium" style={{ color: 'var(--text-1)' }}>Mode:</span>
                    {benefit.mode.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                  </div>
                )}
                {benefit.installments && (
                  <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-2)' }}>
                    <span className="font-medium" style={{ color: 'var(--text-1)' }}>Installments:</span>
                    {benefit.installments}
                  </div>
                )}
                {benefit.notes && (
                  <div className="text-sm mt-2" style={{ color: 'var(--text-2)' }}>
                    <TranslatedText>{benefit.notes}</TranslatedText>
                  </div>
                )}
              </div>
            </div>
          </GlassCard>
        )}

        {/* ─── Eligibility Rules ─── */}
        {detail?.rules && detail.rules.length > 0 && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Shield size={18} style={{ color: 'var(--accent-1)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>Eligibility Rules</TranslatedText>
              </h2>
              <span className="text-xs px-2 py-0.5 rounded-[9999px]" style={{ background: 'rgba(110,108,255,0.08)', color: 'var(--accent-1)' }}>
                {detail.rules.length}
              </span>
            </div>
            <div className="space-y-3">
              {detail.rules.map(rule => {
                // Determine icon based on whether user passed this rule (if result exists)
                const evalResult = result?.rules_evaluated.find(r => r.rule_id === rule.id);
                const ruleTypeColor = rule.type === 'exclusion' ? 'var(--status-no)' :
                  rule.type === 'mandatory_doc' ? 'var(--status-uncertain)' : 'var(--accent-1)';

                return (
                  <div key={rule.id} className="p-3 rounded-[var(--radius-sm)] border" style={{ borderColor: 'rgba(0,0,0,0.06)', background: 'rgba(0,0,0,0.01)' }}>
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5">
                        {evalResult ? (
                          evalResult.result === true ? (
                            <CheckCircle2 size={18} style={{ color: 'var(--status-qualifies)' }} />
                          ) : evalResult.result === false ? (
                            <XCircle size={18} style={{ color: 'var(--status-no)' }} />
                          ) : (
                            <HelpCircle size={18} style={{ color: 'var(--status-uncertain)' }} />
                          )
                        ) : (
                          <Shield size={16} style={{ color: ruleTypeColor }} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>
                            <TranslatedText>{rule.description}</TranslatedText>
                          </span>
                          <span className="text-[10px] uppercase px-1.5 py-0.5 rounded font-medium" style={{
                            background: rule.type === 'exclusion' ? 'rgba(239,68,68,0.08)' :
                              rule.type === 'mandatory_doc' ? 'rgba(245,158,11,0.08)' : 'rgba(110,108,255,0.08)',
                            color: ruleTypeColor
                          }}>
                            {rule.type.replace(/_/g, ' ')}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded" style={{
                            background: rule.confidence === 'high' ? 'rgba(34,197,94,0.08)' : 'rgba(245,158,11,0.08)',
                            color: rule.confidence === 'high' ? 'var(--status-qualifies)' : 'var(--status-uncertain)'
                          }}>
                            {rule.confidence} confidence
                          </span>
                        </div>
                        <code className="text-xs block mt-1 px-2 py-1 rounded" style={{ background: 'rgba(0,0,0,0.03)', color: 'var(--text-3)', fontFamily: 'monospace' }}>
                          {rule.predicate}
                        </code>
                        {rule.source_text && (
                          <div className="text-xs mt-1.5" style={{ color: 'var(--text-3)' }}>
                            <TranslatedText>{rule.source_text}</TranslatedText>
                          </div>
                        )}
                        {evalResult && (
                          <div className="text-xs mt-1 italic" style={{ color: 'var(--text-3)' }}>
                            <TranslatedText>{evalResult.evidence}</TranslatedText>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </GlassCard>
        )}

        {/* ─── Gap Analysis (from result) ─── */}
        {result && result.gap_analysis.length > 0 && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} style={{ color: 'var(--status-uncertain)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>What You Need</TranslatedText>
              </h2>
            </div>
            <ul className="space-y-2">
              {result.gap_analysis.map((gap, i) => (
                <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--text-2)' }}>
                  <span style={{ color: 'var(--accent-1)' }}>→</span> <TranslatedText>{gap}</TranslatedText>
                </li>
              ))}
            </ul>
          </GlassCard>
        )}

        {/* ─── Documents Checklist ─── */}
        {detail?.documents_checklist && detail.documents_checklist.length > 0 && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <ClipboardList size={18} style={{ color: 'var(--accent-1)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>Documents Required</TranslatedText>
              </h2>
            </div>
            <ul className="space-y-2">
              {detail.documents_checklist.map((doc, i) => (
                <li key={i} className="flex items-center gap-2.5 text-sm" style={{ color: 'var(--text-2)' }}>
                  <CheckCircle2 size={15} style={{ color: 'var(--status-qualifies)' }} />
                  <TranslatedText>{doc.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</TranslatedText>
                </li>
              ))}
            </ul>
          </GlassCard>
        )}

        {/* ─── Inputs Required ─── */}
        {detail?.inputs_required && detail.inputs_required.length > 0 && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <FileText size={18} style={{ color: 'var(--accent-1)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>Information Required</TranslatedText>
              </h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {detail.inputs_required.map((input, i) => (
                <span key={i} className="text-xs px-3 py-1.5 rounded-[9999px]" style={{ background: 'rgba(110,108,255,0.06)', color: 'var(--accent-1)', border: '1px solid rgba(110,108,255,0.12)' }}>
                  {input.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </GlassCard>
        )}

        {/* ─── Ambiguity Notes (from result) ─── */}
        {result && result.ambiguity_notes.length > 0 && (
          <GlassCard className="mb-6">
            <h2 className="text-h3 mb-3" style={{ color: 'var(--status-uncertain)' }}>
              ⚠️ <TranslatedText>Ambiguity Notes</TranslatedText>
            </h2>
            <ul className="space-y-2">
              {result.ambiguity_notes.map((note, i) => (
                <li key={i} className="text-sm" style={{ color: 'var(--text-2)' }}>
                  • <TranslatedText>{note}</TranslatedText>
                </li>
              ))}
            </ul>
          </GlassCard>
        )}

        {/* ─── Apply ─── */}
        {detail?.application_url && (
          <GlassCard tone="raised" className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                  <TranslatedText>Ready to Apply?</TranslatedText>
                </h2>
                <p className="text-sm mt-1" style={{ color: 'var(--text-3)' }}>
                  <TranslatedText>Visit the official application portal</TranslatedText>
                </p>
              </div>
              <a href={detail.application_url} target="_blank" rel="noopener noreferrer">
                <PillButton>
                  <ExternalLink size={16} /> <TranslatedText>Apply Now</TranslatedText>
                </PillButton>
              </a>
            </div>
          </GlassCard>
        )}

        {/* ─── Sources ─── */}
        {detail?.sources && detail.sources.length > 0 && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Link2 size={18} style={{ color: 'var(--text-3)' }} />
              <h2 className="text-h3" style={{ color: 'var(--text-1)' }}>
                <TranslatedText>Sources</TranslatedText>
              </h2>
            </div>
            <div className="space-y-2">
              {detail.sources.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm py-2 px-3 rounded-[var(--radius-sm)] hover:underline transition-colors"
                  style={{ color: 'var(--accent-1)', background: 'rgba(110,108,255,0.03)' }}
                >
                  <ExternalLink size={14} />
                  <span className="flex-1 truncate">{src.url}</span>
                  <span className="text-caption shrink-0">{src.section} • {src.fetched_on}</span>
                </a>
              ))}
            </div>
          </GlassCard>
        )}

      </motion.div>
    </div>
  );
}
