const MINOR_WORDS = new Set([
  'en', 'de', 'del', 'la', 'las', 'lo', 'los', 'el',
  'un', 'una', 'y', 'e', 'o', 'a', 'con', 'sin',
  'por', 'para', 'al', 'su', 'que'
])

const isUppercaseWord = (word) => word.length > 1 && word === word.toUpperCase()

export function formatPropertyTitle(title) {
  const raw = (title ?? '').trim()
  if (!raw) return ''

  const words = raw.split(/\s+/)
  return words.map((word, i) => {
    if (isUppercaseWord(word)) return word
    const lower = word.toLowerCase()
    if (i === 0) return lower.charAt(0).toUpperCase() + lower.slice(1)
    if (MINOR_WORDS.has(lower)) return lower
    return lower.charAt(0).toUpperCase() + lower.slice(1)
  }).join(' ')
}
