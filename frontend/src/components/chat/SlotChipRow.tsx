import { X } from 'lucide-react';

interface Props {
  slots: Record<string, any>;
  onRemove?: (key: string) => void;
}

export function SlotChipRow({ slots, onRemove }: Props) {
  const entries = Object.entries(slots).filter(([, v]) => v !== null && v !== undefined && v !== 'UNKNOWN');

  if (entries.length === 0) {
    return <div className="text-sm italic" style={{ color: 'var(--text-3)' }}>No data extracted yet</div>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[9999px] text-xs font-medium"
          style={{
            background: 'rgba(110, 108, 255, 0.08)',
            color: 'var(--accent-1)',
            border: '1px solid rgba(110, 108, 255, 0.15)',
          }}
        >
          <span style={{ opacity: 0.6 }}>{key}:</span>
          <span className="font-semibold">{String(value)}</span>
          {onRemove && (
            <button onClick={() => onRemove(key)} className="ml-0.5 hover:opacity-70">
              <X size={12} />
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
