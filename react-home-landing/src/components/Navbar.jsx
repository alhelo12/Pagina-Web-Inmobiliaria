import { motion } from 'framer-motion'
import { Home } from 'lucide-react'

const links = ['Home', 'Contacts', 'Support', 'Location', 'About us']

export default function Navbar() {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: 'easeOut' }}
      className="absolute inset-x-0 top-0 z-20 mx-auto flex w-[92%] max-w-6xl items-center justify-between px-4 py-6 text-white md:px-8"
    >
      <div className="flex items-center gap-2 text-base font-bold tracking-tight">
        <Home className="h-5 w-5" />
        <span>Rent H&U</span>
      </div>

      <ul className="hidden items-center gap-10 text-sm font-medium text-white/90 lg:flex">
        {links.map((link) => (
          <li key={link} className="transition hover:text-white">
            <a href="#">{link}</a>
          </li>
        ))}
      </ul>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.97 }}
        className="rounded-full border border-white/20 bg-white/20 px-6 py-2 text-sm font-semibold backdrop-blur-xl transition hover:bg-white/30"
      >
        Try now
      </motion.button>
    </motion.nav>
  )
}
