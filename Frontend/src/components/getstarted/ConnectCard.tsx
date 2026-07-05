import { motion } from 'motion/react'
import { Check, Camera, PlaySquare, Music2, type LucideIcon } from 'lucide-react'
import { EASE } from '../../lib/motion'

const PLATFORM_ICON: Record<string, LucideIcon> = {
  instagram: Camera,
  youtube: PlaySquare,
  tiktok: Music2,
}

const PLATFORM_LABEL: Record<string, string> = {
  instagram: 'Instagram',
  youtube: 'YouTube',
  tiktok: 'TikTok',
}

export function ConnectCard({ handle, platform }: { handle: string; platform: string }) {
  const Icon = PLATFORM_ICON[platform] ?? Camera
  const label = PLATFORM_LABEL[platform] ?? platform
  const display = handle.trim() ? (handle.startsWith('@') ? handle : `@${handle}`) : '@your_handle'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: EASE }}
      className="flex items-center gap-3 rounded-2xl border border-brand-200 bg-brand-50/60 p-4"
    >
      <span className="grid h-11 w-11 place-items-center rounded-xl bg-white text-brand-600 shadow-soft">
        <Icon className="h-5 w-5" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-ink">{display}</p>
        <p className="text-xs text-muted">{label} · connected</p>
      </div>
      <span className="grid h-7 w-7 place-items-center rounded-full bg-brand-600 text-white shadow-[0_8px_20px_-8px_rgba(5,150,105,0.6)]">
        <Check className="h-4 w-4" />
      </span>
    </motion.div>
  )
}
