import { useState, useRef, useEffect } from 'react';
import { Globe, Check } from 'lucide-react';
import { useI18n } from '@/lib/i18n';

export function LanguageSwitcher() {
  const { lang, setLang, languages } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    if (open) document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [open]);

  const current = languages.find(l => l.code === lang) ?? languages[0];

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(x => !x)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-[var(--radius-sm)] hover:bg-black/5 transition-colors"
        style={{ color: 'var(--text-2)' }}
        aria-label="Select language"
      >
        <Globe size={16} />
        <span>{current?.local_name || 'English'}</span>
      </button>
      {open && (
        <div
          className="absolute right-0 mt-2 py-1 min-w-[180px] glass glass-raised z-50 max-h-[70vh] overflow-y-auto"
          style={{ borderRadius: 'var(--radius-md)' }}
        >
          {languages.map(l => (
            <button
              key={l.code}
              onClick={() => { setLang(l.code); setOpen(false); }}
              className="flex items-center justify-between w-full px-3 py-2 text-sm hover:bg-black/5 text-left"
              style={{ color: 'var(--text-1)' }}
            >
              <span>
                <span className="font-medium">{l.local_name}</span>
                <span className="ml-2 text-xs" style={{ color: 'var(--text-3)' }}>{l.name}</span>
              </span>
              {l.code === lang && <Check size={14} style={{ color: 'var(--accent-1)' }} />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
