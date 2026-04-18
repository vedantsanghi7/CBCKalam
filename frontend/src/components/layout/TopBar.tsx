import { Globe, Check, Sparkles } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useI18n } from '@/lib/i18n';
import { NavLink, useLocation } from 'react-router-dom';

export function TopBar() {
  const { lang, setLang, languages } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    if (open) document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [open]);

  const current = languages.find(l => l.code === lang) ?? languages[0];

  const navItems = [
    { to: '/', label: 'Chat' },
    { to: '/schemes', label: 'Schemes' },
    { to: '/results', label: 'Results' },
    { to: '/about', label: 'About' },
  ];

  return (
    <header className="topbar">
      <div className="topbar-inner">
        {/* Brand */}
        <NavLink to="/" className="topbar-brand">
          <div className="topbar-logo">
            <Sparkles size={18} strokeWidth={2} />
          </div>
          <span className="topbar-wordmark">KALAM</span>
          <span className="topbar-tagline">Welfare Engine</span>
        </NavLink>

        {/* Center Nav (desktop) */}
        <nav className="topbar-nav">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `topbar-nav-item ${isActive ? 'active' : ''}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Right: Language */}
        <div ref={ref} className="topbar-right">
          <button
            onClick={() => setOpen(x => !x)}
            className="topbar-lang-btn"
            aria-label="Select language"
          >
            <Globe size={15} />
            <span>{current?.local_name || 'English'}</span>
          </button>
          {open && (
            <div className="topbar-lang-dropdown glass glass-raised">
              {languages.map(l => (
                <button
                  key={l.code}
                  onClick={() => { setLang(l.code); setOpen(false); }}
                  className="topbar-lang-option"
                >
                  <span>
                    <span className="font-medium">{l.local_name}</span>
                    <span className="topbar-lang-sub">{l.name}</span>
                  </span>
                  {l.code === lang && <Check size={14} style={{ color: 'var(--accent-1)' }} />}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
