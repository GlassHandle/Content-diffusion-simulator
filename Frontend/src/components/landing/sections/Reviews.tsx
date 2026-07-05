import { motion } from 'motion/react'
import { Star } from 'lucide-react'
import { Container } from '../../ui/Container'
import { SectionHeading } from '../SectionHeading'
import { EASE } from '../../../lib/motion'

const QUOTES = [
  { quote: 'I stopped posting on vibes. Reech showed me the hook that would land — and it did, 3× my usual reach.', name: '@laine.loops', role: 'Travel creator', init: 'LL' },
  { quote: 'It flagged that my “sure thing” would flop before I wasted a whole shoot on it. Saved me a weekend.', name: '@byte.betty', role: 'Tech reviewer', init: 'BB' },
  { quote: 'Caught a trend two days before it peaked. That one post did more than my last month combined.', name: '@sol.and.co', role: 'Fashion & lifestyle', init: 'SC' },
]
const STATS = [
  { v: '50K', l: 'AI viewers' },
  { v: '10K', l: 'simulations' },
  { v: '24', l: 'topics' },
  { v: '8', l: 'dimensions' },
]

export function Reviews() {
  return (
    <section className="bg-canvas py-14 sm:py-24">
      <Container>
        <SectionHeading eyebrow="Loved by creators" title="Creators who stopped guessing" />
        <div className="mt-10 grid gap-px border border-line bg-line sm:mt-16 md:grid-cols-3">
          {QUOTES.map((q, i) => (
            <motion.div
              key={q.name}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.08, ease: EASE }}
              className="flex flex-col bg-canvas p-6 sm:p-7"
            >
              <div className="flex gap-0.5 text-brand-500">
                {Array.from({ length: 5 }).map((_, j) => <Star key={j} className="h-4 w-4 fill-current" />)}
              </div>
              <p className="mt-4 flex-1 text-[15px] leading-relaxed text-ink">“{q.quote}”</p>
              <div className="mt-6 flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">{q.init}</span>
                <div>
                  <p className="text-sm font-bold text-ink">{q.name}</p>
                  <p className="text-xs text-muted">{q.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
        <div className="mt-10 grid grid-cols-2 gap-px border border-line bg-line sm:mt-14 sm:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.l} className="bg-canvas py-6 text-center">
              <p className="text-3xl font-black tracking-tight text-ink sm:text-4xl">{s.v}</p>
              <p className="mt-1 text-xs text-muted">{s.l}</p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}
