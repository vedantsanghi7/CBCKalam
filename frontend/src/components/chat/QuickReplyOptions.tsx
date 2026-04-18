import { motion } from 'framer-motion';
import { TranslatedText } from '@/lib/i18n';

interface Props {
  options: string[];
  onSelect: (option: string) => void;
}

export function QuickReplyOptions({ options, onSelect }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-wrap gap-2 ml-11"
    >
      {options.map((opt, i) => (
        <button
          key={i}
          onClick={() => onSelect(opt)}
          className="px-4 py-2 text-sm font-medium rounded-[9999px] hover:-translate-y-0.5 transition-all"
          style={{
            background: 'var(--surface-2)',
            color: 'var(--text-1)',
            border: '1px solid var(--border-ink)',
          }}
        >
          <TranslatedText>{opt}</TranslatedText>
        </button>
      ))}
    </motion.div>
  );
}
