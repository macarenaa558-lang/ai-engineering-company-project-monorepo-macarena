import type { ImgHTMLAttributes } from 'react'

type OptimizedImageProps = ImgHTMLAttributes<HTMLImageElement> & {
  width: number
  height: number
}

export function OptimizedImage({
  loading = 'lazy',
  decoding = 'async',
  ...props
}: OptimizedImageProps) {
  return (
    <img
      loading={loading}
      decoding={decoding}
      {...props}
    />
  )
}
