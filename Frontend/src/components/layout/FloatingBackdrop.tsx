import { motion } from 'motion/react'
import { ImageWithFallback } from '../ui/ImageWithFallback'
import { EASE } from '../../lib/motion'
import { CONTENT_FEED } from '../../config/site'

// thumbnails behind input form
const TILES = [
  { img: CONTENT_FEED[3], cls: 'left-[5%] top-[10%] w-32 -rotate-6', dur: 6 },
  { img: CONTENT_FEED[1], cls: 'right-[6%] top-[14%] w-28 rotate-4', dur: 7 },
  { img: CONTENT_FEED[6], cls: 'left-[3%] top-[52%] w-24 rotate-3', dur: 5.5 },
  { img: CONTENT_FEED[2], cls: 'right-[4%] top-[55%] w-32 -rotate-3', dur: 6.5 },
  { img: CONTENT_FEED[4], cls: 'bottom-[9%] left-[11%] w-28 rotate-5', dur: 7.5 },
  { img: CONTENT_FEED[11], cls: 'bottom-[7%] right-[10%] w-24 -rotate-4', dur: 6 },
]

export function FloatingBackdrop() {
  return (
    <div className="pointer-events-none fixed inset-0 hidden overflow-hidden lg:block" aria-hidden>
      {TILES.map((t, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: -14 }}
          transition={{
            opacity: { duration: 0.8, delay: 0.3 + i * 0.1, ease: EASE },

            y: { duration: t.dur, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut', delay: i * 0.6 },
          }}
          className={`absolute ${t.cls} opacity-45`}
        >
          <div className="aspect-4/5 overflow-hidden rounded-2xl border border-line shadow-soft">
            <ImageWithFallback src={t.img} alt="" className="h-full w-full object-cover" />
          </div>
        </motion.div>
      ))}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1, y: -10 }}
        transition={{
          opacity: { duration: 0.8, delay: 0.9, ease: EASE },
          y: { duration: 5.5, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut', delay: 1.2 },
        }}
        className="absolute left-[13%] top-[32%] rounded-full border border-line bg-white px-3 py-1.5 text-xs font-bold text-ink shadow-soft"
      >
        ❤ 12.4k
      </motion.div>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1, y: -11 }}
        transition={{
          opacity: { duration: 0.8, delay: 1.1, ease: EASE },
          y: { duration: 6.5, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut', delay: 0.4 },
        }}
        className="absolute right-[12%] top-[36%] rounded-full border border-line bg-white px-3 py-1.5 text-xs font-bold text-brand-700 shadow-soft"
      >
        Reach 128K
      </motion.div>
    </div>
  )
}
