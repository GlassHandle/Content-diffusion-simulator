import { useState } from 'react'
import { cn } from '../../lib/cn'

export function ImageWithFallback({src,alt,className,}: {
  src: string
  alt: string
  className?: string
}) {
  const [failed, setFailed] = useState(false)

  if (failed) {
    return (
      <div
        role="img"
        aria-label={alt}
        className={cn('bg-linear-to-br from-brand-100 via-teal-50 to-sky-100', className)}
      />
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={className}
    />
  )
}
