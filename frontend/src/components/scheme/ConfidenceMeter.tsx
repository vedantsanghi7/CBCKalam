import type { Status, ConfidenceBreakdown } from '@/types';

interface Props {
  value: number;
  status: Status;
  breakdown?: ConfidenceBreakdown;
}

export function ConfidenceMeter({ value, status, breakdown }: Props) {
  const pct = Math.round(value * 100);
  const track =
    status === 'QUALIFIES' ? 'var(--status-qualifies)' :
    status === 'ALMOST_QUALIFIES' ? 'var(--status-almost)' :
    status === 'DOES_NOT_QUALIFY' ? 'var(--status-no)' :
    'var(--status-uncertain)';

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-caption">Confidence</span>
        <span className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full overflow-hidden" style={{ background: 'rgba(0,0,0,0.05)' }}>
        <div
          className="h-full rounded-full"
          style={{
            width: `${pct}%`,
            backgroundColor: track,
            transition: 'width 700ms ease-out',
          }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {breakdown && (
        <dl className="mt-2 grid grid-cols-4 gap-2 text-caption">
          <Metric k="Base" v={breakdown.base} />
          <Metric k="Data" v={breakdown.completeness} />
          <Metric k="Clarity" v={breakdown.cleanliness} />
          <Metric k="Freshness" v={breakdown.freshness} />
        </dl>
      )}
    </div>
  );
}

function Metric({ k, v }: { k: string; v: number }) {
  return (
    <div>
      <dt style={{ color: 'var(--text-3)' }}>{k}</dt>
      <dd className="font-medium" style={{ color: 'var(--text-1)' }}>{Math.round(v * 100)}%</dd>
    </div>
  );
}
