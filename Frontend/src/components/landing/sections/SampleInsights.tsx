import { motion } from 'motion/react'
import { Sparkles, TrendingUp, ArrowRight, Check, Flame, type LucideIcon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../ui/Container'
import { Button } from '../../ui/Button'
import { SectionHeading } from '../SectionHeading'
import { EASE } from '../../../lib/motion'
import { formatCompact } from '../../../lib/cn'
import { mockSimOutput, mockSuggestions } from '../../../config/site'

const o = mockSimOutput
const topEdit = mockSuggestions[0]
const viralPct = Math.round(o.viral_probability * 100)

const points: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: Sparkles,
    title: 'Not a score — a full read',
    body: 'Reech surfaces the metadata, the audience most likely to spread it, and the live trend it rides — every signal behind the number, made explicit.',
  },
  {
    icon: TrendingUp,
    title: 'A forecast you can act on',
    body: 'Expected reach, real viral odds, and the single highest-impact edit — a ready-to-use brief before you ever hit publish.',
  },
]

const TICKER = [
  `Reach ${formatCompact(o.expected_reach)}`,
  `Viral ${viralPct}%`,
  `Confidence ${Math.round(o.confidence * 100)}%`,
  'Share 7.8',
  'Humor 8.4',
]

const STAIR_MINI = [
  'text-xl sm:text-2xl',
  'text-2xl sm:text-3xl',
  'text-3xl sm:text-4xl',
  'text-3xl sm:text-4xl',
]
function StairMini({ value }: { value: number }) {
  let di = 0
  return (
    <span className="inline-flex items-baseline leading-none tabular-nums">
      {[...formatCompact(value)].map((ch, i) => {
        const isDigit = /\d/.test(ch)
        const size = STAIR_MINI[Math.min(isDigit ? di : Math.max(di - 1, 0), STAIR_MINI.length - 1)]
        if (isDigit) di++
        return (
          <span key={i} className={size}>
            {ch}
          </span>
        )
      })}
    </span>
  )
}

function MiniRow({ label, value, strong }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="flex items-baseline gap-2 border-b border-dotted border-ink/20 pb-1">
      <span className="text-[11px] text-ink/80">{label}</span>
      <span className="flex-1" />
      <span className={`text-[11px] font-bold tabular-nums ${strong ? 'text-brand-700' : 'text-ink'}`}>{value}</span>
    </div>
  )
}

export function SampleInsights() {
  const navigate = useNavigate()

  return (
    <section className="bg-canvas py-14 sm:py-24">
      <Container>
        <div className="grid items-center gap-14 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="min-w-0">
            <SectionHeading
              center={false}
              eyebrow="A real forecast"
              title="This is what Reech hands you back"
              subtitle="One post in — your own front page out. This is the actual report, not a mock-up."
            />

            <div className="mt-10 space-y-7">
              {points.map((pt, i) => {
                const Icon = pt.icon
                return (
                  <motion.div
                    key={pt.title}
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-60px' }}
                    transition={{ duration: 0.5, delay: i * 0.1, ease: EASE }}
                    className="flex gap-4"
                  >
                    <div className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-brand-600 text-white shadow-glow">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold tracking-tight text-ink">{pt.title}</h3>
                      <p className="mt-1.5 text-[15px] leading-relaxed text-muted">{pt.body}</p>
                    </div>
                  </motion.div>
                )
              })}
            </div>

            <div className="mt-10">
              <Button size="lg" onClick={() => navigate('/get-started')} className="shadow-glow">
                Get my report
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 34 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.7, ease: EASE }}
            className="relative min-w-0"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: 0.5, ease: EASE }}
              className="absolute -right-2 -top-4 z-20 flex items-center gap-2 rounded-full bg-brand-600 px-4 py-2 text-white shadow-glow sm:-right-4"
            >
              <span className="grid h-6 w-6 place-items-center rounded-full bg-white/20">
                <Check className="h-3.5 w-3.5" />
              </span>
              <span className="text-sm font-bold tracking-tight">Forecast ready</span>
            </motion.div>

            <div className="overflow-hidden border border-line bg-surface">
              <div className="flex items-center gap-2 border-b border-line bg-canvas/80 px-5 py-3">
                <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
                <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
                <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
                <span className="ml-3 text-xs font-semibold uppercase tracking-wider text-muted">
                  Reech · your results
                </span>
              </div>

              <div className="px-4 pb-5 pt-4 sm:px-7 sm:pb-6">
                <div className="border-t-2 border-ink pt-1.5">
                  <div className="flex items-baseline justify-center gap-2 sm:justify-between">
                    <span className="hidden text-[9px] font-semibold uppercase tracking-[0.18em] text-muted sm:block">Vol. 001</span>
                    <span className="font-serif text-base font-black uppercase tracking-[0.08em] text-ink sm:text-lg">
                      The Reech Report
                    </span>
                    <span className="hidden text-[9px] font-semibold uppercase tracking-[0.18em] text-muted sm:block">
                      Forecast edition
                    </span>
                  </div>
                </div>

                <div className="mt-2 overflow-hidden border-y border-ink/15 py-1.5 whitespace-nowrap">
                  {TICKER.map((t) => (
                    <span key={t} className="mr-4 inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-[0.12em] text-ink/70">
                      <span className="text-brand-600">▲</span>
                      {t}
                    </span>
                  ))}
                </div>

                <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.2em] text-brand-700">
                  Today&rsquo;s verdict
                </p>
                <p className="mt-1 font-serif text-3xl font-black leading-tight tracking-tight text-ink">
                  This one&rsquo;s got legs.
                </p>
                <p className="mt-1 text-[10px] italic text-muted">
                  By the Reech simulation desk — 10,000 runs across 50,000 AI viewers
                </p>

                <div className="mt-4 flex items-end justify-between gap-4 border-b border-ink/15 pb-4">
                  <div>
                    <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-muted">Expected reach</p>
                    <p className="mt-1 font-serif font-black text-brand-700">
                      <StairMini value={o.expected_reach} />
                    </p>
                  </div>
                  <div className="flex items-center gap-2 sm:gap-2.5">
                    <span className="grid h-7 w-7 flex-none place-items-center rounded-full bg-brand-600 text-white sm:h-8 sm:w-8">
                      <Flame className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                    </span>
                    <div>
                      <p className="font-serif text-2xl font-black leading-none text-ink sm:text-3xl">{viralPct}%</p>
                      <p className="text-[9px] text-muted">chance of going viral</p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 space-y-2">
                  <MiniRow label="Quiet day" value={formatCompact(o.reach_p10)} />
                  <MiniRow label="Typical run" value={formatCompact(o.reach_p50)} />
                  <MiniRow label="If it pops" value={formatCompact(o.reach_p90)} strong />
                  <MiniRow label="Confidence" value={`${Math.round(o.confidence * 100)}%`} />
                </div>

                <div className="mt-4 border-t border-ink/15 pt-3">
                  <p className="font-serif text-[15px] font-black leading-snug text-ink">
                    <span className="text-brand-600">“</span>
                    {topEdit.title}
                    <span className="text-brand-600">”</span>
                  </p>
                  <span className="mt-2 inline-block rounded-full bg-brand-50 px-2.5 py-0.5 text-[10px] font-semibold text-brand-700">
                    {topEdit.impact} impact · do this first
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </Container>
    </section>
  )
}
