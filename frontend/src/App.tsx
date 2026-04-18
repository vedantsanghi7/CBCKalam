import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { TopBar } from '@/components/layout/TopBar';
import { I18nProvider } from '@/lib/i18n';
import { MessageCircle, Compass, Search, BookOpen } from 'lucide-react';
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
          {/* Top Bar */}
          <TopBar />

          {/* Main content area — padded for top bar */}
          <main className="main-content">
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
          <nav className="mobile-nav md:hidden">
            <MobileNavLink to="/" icon={<MessageCircle size={20} />} label="Chat" />
            <MobileNavLink to="/schemes" icon={<Compass size={20} />} label="Schemes" />
            <MobileNavLink to="/results" icon={<Search size={20} />} label="Results" />
            <MobileNavLink to="/about" icon={<BookOpen size={20} />} label="About" />
          </nav>
        </div>
      </BrowserRouter>
    </I18nProvider>
  );
}

function MobileNavLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}
    >
      {icon}
      <span>{label}</span>
    </NavLink>
  );
}
