import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Button } from '../ui/Button'
import { Container } from '../ui/Container'
import { BRAND } from '../../config/site'

export function Logo({ withName = true }: { withName?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 shadow-[0_6px_16px_-6px_rgba(5,150,105,0.7)]">
        <svg viewBox="0 0 32 32" className="h-5.5 w-5.5" fill="none">
          <circle cx="7" cy="22.5" r="2.6" fill="#fff" />
          <path
            d="M7 22.5 C11.5 22.5 12.5 9 17 9 C21.5 9 21.5 16.5 26.5 16.5"
            stroke="#fff"
            strokeWidth="2.7"
            strokeLinecap="round"
          />
          <path
            d="M10.5 26.5 C14 26.5 14.8 16 18.4 16 C21.4 16 21.4 21 24.8 21"
            stroke="#fff"
            strokeOpacity="0.42"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
      </span>
      {withName && <span className="text-lg font-bold tracking-tight text-ink">{BRAND.name}</span>}
    </Link>
  )
}

export function Navbar() {
  const navigate = useNavigate()
  return (
    <header className="sticky top-0 z-50 border-b border-line/70 bg-canvas/80 backdrop-blur-xl">
      <Container className="flex h-16 items-center justify-between">
        <Logo />
        <nav className="hidden items-center gap-8 text-sm font-medium text-muted md:flex">
          <a href="#benefits" className="transition-colors hover:text-ink">Why Reech</a>
          <a href="#sample" className="transition-colors hover:text-ink">The report</a>
          <a href="#reviews" className="transition-colors hover:text-ink">Reviews</a>
          <a href="#faq" className="transition-colors hover:text-ink">FAQ</a>
        </nav>
        <Button size="sm" onClick={() => navigate('/get-started')}>
          Get started <ArrowRight className="h-3.5 w-3.5" />
        </Button>
      </Container>
    </header>
  )
}
