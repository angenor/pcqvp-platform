export interface ImageVariants {
  low: Blob
  medium: Blob
  original: Blob
  dimensions: {
    low: { width: number; height: number }
    medium: { width: number; height: number }
    original: { width: number; height: number }
  }
}
