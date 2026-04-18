import { GlassCard } from '@/components/ui/GlassCard';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import { TranslatedText } from '@/lib/i18n';

export default function About() {
  return (
    <div className="max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-8">
          <BookOpen size={28} style={{ color: 'var(--accent-1)' }} />
          <h1 className="text-h1" style={{ color: 'var(--text-1)' }}><TranslatedText>About KALAM</TranslatedText></h1>
        </div>

        <GlassCard tone="raised" className="mb-6">
          <h2 className="text-h2 mb-3" style={{ color: 'var(--text-1)' }}>🏛️ <TranslatedText>What is KALAM?</TranslatedText></h2>
          <p className="text-body" style={{ color: 'var(--text-2)' }}>
            <TranslatedText>Named after Dr. APJ Abdul Kalam, KALAM is an AI document intelligence engine for India's welfare system. Millions of Indians qualify for government schemes but never claim them because eligibility criteria are buried in bureaucratic language across hundreds of PDFs. KALAM changes that.</TranslatedText>
          </p>
        </GlassCard>

        <GlassCard className="mb-6">
          <h2 className="text-h3 mb-3" style={{ color: 'var(--text-1)' }}><TranslatedText>How it Works</TranslatedText></h2>
          <div className="space-y-3 text-sm" style={{ color: 'var(--text-2)' }}>
            <div className="flex gap-3">
              <span className="text-lg">1️⃣</span>
              <div><strong><TranslatedText>Tell us about yourself</TranslatedText></strong> — <TranslatedText>in Hindi, English, or Hinglish</TranslatedText></div>
            </div>
            <div className="flex gap-3">
              <span className="text-lg">2️⃣</span>
              <div><strong><TranslatedText>Deterministic engine evaluates</TranslatedText></strong> — <TranslatedText>no LLM decides eligibility, only verified rules</TranslatedText></div>
            </div>
            <div className="flex gap-3">
              <span className="text-lg">3️⃣</span>
              <div><strong><TranslatedText>Get explainable results</TranslatedText></strong> — <TranslatedText>with confidence scores, rule traces, and ambiguity flags</TranslatedText></div>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="mb-6">
          <h2 className="text-h3 mb-3" style={{ color: 'var(--text-1)' }}><TranslatedText>Anti-Hallucination Promise</TranslatedText></h2>
          <p className="text-sm" style={{ color: 'var(--text-2)' }}>
            <TranslatedText>The LLM never decides eligibility. A deterministic Python rule engine evaluates whether you qualify. Every rule is traceable to an official government source. "I don't know" is a first-class output — KALAM will never guess when it's uncertain.</TranslatedText>
          </p>
        </GlassCard>

        <GlassCard>
          <h2 className="text-h3 mb-3" style={{ color: 'var(--text-1)' }}><TranslatedText>18 Schemes Covered</TranslatedText></h2>
          <p className="text-sm mb-2" style={{ color: 'var(--text-2)' }}>
            PM-KISAN, MGNREGA, PMJAY, PMAY-G, PMAY-U, PMUY, PMJDY, PMJJBY, PMSBY, APY, 
            PMMVY, SSY, IGNOAPS, IGNWPS, PM SVANidhi, Stand-Up India, PM Vishwakarma, PM Kisan Maan-Dhan
          </p>
        </GlassCard>
      </motion.div>
    </div>
  );
}
