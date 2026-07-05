type ClassValue = string | number | null | false | undefined

/* classNames joiner */
export function cn(...classes: ClassValue[]): string {
  return classes.filter(Boolean).join(' ')
}

/* converts 128400 -> "128K", 1_240_000 -> "1.2M". */
export function formatCompact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n >= 10_000_000 ? 0 : 1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(n >= 10_000 ? 0 : 1)}K`
  return `${Math.round(n)}`
}
