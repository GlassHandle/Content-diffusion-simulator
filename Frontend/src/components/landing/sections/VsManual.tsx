import { motion } from 'motion/react'
import { Check, X, ArrowRight, Sparkles, TrendingUp, Users, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../ui/Container'
import { Button } from '../../ui/Button'
import { ImageWithFallback } from '../../ui/ImageWithFallback'
import { formatCompact } from '../../../lib/cn'
import { EASE } from '../../../lib/motion'
import { POST_IMAGE, CONTENT_FEED, STORY_NICHES, TRENDING, mockSimOutput } from '../../../config/site'

const MANUAL_POINTS = [
  'Hand-typed tags, one post at a time',
  'No real audience — just a hunch',
  'Static keywords, blind to live trends',
  'Skewed by your own taste',
  'Post and hope. No reach in sight.',
]

const GUESS_TAGS = ['#fashion', '#ootd', '#style', '#vibes', '#aesthetic', '#trendy']

export function VsManual() {
  const navigate = useNavigate()
  const o = mockSimOutput

  return (
    <section className="bg-white py-14 sm:py-24">
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.7, ease: EASE }}
          className="max-w-3xl"
        >
          <p className="inline-flex items-center gap-1.5 rounded-full border border-line bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-brand-700 backdrop-blur">
            <Sparkles className="h-3.5 w-3.5" /> The difference
          </p>
          <h2 className="mt-5 font-serif text-4xl font-black leading-[1.02] tracking-tight text-ink sm:text-5xl">
            Guesswork <span className="text-muted/70">vs</span>{' '}
            <span className="text-brand-700">Reech</span>.
          </h2>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted">
            Tagging by hand asks you to guess your audience. Reech understands the
            post, plays it to a calibrated crowd, and hands back a real forecast —
            before you ever hit publish.
          </p>
        </motion.div>

        <div className="mt-14 grid items-stretch gap-6 lg:grid-cols-2">
          <ManualPanel points={MANUAL_POINTS} tags={GUESS_TAGS} />
          <ReechPanel reach={o.expected_reach} p10={o.reach_p10} p90={o.reach_p90} viral={o.viral_probability} />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.6, delay: 0.1, ease: EASE }}
          className="mt-14 flex flex-col items-center gap-4 text-center"
        >
          <p className="text-base font-medium text-muted">
            Stop guessing your tags. See your reach before you post.
          </p>
          <Button size="lg" onClick={() => navigate('/get-started')}>
            Forecast my next post <ArrowRight className="h-4 w-4" />
          </Button>
        </motion.div>
      </Container>
    </section>
  )
}

function ManualPanel({ points, tags }: { points: string[]; tags: string[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.6, ease: EASE }}
      className="flex flex-col overflow-hidden border border-line bg-white/60 backdrop-blur"
    >
      <div className="relative">
        <div className="grid grid-cols-3 gap-0.5 opacity-90">
          {CONTENT_FEED.slice(0, 3).map((src) => (
            <div key={src} className="aspect-square overflow-hidden">
              <ImageWithFallback src={src} alt="" className="h-full w-full object-cover grayscale" />
            </div>
          ))}
        </div>
        <div className="absolute inset-0 flex flex-wrap content-center items-center justify-center gap-1.5 bg-slate-900/45 p-4">
          {tags.map((t) => (
            <span
              key={t}
              className="rounded-full border border-white/30 bg-white/15 px-2.5 py-1 text-[11px] font-semibold text-white/85 backdrop-blur-sm"
            >
              {t}
            </span>
          ))}
        </div>
      </div>

      <div className="flex flex-1 flex-col p-8 sm:p-9">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-slate-100 text-slate-500">
            <X className="h-5 w-5" strokeWidth={2.5} />
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">The old way</p>
            <h3 className="text-2xl font-extrabold tracking-tight text-ink">Manual tagging</h3>
          </div>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-muted">
          Slow, subjective, and blind to how the feed actually behaves.
        </p>

        <ul className="mt-7 space-y-3.5 border-t border-line pt-7">
          {points.map((p, i) => (
            <motion.li
              key={p}
              initial={{ opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: 0.05 + i * 0.06, ease: EASE }}
              className="flex items-start gap-3"
            >
              <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-slate-100 text-slate-400">
                <X className="h-3 w-3" strokeWidth={3} />
              </span>
              <span className="text-[15px] leading-relaxed text-muted">{p}</span>
            </motion.li>
          ))}
        </ul>

        <div className="mt-auto pt-8">
          <div className="border border-dashed border-line bg-slate-50/70 px-5 py-4 text-center">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted">Expected reach</p>
            <p className="mt-1 text-3xl font-black tracking-tight text-slate-300">???</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function ReechPanel({reach,p10,p90,viral}: {
  reach: number
  p10: number
  p90: number
  viral: number
}) {
  const topNiche = STORY_NICHES[0]
  const matches = TRENDING.filter((t) => t.match).slice(0, 3)

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.6, delay: 0.1, ease: EASE }}
      className="relative flex flex-col overflow-hidden border border-brand-200 bg-white"
    >
      <div className="relative">
        <div className="aspect-16/10 w-full overflow-hidden sm:aspect-video">
          <ImageWithFallback src={POST_IMAGE} alt="Your post, understood by Reech" className="h-full w-full object-cover" />
        </div>
        <div className="absolute inset-0 bg-linear-to-t from-black/65 via-black/10 to-transparent" />

        <span className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-[11px] font-bold text-ink shadow-soft">
          your post
        </span>

        <div className="absolute right-4 top-4 flex items-center gap-2 rounded-full bg-white/90 py-1 pl-1 pr-3 shadow-soft backdrop-blur">
          <span className="h-6 w-6 overflow-hidden rounded-full">
            <ImageWithFallback src={topNiche.img} alt={topNiche.name} className="h-full w-full object-cover" />
          </span>
          <span className="text-[11px] font-bold text-ink">
            {topNiche.name} · {Math.round(topNiche.aff * 100)}%
          </span>
        </div>

        <div className="absolute inset-x-4 bottom-4 flex items-center gap-2">
          {matches.map((t) => (
            <div
              key={t.label}
              className="relative h-11 w-11 overflow-hidden rounded-xl border-2 border-white/80 shadow-lift"
            >
              <ImageWithFallback src={t.img} alt={t.label} className="h-full w-full object-cover" />
              <span className="absolute inset-0 grid place-items-center bg-brand-600/45">
                <Check className="h-4 w-4 text-white" strokeWidth={3} />
              </span>
            </div>
          ))}
          <span className="ml-1 text-xs font-bold text-white/95 [text-shadow:0_1px_6px_rgba(0,0,0,0.5)]">
            {matches.length} live trends matched
          </span>
        </div>
      </div>

      <div className="relative flex flex-1 flex-col p-8 sm:p-9">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-brand-600 text-white shadow-[0_10px_30px_-10px_rgba(5,150,105,0.6)]">
            <Check className="h-5 w-5" strokeWidth={2.5} />
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">The Reech way</p>
            <h3 className="text-2xl font-extrabold tracking-tight text-ink">Reech simulation</h3>
          </div>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-muted">
          Understanding, audience, and trends — modeled into one honest forecast.
        </p>

        <ul className="mt-7 space-y-3.5 border-t border-brand-100 pt-7">
          {[
            { icon: Zap, text: 'AI reads your content and understands it instantly' },
            { icon: Users, text: 'Judged by 50,000 synthetic viewer personas' },
            { icon: TrendingUp, text: 'Live topic and entity trends feed every run' },
            { icon: Sparkles, text: 'A calibrated crowd — not a single point of view' },
          ].map((item, i) => (
            <motion.li
              key={item.text}
              initial={{ opacity: 0, x: 8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: 0.1 + i * 0.06, ease: EASE }}
              className="flex items-start gap-3"
            >
              <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-brand-100 text-brand-700">
                <Check className="h-3 w-3" strokeWidth={3} />
              </span>
              <span className="text-[15px] font-medium leading-relaxed text-ink">{item.text}</span>
            </motion.li>
          ))}
        </ul>

        <div className="mt-auto pt-8">
          <div className="relative overflow-hidden border border-brand-200 bg-brand-50/60 px-5 py-4">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-brand-700">Forecast reach</p>
                <p className="mt-1 text-4xl font-black tracking-tight text-ink">
                  {formatCompact(reach)}
                </p>
                <p className="mt-1 text-xs text-muted">
                  {formatCompact(p10)}–{formatCompact(p90)} range
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs font-semibold uppercase tracking-wider text-brand-700">Viral odds</p>
                <p className="mt-1 text-4xl font-black tracking-tight text-ink">
                  {Math.round(viral * 100)}%
                </p>
                <p className="mt-1 text-xs text-muted">10k Monte Carlo runs</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
