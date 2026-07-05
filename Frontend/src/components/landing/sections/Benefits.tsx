import type { ReactNode } from 'react'
import { motion } from 'motion/react'
import { Target, Users, TrendingUp, Wrench, Zap, Check, type LucideIcon } from 'lucide-react'
import { Container } from '../../ui/Container'
import { SectionHeading } from '../SectionHeading'
import { EASE } from '../../../lib/motion'
import { cn, formatCompact } from '../../../lib/cn'
import { STORY_NICHES, TRENDING, mockSimOutput, mockSuggestions } from '../../../config/site'

function Cell({ className, delay = 0, children }: { className?: string; delay?: number; children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay, ease: EASE }}
      className={cn('flex flex-col bg-canvas p-5 sm:p-7', className)}
    >
      {children}
    </motion.div>
  )
}

function Head({ icon: Icon, title, body }: { icon: LucideIcon; title: string; body: string }) {
  return (
    <>
      <div className="grid h-11 w-11 place-items-center rounded-2xl bg-brand-50 text-brand-600">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mt-4 text-xl font-extrabold tracking-tight text-ink">{title}</h3>
      <p className="mt-2 text-[14px] leading-relaxed text-muted">{body}</p>
    </>
  )
}

function ReachRangeMini() {
  const o = mockSimOutput
  const markerPct = Math.round(((o.expected_reach - o.reach_p10) / (o.reach_p90 - o.reach_p10)) * 100)
  return (
    <div className="mt-5 border border-line p-4 sm:mt-auto">
      <div className="flex items-end justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wide text-muted">Expected reach</p>
          <p className="text-3xl font-black tracking-tight text-ink">{formatCompact(o.expected_reach)}</p>
        </div>
        <span className="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-bold text-brand-700">{Math.round(o.viral_probability * 100)}% viral odds</span>
      </div>
      <div className="relative mt-4 h-2.5 w-full rounded-full bg-brand-100">
        <motion.div className="absolute inset-y-0 left-0 rounded-full bg-brand-500" initial={{ width: 0 }} whileInView={{ width: '100%' }} viewport={{ once: true, margin: '-60px' }} transition={{ duration: 1, ease: EASE }} />
        <motion.span className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-brand-700 shadow" style={{ left: `${markerPct}%` }} initial={{ opacity: 0, scale: 0.5 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: 0.6, ease: EASE }} />
      </div>
      <div className="mt-1.5 flex justify-between text-[10px] font-medium text-muted">
        <span>{formatCompact(o.reach_p10)} floor</span>
        <span>{formatCompact(o.reach_p90)} ceiling</span>
      </div>
    </div>
  )
}

function AudienceSpread() {
  return (
    <div className="mt-auto space-y-2 pt-2">
      {STORY_NICHES.map((n) => {
        const strong = n.aff >= 0.7
        const initials = n.name.split(' ').map((w) => w[0]).join('').slice(0, 2)
        return (
          <div key={n.name} className="flex items-center gap-2.5">
            <span className={cn('grid h-6 w-6 flex-none place-items-center rounded-lg text-[10px] font-bold', strong ? 'bg-brand-100 text-brand-700' : 'bg-neutral-100 text-muted')}>{initials}</span>
            <span className="flex-1 truncate text-[13px] font-medium text-ink">{n.name}</span>
            {strong && <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[10px] font-bold text-brand-700">strong</span>}
          </div>
        )
      })}
    </div>
  )
}

function TrendSpark() {
  return (
    <div className="mt-auto space-y-2 pt-4">
      {TRENDING.slice(0, 4).map((t) => (
        <div key={t.label} className="flex items-center gap-2.5">
          <span className={cn('grid h-4 w-4 flex-none place-items-center rounded-full', t.match ? 'bg-brand-600 text-white' : 'bg-neutral-100 text-muted')}>
            {t.match ? <Check className="h-2.5 w-2.5" /> : <TrendingUp className="h-2.5 w-2.5" />}
          </span>
          <span className="flex-1 truncate text-[13px] font-medium text-ink">{t.label}</span>
        </div>
      ))}
    </div>
  )
}

function TopEditMini() {
  const s = mockSuggestions[0]
  return (
    <div className="mt-5 flex items-start gap-3 border border-line p-3.5 sm:mt-auto">
      <span className="grid h-8 w-8 flex-none place-items-center rounded-xl bg-brand-600 text-white">
        <Zap className="h-4 w-4" />
      </span>
      <div className="min-w-0">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-brand-700">Top edit · {s.impact} impact</p>
        <p className="mt-0.5 text-[13px] font-semibold leading-snug text-ink">{s.title}</p>
      </div>
    </div>
  )
}

export function Benefits() {
  return (
    <section className="bg-canvas py-14 sm:py-24">
      <Container>
        <SectionHeading
          eyebrow="Why Reech"
          title="Stop guessing. Start forecasting."
          subtitle="Most tools hand you a vanity score. Reech shows you what the feed will actually do with your post — as numbers you can act on."
        />
        <div className="mt-10 grid gap-px border border-line bg-line sm:mt-16 md:grid-cols-3 md:grid-rows-2">
          <Cell className="md:col-span-2" delay={0}>
            <Head icon={Target} title="Post with conviction, not hope" body="Every post gets a real reach range and viral probability from thousands of simulations — so you commit to the version most likely to land, not a hunch." />
            <ReachRangeMini />
          </Cell>

          <Cell className="md:row-span-2" delay={0.06}>
            <Head icon={Users} title="Know your audience before they do" body="50,000 synthetic viewers judge your content independently — see exactly which audiences light up and which scroll past." />
            <AudienceSpread />
          </Cell>

          <Cell delay={0.12}>
            <Head icon={TrendingUp} title="Ride trends while they’re hot" body="Live topic and entity signals feed every run — timing genuinely moves your forecast." />
            <TrendSpark />
          </Cell>

          <Cell delay={0.18}>
            <Head icon={Wrench} title="Fix the weak spot first" body="Every forecast comes with the highest-impact edit, tied to the lever that changed the outcome." />
            <TopEditMini />
          </Cell>
        </div>
      </Container>
    </section>
  )
}
