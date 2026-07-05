import { GLOSSARY } from "../../config/site"
import Kicker from "./Kicker"
import { motion } from "motion/react"
import { EASE } from '../../lib/motion'

export default function MeaningSpread() {
  return (
    <div className="pt-8">
      {GLOSSARY.map((g, gi) => (
        <div key={g.group} className={gi === 0 ? '' : 'mt-10 border-t border-ink/15 pt-8'}>
          <div className="md:flex md:items-baseline md:gap-10">
            <div className="md:w-64 md:flex-none">
              <Kicker>{g.group}</Kicker>
              <p className="mt-2 text-[14px] leading-relaxed text-muted">{g.blurb}</p>
            </div>
            <div className="mt-6 flex-1 gap-10 md:mt-0 md:columns-2 xl:columns-3">
              {g.terms.map((t, i) => (
                <motion.div
                  key={t.term}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-40px' }}
                  transition={{ duration: 0.4, delay: i * 0.04, ease: EASE }}
                  className="mb-6 break-inside-avoid"
                >
                  <p className="border-b border-dotted border-ink/20 pb-1 font-serif text-[17px] font-black text-ink">
                    {t.term}
                  </p>
                  <p className="mt-1.5 text-[14px] leading-relaxed text-muted">{t.def}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}