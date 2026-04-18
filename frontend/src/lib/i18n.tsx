import { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { api } from './api';
import type { Language } from '@/types';

interface I18nCtx {
  lang: string;
  setLang: (l: string) => void;
  languages: Language[];
  t: (text: string) => string;
  translateMany: (items: string[]) => Promise<string[]>;
}

const Ctx = createContext<I18nCtx | null>(null);
const CACHE_KEY = (lang: string) => `kalam_i18n_${lang}`;
const LANG_KEY = 'kalam_lang';

const DEFAULT_LANGS: Language[] = [
  { code: 'hinglish', name: 'Hinglish', local_name: 'Hinglish' },
  { code: 'en', name: 'English', local_name: 'English' },
  { code: 'hi', name: 'Hindi', local_name: 'हिन्दी' },
  { code: 'bn', name: 'Bengali', local_name: 'বাংলা' },
  { code: 'gu', name: 'Gujarati', local_name: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', local_name: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', local_name: 'മലയാളം' },
  { code: 'mr', name: 'Marathi', local_name: 'मराठी' },
  { code: 'or', name: 'Odia', local_name: 'ଓଡ଼ିଆ' },
  { code: 'pa', name: 'Punjabi', local_name: 'ਪੰਜਾਬੀ' },
  { code: 'ta', name: 'Tamil', local_name: 'தமிழ்' },
  { code: 'te', name: 'Telugu', local_name: 'తెలుగు' },
  { code: 'ur', name: 'Urdu', local_name: 'اردو' },
];

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<string>(() => localStorage.getItem(LANG_KEY) || 'hinglish');
  const [languages, setLanguages] = useState<Language[]>(DEFAULT_LANGS);
  const [cache, setCache] = useState<Record<string, string>>(() => {
    try { return JSON.parse(localStorage.getItem(CACHE_KEY(lang)) || '{}'); }
    catch { return {}; }
  });

  useEffect(() => {
    api.languages().then(r => setLanguages(r.languages)).catch(() => {});
  }, []);

  useEffect(() => {
    try {
      setCache(JSON.parse(localStorage.getItem(CACHE_KEY(lang)) || '{}'));
    } catch { setCache({}); }
  }, [lang]);

  const setLang = useCallback((l: string) => {
    try { localStorage.setItem(LANG_KEY, l); } catch (e) { console.warn('Storage quota exceeded'); }
    setLangState(l);
  }, []);

  const persist = useCallback((next: Record<string, string>) => {
    try { localStorage.setItem(CACHE_KEY(lang), JSON.stringify(next)); } catch (e) { console.warn('Cache quota exceeded'); }
  }, [lang]);

  const t = useCallback((text: string) => {
    if (!text) return text;
    if (lang === 'hinglish') return text;
    return cache[text] ?? text;
  }, [lang, cache]);

  const translateMany = useCallback(async (items: string[]): Promise<string[]> => {
    const currentLang = lang;
    if (currentLang === 'hinglish') return items;
    
    // Determine what's missing using the closure cache
    const need = Array.from(new Set(items.filter(x => x && !(x in cache))));
    if (need.length === 0) return items.map(x => cache[x] ?? x);
    
    try {
      const res = await api.translateBatch(
        need.map((text, i) => ({ id: String(i), text })),
        currentLang
      );
      
      const newMap: Record<string, string> = {};
      res.items.forEach((r, i) => { newMap[need[i]] = r.translated_text; });
      
      setCache(prev => {
        // ALWAYS use functional update to prevent overlapping closures from wiping each other's cache!
        const next = { ...prev, ...newMap };
        try { localStorage.setItem(CACHE_KEY(currentLang), JSON.stringify(next)); } catch (e) {}
        return next;
      });
      
      return items.map(x => newMap[x] ?? cache[x] ?? x);
    } catch {
      return items;
    }
  }, [lang, cache]);

  const value = useMemo(() => ({ lang, setLang, languages, t, translateMany }),
    [lang, setLang, languages, t, translateMany]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n() {
  const c = useContext(Ctx);
  if (!c) throw new Error('useI18n outside provider');
  return c;
}

/** Translate a list of strings and return the lookup map, caching them. */
export function useTranslatedTexts(texts: string[]): Record<string, string> {
  const { lang, t, translateMany } = useI18n();
  const [, force] = useState(0);
  useEffect(() => {
    if (lang === 'hinglish') return;
    translateMany(texts).then(() => force(x => x + 1));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, texts.join('|')]);
  const map: Record<string, string> = {};
  texts.forEach(x => { map[x] = t(x); });
  return map;
}

export function TranslatedText({ children }: { children: string }) {
  useTranslatedTexts([children]);
  const { t } = useI18n();
  return <>{t(children)}</>;
}
