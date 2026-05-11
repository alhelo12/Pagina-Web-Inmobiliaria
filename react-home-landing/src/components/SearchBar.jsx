import { motion } from 'framer-motion'
import { Search, ChevronDown } from 'lucide-react'

const fieldClass =
  'rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 outline-none transition focus:border-deepBlue2 focus:ring-4 focus:ring-blue-100'

export default function SearchBar() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 26 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.2 }}
      className="relative z-30 mx-auto -mt-12 w-[92%] max-w-4xl rounded-[2rem] border border-white/60 bg-white/95 p-3 shadow-soft backdrop-blur-xl"
    >
      <div className="grid gap-3 md:grid-cols-[1.2fr_1.2fr_1fr_auto]">
        <label className="flex flex-col rounded-2xl bg-slate-50 px-4 py-3">
          <span className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">City Street</span>
          <div className="flex items-center justify-between">
            <input className="w-full bg-transparent text-base font-semibold text-slate-800 outline-none" defaultValue="123Street" />
            <ChevronDown className="h-4 w-4 text-slate-400" />
          </div>
        </label>

        <label className="flex flex-col rounded-2xl bg-slate-50 px-4 py-3">
          <span className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Tipology of rent</span>
          <div className="flex items-center justify-between text-base font-semibold text-slate-800">
            <span>Villa</span>
            <ChevronDown className="h-4 w-4 text-slate-400" />
          </div>
        </label>

        <label className="flex flex-col rounded-2xl bg-slate-50 px-4 py-3">
          <span className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Price</span>
          <div className="flex items-center justify-between text-base font-semibold text-slate-800">
            <span>€ 950.000,00</span>
            <ChevronDown className="h-4 w-4 text-slate-400" />
          </div>
        </label>

        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          className="flex items-center justify-center gap-2 rounded-2xl bg-ink px-6 py-4 text-sm font-semibold text-white shadow-lg shadow-slate-300 transition hover:bg-deepBlue"
        >
          <Search className="h-4 w-4" />
          Search
        </motion.button>
      </div>
    </motion.div>
  )
}
