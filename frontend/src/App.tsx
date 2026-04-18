import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { IconRail } from '@/components/layout/IconRail';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { I18nProvider, TranslatedText } from '@/lib/i18n';
import Landing from '@/pages/Landing';
import ChatPage from '@/pages/Chat';
import Results from '@/pages/Results';
import SchemeDetail from '@/pages/SchemeDetail';
import SchemesCatalogue from '@/pages/SchemesCatalogue';
import AmbiguityMap from '@/pages/AmbiguityMap';
import About from '@/pages/About';
import KitchenSink from '@/pages/KitchenSink';

export default function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <div className="kalam-bg">
          {/* Icon Rail — desktop only */}
          <div className="hidden md:block">
            <IconRail />
          </div>

          {/* Top-right language switcher */}
          <div className="fixed top-3 right-4 z-40">
            <LanguageSwitcher />
          </div>

          {/* Main content area */}
          <main className="md:ml-[72px] p-4 md:p-6 lg:p-8 min-h-screen">
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/welcome" element={<Landing />} />
              <Route path="/schemes" element={<SchemesCatalogue />} />
              <Route path="/scheme/:id" element={<SchemeDetail />} />
              <Route path="/results" element={<Results />} />
              <Route path="/ambiguity" element={<AmbiguityMap />} />
              <Route path="/about" element={<About />} />
              <Route path="/_kitchen-sink" element={<KitchenSink />} />
            </Routes>
          </main>

          {/* Mobile bottom nav */}
          <nav className="md:hidden fixed bottom-0 inset-x-0 z-20 glass glass-raised p-2 flex justify-around" style={{ borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0' }}>
            <MobileNavLink to="/" label="Chat" />
            <MobileNavLink to="/schemes" label="Schemes" />
            <MobileNavLink to="/results" label="Results" />
            <MobileNavLink to="/about" label="About" />
          </nav>
        </div>
      </BrowserRouter>
    </I18nProvider>
  );
}

function MobileNavLink({ to, label }: { to: string; label: string }) {
  return (
    <a
      href={to}
      className="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-[var(--radius-sm)] text-xs font-medium transition-colors hover:bg-black/5"
      style={{ color: 'var(--text-2)' }}
    >
      <TranslatedText>{label}</TranslatedText>
    </a>
  );
}
