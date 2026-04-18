import { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { api } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { motion } from 'framer-motion';
import type { SchemeSummary } from '@/types';
import { Compass, FileText, Search, Loader2 } from 'lucide-react';

// Simple in-memory + sessionStorage cache for schemes
const CACHE_KEY = 'kalam_schemes_cache';
let memoryCache: SchemeSummary[] | null = null;

function getCachedSchemes(): SchemeSummary[] | null {
  if (memoryCache) return memoryCache;
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (raw) {
      memoryCache = JSON.parse(raw);
      return memoryCache;
    }
  } catch {}
  return null;
}

function setCachedSchemes(schemes: SchemeSummary[]) {
  memoryCache = schemes;
  try { sessionStorage.setItem(CACHE_KEY, JSON.stringify(schemes)); } catch {}
}

export default function SchemesCatalogue() {
  const navigate = useNavigate();
  const cached = useRef(getCachedSchemes());
  const [schemes, setSchemes] = useState<SchemeSummary[]>(cached.current ?? []);
  const [loading, setLoading] = useState(!cached.current);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState<string>('all');
  const { t, translateMany, lang } = useI18n();

  useEffect(() => {
    // Always fetch fresh data in background, but show cached first
    api.listSchemes()
      .then(data => {
        setSchemes(data.schemes);
        setCachedSchemes(data.schemes);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Pre-translate scheme short descriptions & names when language changes
  useEffect(() => {
    if (schemes.length === 0 || lang === 'en' || lang === 'hinglish') return;
    const texts: string[] = [];
    schemes.forEach(s => {
      if (s.name) texts.push(s.name);
      if (s.short_description) texts.push(s.short_description);
      if (s.category) texts.push(s.category);
      if (s.ministry) texts.push(s.ministry);
    });
    translateMany(texts);
  }, [schemes, lang, translateMany]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    schemes.forEach(s => s.category && set.add(s.category));
    return Array.from(set).sort();
  }, [schemes]);

  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    return schemes.filter(s => {
      if (category !== 'all' && s.category !== category) return false;
      if (!q) return true;
      return (
        s.name.toLowerCase().includes(q) ||
        s.id.toLowerCase().includes(q) ||
        (s.short_description || '').toLowerCase().includes(q) ||
        (s.ministry || '').toLowerCase().includes(q)
      );
    });
  }, [schemes, query, category]);

  if (loading && schemes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--accent-1)' }} />
        <div className="text-body" style={{ color: 'var(--text-3)' }}>Loading schemes…</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-6">
          <Compass size={28} style={{ color: 'var(--accent-1)' }} />
          <div>
            <h1 className="text-h1" style={{ color: 'var(--text-1)' }}>{t('All Schemes')}</h1>
            <p className="text-caption">
              {schemes.length} {t('central government welfare schemes')}
            </p>
          </div>
        </div>
      </motion.div>

      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-3)' }} />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder={t('Search schemes…')}
            className="w-full pl-9 pr-3 py-2 text-sm glass"
            style={{ borderRadius: 'var(--radius-sm)', color: 'var(--text-1)' }}
          />
        </div>
        <select
          value={category}
          onChange={e => setCategory(e.target.value)}
          className="px-3 py-2 text-sm glass"
          style={{ borderRadius: 'var(--radius-sm)', color: 'var(--text-1)' }}
        >
          <option value="all">{t('All categories')}</option>
          {categories.map(c => (
            <option key={c} value={c}>{t(c)}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((scheme, i) => (
          <motion.div
            key={scheme.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(i, 8) * 0.03, duration: 0.25 }}
          >
            <GlassCard
              className="flex flex-col gap-3 p-5 hover:-translate-y-0.5 transition-transform cursor-pointer h-full"
              onClick={() => navigate(`/scheme/${scheme.id}`)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={16} style={{ color: 'var(--accent-1)' }} />
                  <span className="text-xs uppercase tracking-wider font-semibold" style={{ color: 'var(--text-3)' }}>
                    {scheme.id}
                  </span>
                </div>
                {scheme.category && (
                  <span
                    className="text-xs px-2 py-0.5 rounded-[9999px] capitalize"
                    style={{ background: 'rgba(110,108,255,0.08)', color: 'var(--accent-1)' }}
                  >
                    {t(scheme.category)}
                  </span>
                )}
              </div>
              <h3 className="text-h3" style={{ color: 'var(--text-1)' }}>{t(scheme.name)}</h3>
              {scheme.short_description && (
                <p className="text-sm line-clamp-3" style={{ color: 'var(--text-2)' }}>
                  {t(scheme.short_description)}
                </p>
              )}
              {scheme.benefit_line && (
                <p className="text-sm font-medium" style={{ color: 'var(--accent-1)' }}>
                  {scheme.benefit_line}
                </p>
              )}
              <div className="flex items-center justify-between mt-auto pt-2">
                <span className="text-caption">{t(scheme.ministry || '')}</span>
                <span className="text-xs" style={{ color: 'var(--text-3)' }}>
                  {scheme.rules_count} {t('rules')}
                </span>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-20" style={{ color: 'var(--text-3)' }}>
          {t('No schemes match your search.')}
        </div>
      )}
    </div>
  );
}
