export const FALLBACK_PROPERTY_IMAGE = 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80'

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

export const normalizeImageUrl = (url) => {
  if (!url) return FALLBACK_PROPERTY_IMAGE
  if (/^(https?:|blob:|data:)/.test(url)) return url
  if (url.startsWith('/media')) return `${API_BASE_URL}${url}`
  if (url.startsWith('media/')) return `${API_BASE_URL}/${url}`
  return url
}

export const getPropertyImage = (property) => {
  const images = property?.images ?? []
  const selected = images.find((img) => img.is_main)
    ?? images.find((img) => (img.image_type ?? 'general') === 'general')
    ?? images[0]

  return normalizeImageUrl(selected?.image_url ?? property?.main_image_url)
}