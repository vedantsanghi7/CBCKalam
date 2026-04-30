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
  const [local, setLocal] = useState<Record<string, string>>({});
  // Use a serialized key to prevent unnecessary re-fires
  const textsKey = texts.join('\x00');
  // Track the lang+textsKey combo to know when to clear
  const prevKeyRef = useRef('');

  useEffect(() => {
    const currentKey = `${lang}:${textsKey}`;

    // If lang or texts changed, clear stale local state immediately
    if (prevKeyRef.current !== currentKey) {
      setLocal({});
      prevKeyRef.current = currentKey;
    }

    if (NO_TRANSLATE.has(lang)) {
      return;
    }

    let cancelled = false;

    translateMany(texts).then(results => {
      if (cancelled) return;
      const map: Record<string, string> = {};
      texts.forEach((x, i) => { map[x] = results[i] ?? x; });
      setLocal(map);
    });

    return () => { cancelled = true; };
    // translateMany is stable (ref-based), so it won't cause re-fires.
    // We deliberately omit translateMany from deps since it's stable.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, textsKey]);

  // Build the output map using both local state and the live cache via t()
  return useMemo(() => {
    const map: Record<string, string> = {};
    texts.forEach(x => { map[x] = local[x] || t(x); });
    return map;
    // cacheVersion ensures this re-computes when global cache updates
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [local, cacheVersion, textsKey]);
}

/**
 * Render a single translated string reactively.
 */
export function TranslatedText({ children }: { children: string }) {
  const map = useTranslatedTexts([children]);
  return <>{map[children] ?? children}</>;
}
