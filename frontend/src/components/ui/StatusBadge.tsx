import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';
import type { Status } from '@/types';

const map: Record<Status, { label: string; icon: React.ElementType; fg: string; bg: string }> = {
  QUALIFIES:        { label: 'Eligible',           icon: CheckCircle2,  fg: 'var(--status-qualifies)', bg: 'var(--status-qualifies-bg)' },
  ALMOST_QUALIFIES: { label: 'Almost eligible',    icon: AlertTriangle, fg: 'var(--status-almost)',    bg: 'var(--status-almost-bg)' },
  DOES_NOT_QUALIFY: { label: 'Not eligible',       icon: XCircle,       fg: 'var(--status-no)',        bg: 'var(--status-no-bg)' },
  UNCERTAIN:        { label: 'Needs clarification', icon: HelpCircle,   fg: 'var(--status-uncertain)', bg: 'var(--status-uncertain-bg)' },
};

export function StatusBadge({ status }: { status: Status }) {
  const { label, icon: Icon, fg, bg } = map[status];
  return (
    <span
      role="status"
      style={{ backgroundColor: bg, color: fg }}
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-sm font-semibold"
    >
      <Icon size={14} strokeWidth={2.25} />
      {label}
    </span>
  );
}
