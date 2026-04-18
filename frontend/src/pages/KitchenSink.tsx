import { GlassCard } from '@/components/ui/GlassCard';
import { PillButton } from '@/components/ui/PillButton';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ConfidenceMeter } from '@/components/scheme/ConfidenceMeter';
import { ChatComposer } from '@/components/chat/ChatComposer';

export default function KitchenSink() {
  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-32">
      <div>
        <h1 className="text-display">Design System Reference</h1>
        <p className="text-body mt-2">Checking tokens, glassmorphism, and components against the frontend.md specification.</p>
      </div>

      <section className="space-y-4">
        <h2 className="text-h2">1. Glass Cards</h2>
        <div className="grid grid-cols-2 gap-6">
          <GlassCard>
            <h3 className="text-h3">Default Glass</h3>
            <p className="text-body mt-2">Surface 1 with blur-md and standard shadow. Has top white pseudo-highlight.</p>
          </GlassCard>
          
          <GlassCard tone="raised">
            <h3 className="text-h3">Raised Glass</h3>
            <p className="text-body mt-2">Surface 2 with heavier shadow for prominent floating elements.</p>
          </GlassCard>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-h2">2. Primary Buttons (Pill)</h2>
        <div className="flex gap-4 items-center">
          <PillButton size="lg">Large Send</PillButton>
          <PillButton size="md">Primary</PillButton>
          <PillButton size="sm">Small Action</PillButton>
          <PillButton variant="ghost">Ghost Pill</PillButton>
          <PillButton variant="outline">Outline</PillButton>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-h2">3. Status Badges</h2>
        <div className="flex gap-4">
          <StatusBadge status="QUALIFIES" />
          <StatusBadge status="ALMOST_QUALIFIES" />
          <StatusBadge status="UNCERTAIN" />
          <StatusBadge status="DOES_NOT_QUALIFY" />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-h2">4. Complex Components</h2>
        <div className="grid grid-cols-2 gap-6">
          <GlassCard>
            <h3 className="text-h3 mb-4">Confidence Meter</h3>
            <ConfidenceMeter 
              value={0.88} 
              status="QUALIFIES" 
              breakdown={{ base: 0.9, completeness: 1.0, cleanliness: 0.8, freshness: 0.8 }} 
            />
          </GlassCard>

          <div className="flex flex-col gap-4">
            <h3 className="text-h3">Chat Composer</h3>
            <ChatComposer onSend={(v) => console.log(v)} />
          </div>
        </div>
      </section>

    </div>
  );
}
