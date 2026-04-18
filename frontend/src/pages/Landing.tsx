import { useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { PillButton } from '@/components/ui/PillButton';
import { ChatComposer } from '@/components/chat/ChatComposer';
import { motion } from 'framer-motion';
import { Wheat, Heart, Home, Banknote, Shield, Baby } from 'lucide-react';
import { TranslatedText } from '@/lib/i18n';

const categories = [
  { icon: Wheat,    label: 'Farmer Schemes',    desc: '4 yojanaen', color: '#0E7A4D' },
  { icon: Heart,    label: 'Health & Insurance', desc: '3 yojanaen', color: '#E67AA8' },
  { icon: Home,     label: 'Housing',           desc: '2 yojanaen', color: '#9A5B00' },
  { icon: Banknote, label: 'Financial',          desc: '4 yojanaen', color: '#6E6CFF' },
  { icon: Shield,   label: 'Pension',            desc: '3 yojanaen', color: '#4A4690' },
  { icon: Baby,     label: 'Women & Child',      desc: '2 yojanaen', color: '#E67AA8' },
];

export default function Landing() {
  const navigate = useNavigate();

  const handleChatStart = (text: string) => {
    navigate('/', { state: { initialMessage: text } });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100dvh-64px)] max-w-3xl mx-auto px-4">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="text-center mb-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-[9999px] text-sm font-medium mb-6" style={{ background: 'var(--surface-2)', color: 'var(--text-2)' }}>
          🏛️ <TranslatedText>18 Central Government Schemes</TranslatedText>
        </div>
        <h1 className="text-display mb-4" style={{ color: 'var(--text-1)' }}>
          <TranslatedText>Namaste 🙏</TranslatedText>
        </h1>
        <p className="text-h2 font-normal mb-2" style={{ color: 'var(--text-2)' }}>
          <TranslatedText>Kaunsi sarkari yojana aapke liye hai?</TranslatedText>
        </p>
        <p className="text-body" style={{ color: 'var(--text-3)' }}>
          <TranslatedText>Chaliye pata lagate hain — Hindi, English, ya Hinglish mein baat karein</TranslatedText>
        </p>
      </motion.div>

      {/* CTA Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.5 }}
        className="flex gap-4 mb-12"
      >
        <PillButton size="lg" onClick={() => navigate('/')}>
          <TranslatedText>Start eligibility check — 2 min</TranslatedText>
        </PillButton>
        <PillButton variant="outline" size="lg" onClick={() => navigate('/schemes')}>
          <TranslatedText>Browse all 18 schemes</TranslatedText>
        </PillButton>
      </motion.div>

      {/* Category Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="grid grid-cols-2 sm:grid-cols-3 gap-4 w-full mb-12"
      >
        {categories.map(({ icon: Icon, label, desc, color }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + i * 0.06 }}
          >
            <GlassCard className="flex flex-col items-center gap-2 p-5 hover:-translate-y-1 transition-transform cursor-pointer text-center" onClick={() => navigate('/schemes')}>
              <div className="w-12 h-12 rounded-full grid place-items-center" style={{ background: color + '15', color }}>
                <Icon size={24} />
              </div>
              <div className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}><TranslatedText>{label}</TranslatedText></div>
              <div className="text-xs" style={{ color: 'var(--text-3)' }}><TranslatedText>{desc}</TranslatedText></div>
            </GlassCard>
          </motion.div>
        ))}
      </motion.div>

      {/* Composer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.45, duration: 0.5 }}
        className="w-full max-w-xl"
      >
        <ChatComposer onSend={handleChatStart} />
      </motion.div>
    </div>
  );
}
