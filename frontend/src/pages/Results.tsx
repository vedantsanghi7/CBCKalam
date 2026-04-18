import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { SchemeCard } from '@/components/scheme/SchemeCard';
import { PillButton } from '@/components/ui/PillButton';
import { motion } from 'framer-motion';
import type { SchemeResult, Status } from '@/types';
import { TranslatedText } from '@/lib/i18n';

const tabs: { label: string; status: Status | 'ALL' }[] = [
  { label: 'All', status: 'ALL' },
  { label: 'Eligible', status: 'QUALIFIES' },
  { label: 'Almost', status: 'ALMOST_QUALIFIES' },
  { label: 'Unclear', status: 'UNCERTAIN' },
  { label: 'Not Eligible', status: 'DOES_NOT_QUALIFY' },
];

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState<SchemeResult[]>([]);
  const [activeTab, setActiveTab] = useState<Status | 'ALL'>('ALL');

  useEffect(() => {
    if (location.state?.results) {
      setResults(location.state.results);
    } else {
      // Fallback: load from sessionStorage (saved by chat page)
      try {
        const raw = sessionStorage.getItem('kalam_results');
        if (raw) setResults(JSON.parse(raw));
      } catch {}
    }
  }, [location.state]);

  const filtered = activeTab === 'ALL' ? results : results.filter(r => r.status === activeTab);
  const counts: Record<string, number> = {};
  for (const r of results) {
    counts[r.status] = (counts[r.status] || 0) + 1;
  }

  const qualCount = counts['QUALIFIES'] || 0;
  const almostCount = counts['ALMOST_QUALIFIES'] || 0;
  const uncertainCount = counts['UNCERTAIN'] || 0;

  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
        <div className="text-4xl">📋</div>
        <div className="text-h2 text-center" style={{ color: 'var(--text-1)' }}><TranslatedText>No results yet</TranslatedText></div>
        <p className="text-body text-center" style={{ color: 'var(--text-2)' }}>
          <TranslatedText>Complete an eligibility check first to see your matched schemes</TranslatedText>
        </p>
        <PillButton onClick={() => navigate('/')}><TranslatedText>Start Check</TranslatedText></PillButton>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-h1 mb-2" style={{ color: 'var(--text-1)' }}>
          <TranslatedText>{`You are eligible for ${qualCount} schemes`}</TranslatedText>
        </h1>
        <p className="text-body" style={{ color: 'var(--text-2)' }}>
          {almostCount > 0 && <TranslatedText>{`Almost eligible for ${almostCount}. `}</TranslatedText>}
          {uncertainCount > 0 && <TranslatedText>{`Need clarity on ${uncertainCount}.`}</TranslatedText>}
        </p>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {tabs.map(tab => {
          const count = tab.status === 'ALL' ? results.length : (counts[tab.status] || 0);
          return (
            <button
              key={tab.status}
              onClick={() => setActiveTab(tab.status)}
              className="px-4 py-2 rounded-[9999px] text-sm font-medium transition-all"
              style={{
                background: activeTab === tab.status ? 'var(--surface-ink)' : 'var(--surface-2)',
                color: activeTab === tab.status ? 'white' : 'var(--text-2)',
              }}
            >
              <TranslatedText>{tab.label}</TranslatedText> ({count})
            </button>
          );
        })}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((result, i) => (
          <SchemeCard
            key={result.scheme_id}
            result={result}
            index={i}
            onOpen={() => navigate(`/scheme/${result.scheme_id}`, { state: { result } })}
          />
        ))}
      </div>
    </div>
  );
}
