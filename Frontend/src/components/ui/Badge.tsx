import type { ReactNode } from 'react'
import { cn } from '../../lib/cn'

export function Badge({children,icon,className}: {
  children: ReactNode
  icon?: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border border-line bg-white/70 px-3 py-1 ' +
          'text-xs font-medium text-muted backdrop-blur',
        className,
      )}
    >
      {icon}
      {children}
    </span>
  )
}
