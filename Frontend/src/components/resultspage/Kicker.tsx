import { type ReactNode } from "react"

export default function Kicker({ children }: { children: ReactNode }) {
  return (
    <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-brand-700">{children}</p>
  )
}