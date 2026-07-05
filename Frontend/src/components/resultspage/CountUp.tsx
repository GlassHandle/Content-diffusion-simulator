import { useEffect, useState } from 'react'
import { motion, animate } from 'motion/react'
import { formatCompact } from '../../lib/cn'

const STAIR_SIZES = [
  'text-5xl sm:text-6xl',
  'text-6xl sm:text-7xl',
  'text-7xl sm:text-8xl',
  'text-8xl sm:text-9xl',
]

export default function CountUp({ to, duration = 1.4 }: { to: number; duration?: number }) {
  const [n, setN] = useState(0)
  const [go, setGo] = useState(false)
  useEffect(() => {
    if (!go) return
    const controls = animate(0, to, { duration, ease: 'circOut', onUpdate: (v) => setN(v) })
    return () => controls.stop()
  }, [go, to, duration])

  let di = 0
  const chars = [...formatCompact(n)].map((ch, i) => {
    const isDigit = /\d/.test(ch)
    const size = STAIR_SIZES[Math.min(isDigit ? di : Math.max(di - 1, 0), STAIR_SIZES.length - 1)]
    if (isDigit) di++
    return (
      <span key={i} className={size}>
        {ch}
      </span>
    )
  })

  return (
    <motion.span
      onViewportEnter={() => setGo(true)}
      viewport={{ once: true }}
      className="inline-flex items-baseline leading-none tabular-nums"
    >
      {chars}
    </motion.span>
  )
}