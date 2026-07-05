import { useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Button } from '../ui/Button'
import { Container } from '../ui/Container'
import { Logo } from './Navbar'
import { BRAND } from '../../config/site'

const COLUMNS = [
  { title: 'Product', links: ['How it works', 'Features', 'For creators', 'Pricing'] },
  { title: 'Company', links: ['About', 'Blog', 'Careers', 'Contact'] },
  { title: 'Resources', links: ['Docs', 'API', 'Changelog', 'Status'] },
]

export function Footer() {
  const navigate = useNavigate()
  return (
    <footer className="border-t border-line bg-white">
      <Container className="py-14">
        {/* final CTA */}
        <div className="mb-14 flex flex-col items-center justify-between gap-6 border border-line bg-canvas px-6 py-9 text-center sm:flex-row sm:text-left sm:px-10">
          <div>
            <h3 className="font-serif text-2xl font-black tracking-tight text-ink sm:text-3xl">Ready to see your reach?</h3>
            <p className="mt-1.5 text-muted">Run your first forecast free — no card, no setup, under a minute.</p>
          </div>
          <Button size="lg" onClick={() => navigate('/get-started')} className="flex-none">
            Analyze my content <ArrowRight className="h-4 w-4" />
          </Button>
        </div>

        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div className="max-w-xs">
            <Logo />
            <p className="mt-4 text-sm leading-relaxed text-muted">{BRAND.tagline}</p>
          </div>
          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h4 className="text-sm font-semibold text-ink">{col.title}</h4>
              <ul className="mt-3 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l}>
                    <a href="#" className="text-sm text-muted transition-colors hover:text-ink">
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-line pt-6 text-sm text-muted sm:flex-row">
          <p>© {new Date().getFullYear()} {BRAND.name}. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="transition-colors hover:text-ink">Privacy</a>
            <a href="#" className="transition-colors hover:text-ink">Terms</a>
          </div>
        </div>
      </Container>
    </footer>
  )
}
