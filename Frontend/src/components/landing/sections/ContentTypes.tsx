import { motion } from 'motion/react'
import { Video, Image as ImageIcon, FileText, Check, type LucideIcon } from 'lucide-react'
import { Container } from '../../ui/Container'
import { SectionHeading } from '../SectionHeading'
import { EASE } from '../../../lib/motion'

const TYPES: { icon: LucideIcon; name: string; kicker: string; extracts: string[] }[] = [
  { icon: Video, name: 'Video', kicker: 'Reels · Shorts · TikToks', extracts: ['Frame-level scenes', 'Cut & pacing rhythm', 'Full transcript', 'Audio & music energy'] },
  { icon: ImageIcon, name: 'Image', kicker: 'Posts · carousels', extracts: ['Scene & setting', 'Objects & subjects', 'Composition & framing', 'Color & mood'] },
  { icon: FileText, name: 'Text', kicker: 'Captions · threads', extracts: ['Topic & theme', 'Tone & sentiment', 'Named entities', 'Intent & call-to-action'] },
]

export function ContentTypes() {
  return (
    <section className="bg-white py-14 sm:py-24">
      <Container>
        <SectionHeading
          eyebrow="Works with your content"
          title="Video, image, or text — read on its own terms"
          subtitle="Each format carries signal differently, so Reech understands each one the way the feed does."
        />
        <div className="mt-10 grid gap-px border border-line bg-line sm:mt-16 md:grid-cols-3">
          {TYPES.map((t, i) => {
            const Icon = t.icon
            return (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.5, delay: i * 0.08, ease: EASE }}
                className="bg-white p-5 sm:p-7"
              >
                <div className="flex items-center gap-3">
                  <div className="grid h-11 w-11 place-items-center rounded-2xl bg-brand-50 text-brand-600">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-lg font-extrabold tracking-tight text-ink">{t.name}</p>
                    <p className="text-xs text-muted">{t.kicker}</p>
                  </div>
                </div>
                <p className="mt-6 text-[11px] font-semibold uppercase tracking-wide text-muted">What the AI extracts</p>
                <ul className="mt-2.5 space-y-2.5">
                  {t.extracts.map((e) => (
                    <li key={e} className="flex items-center gap-2 text-sm text-ink/80">
                      <Check className="h-4 w-4 flex-none text-brand-600" /> {e}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )
          })}
        </div>
      </Container>
    </section>
  )
}
