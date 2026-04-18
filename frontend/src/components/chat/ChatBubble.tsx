import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface Props {
  from: 'user' | 'assistant';
  children: React.ReactNode;
  timestamp?: string;
}

export function ChatBubble({ from, children, timestamp }: Props) {
  const isUser = from === 'user';
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
      className={cn('flex gap-3 w-full', isUser ? 'justify-end' : 'justify-start')}
    >
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full grid place-items-center text-white text-sm font-semibold" style={{ background: 'var(--surface-ink)' }}>
          K
        </div>
      )}
      <div className={cn('flex flex-col max-w-[78%]', isUser && 'items-end')}>
        <div
          className={cn(
            'px-5 py-3 text-body',
            isUser
              ? 'text-white rounded-3xl rounded-br-lg'
              : 'glass glass-highlight rounded-3xl rounded-bl-lg'
          )}
          style={isUser ? { background: 'var(--surface-ink)' } : undefined}
        >
          {children}
        </div>
        {timestamp && <span className="text-caption mt-1 px-2">{timestamp}</span>}
      </div>
    </motion.div>
  );
}
