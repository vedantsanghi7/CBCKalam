import { createContext, useContext, useEffect, useMemo, useState, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import { api } from './api';
import type { Language } from '@/types';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface I18nCtx {
  lang: string;
  setLang: (l: string) => void;
  languages: Language[];
  /** Synchronous lookup — returns cached translation or original */
  t: (text: string) => string;
  /**
   * Request translation for a list of strings.
   * Returns a promise that resolves to the translated strings.
   * Results are cached; subsequent calls for the same strings are instant.
   */
  translateMany: (items: string[]) => Promise<string[]>;
  /** Monotonically increasing counter that bumps on every cache update.
   *  Components that use `t()` can depend on this to re-render. */
  cacheVersion: number;
}

const Ctx = createContext<I18nCtx | null>(null);
const CACHE_LS_KEY = (lang: string) => `kalam_i18n_${lang}`;
const LANG_KEY = 'kalam_lang';

/** Languages that should never be translated (source text is already in these) */
const NO_TRANSLATE = new Set(['hinglish', 'en']);

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

/* ------------------------------------------------------------------ */
/*  Load / persist helpers (never throw)                               */
/* ------------------------------------------------------------------ */

function loadCacheFromLS(lang: string): Record<string, string> {
  try { return JSON.parse(localStorage.getItem(CACHE_LS_KEY(lang)) || '{}'); }
  catch { return {}; }
}

function saveCacheToLS(lang: string, cache: Record<string, string>) {
  try { localStorage.setItem(CACHE_LS_KEY(lang), JSON.stringify(cache)); }
  catch { /* quota exceeded — tolerable */ }
}

/* ------------------------------------------------------------------ */
/*  Provider                                                           */
/* ------------------------------------------------------------------ */

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<string>(() => localStorage.getItem(LANG_KEY) || 'hinglish');
  const [languages, setLanguages] = useState<Language[]>(DEFAULT_LANGS);
  // cacheVersion is used *only* to trigger re-renders when cache updates
  const [cacheVersion, setCacheVersion] = useState(0);

  // ---------- THE CACHE IS A REF, NOT STATE ----------
  // This is the single most important architectural decision.
  // Using a ref means translateMany always reads the *latest* cache,
  // even when multiple concurrent calls are in-flight.
  const cacheRef = useRef<Record<string, string>>(loadCacheFromLS(lang));
  // Track current lang in a ref too, so callbacks never capture stale lang
  const langRef = useRef(lang);

  // Fetch languages from backend (once)
  useEffect(() => {
    api.languages().then(r => setLanguages(r.languages)).catch(() => {});
  }, []);

  // ---------- Language change handler ----------
  const setLang = useCallback((newLang: string) => {
    if (newLang === langRef.current) return;
    // Cancel any pending translation batch from the old language
    if (flushTimer.current) {
      clearTimeout(flushTimer.current);
      flushTimer.current = null;
    }
    // Reject/resolve all pending queue items with original text
    for (const entry of pendingQueue.current) {
      entry.resolve(entry.texts);
    }
    pendingQueue.current = [];
    // Persist choice
    try { localStorage.setItem(LANG_KEY, newLang); } catch { /* quota */ }
    // Load cache for the new language
    cacheRef.current = loadCacheFromLS(newLang);
    langRef.current = newLang;
    // Trigger re-render
    setLangState(newLang);
    setCacheVersion(v => v + 1);
  }, []);

  // ---------- Synchronous translator ----------
  const t = useCallback((text: string): string => {
    if (!text) return text;
    if (NO_TRANSLATE.has(langRef.current)) return text;
    return cacheRef.current[text] ?? text;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cacheVersion]); // depend on cacheVersion so React knows when t()'s results change

  // ---------- Debounced batch translation queue ----------
  // All translateMany calls within a 50ms window are batched into one API call.
  const pendingQueue = useRef<Array<{
    texts: string[];
    resolve: (results: string[]) => void;
    reject: (err: any) => void;
  }>>([]);
  const flushTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flushQueue = useCallback(() => {
    const currentLang = langRef.current;
    const queue = pendingQueue.current;
    pendingQueue.current = [];
    flushTimer.current = null;

    if (queue.length === 0) return;

    // Collect all unique texts that need translation
    const allTexts = new Set<string>();
    for (const entry of queue) {
      for (const text of entry.texts) {
        if (text && !(text in cacheRef.current)) {
          allTexts.add(text);
        }
      }
    }

    // If everything is cached, resolve immediately
    if (allTexts.size === 0) {
      for (const entry of queue) {
        entry.resolve(entry.texts.map(x => cacheRef.current[x] ?? x));
      }
      return;
    }

    // Fire one single batch API call
    const need = Array.from(allTexts);
    api.translateBatch(
      need.map((text, i) => ({ id: String(i), text })),
      currentLang
    ).then(res => {
      // Guard: if language changed while we were waiting, discard results
      if (langRef.current !== currentLang) {
        for (const entry of queue) {
          entry.resolve(entry.texts); // return original text
        }
        return;
      }

      // Merge results into the ref cache
      const newEntries: Record<string, string> = {};
      res.items.forEach((r, i) => {
        newEntries[need[i]] = r.translated_text;
      });
      cacheRef.current = { ...cacheRef.current, ...newEntries };
      saveCacheToLS(currentLang, cacheRef.current);

      // Resolve all queued promises
      for (const entry of queue) {
        entry.resolve(entry.texts.map(x => cacheRef.current[x] ?? x));
      }

      // Bump version to trigger re-renders
      setCacheVersion(v => v + 1);
    }).catch(err => {
      // On failure, resolve with original text (graceful degradation)
      for (const entry of queue) {
        entry.resolve(entry.texts);
      }
    });
  }, []);

  // ---------- translateMany ----------
  // This is STABLE (no deps that change) because it only reads refs.
  const translateMany = useCallback((items: string[]): Promise<string[]> => {
    // Fast-path: no translation needed
    if (NO_TRANSLATE.has(langRef.current)) {
      return Promise.resolve(items);
    }

    // Fast-path: all already cached
    const cache = cacheRef.current;
    const allCached = items.every(x => !x || x in cache);
    if (allCached) {
      return Promise.resolve(items.map(x => cache[x] ?? x));
    }

    // Enqueue and schedule flush
    return new Promise((resolve, reject) => {
      pendingQueue.current.push({ texts: items, resolve, reject });
      if (!flushTimer.current) {
        flushTimer.current = setTimeout(flushQueue, 50);
      }
    });
  }, [flushQueue]);

  const value = useMemo(() => ({
    lang, setLang, languages, t, translateMany, cacheVersion
  }), [lang, setLang, languages, t, translateMany, cacheVersion]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

/* ------------------------------------------------------------------ */
/*  Hooks                                                              */
/* ------------------------------------------------------------------ */

export function useI18n() {
  const c = useContext(Ctx);
  if (!c) throw new Error('useI18n outside provider');
  return c;
}

/**
 * Translate a list of strings reactively.
 * Triggers a batch translation on mount and whenever lang or texts change.
 * Returns a lookup map { original → translated }.
 */
export function useTranslatedTexts(texts: string[]): Record<string, string> {
  const { lang, t, translateMany, cacheVersion } = useI18n();
  // local stores { langKey: string, map: Record<string, string> }
  // so we know WHICH language the local translations are for
  const [local, setLocal] = useState<{ langKey: string; map: Record<string, string> }>({
    langKey: '', map: {}
  });
  const textsKey = texts.join('\x00');
  const currentLangKey = `${lang}:${textsKey}`;

  useEffect(() => {
    if (NO_TRANSLATE.has(lang)) return;

    let cancelled = false;
    const expectedKey = `${lang}:${textsKey}`;

    translateMany(texts).then(results => {
      if (cancelled) return;
      const map: Record<string, string> = {};
      texts.forEach((x, i) => { map[x] = results[i] ?? x; });
      setLocal({ langKey: expectedKey, map });
    });

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, textsKey]);

  // Build the output map. If local is for a different lang/texts, ignore it.
  return useMemo(() => {
    const useLocal = local.langKey === currentLangKey;
    const map: Record<string, string> = {};
    texts.forEach(x => { map[x] = (useLocal ? local.map[x] : undefined) || t(x); });
    return map;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [local, cacheVersion, currentLangKey]);
}

/**
 * Render a single translated string reactively.
 */
export function TranslatedText({ children }: { children: string }) {
  const map = useTranslatedTexts([children]);
  return <>{map[children] ?? children}</>;
}
