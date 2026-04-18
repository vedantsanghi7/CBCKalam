import { cn } from '@/lib/utils';
import { forwardRef } from 'react';
import type { HTMLAttributes } from 'react';

type Props = HTMLAttributes<HTMLDivElement> & {
  tone?: 'default' | 'raised' | 'dialog';
};

export const GlassCard = forwardRef<HTMLDivElement, Props>(
  ({ className, tone = 'default', ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'glass glass-highlight',
        tone === 'raised' && 'glass-raised',
        tone === 'dialog' && 'glass-dialog',
        'p-6',
        className
      )}
      {...props}
    />
  )
);
GlassCard.displayName = 'GlassCard';
