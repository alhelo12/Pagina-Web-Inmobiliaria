import { motion } from 'framer-motion'
import { BedDouble, Bath, MapPin } from 'lucide-react'

export default function PropertyCard({ property, index }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 26 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.4 }}
      transition={{ duration: 0.55, delay: index * 0.1 }}
      whileHover={{ y: -8 }}
      className="group overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-soft"
    >
      <div className="relative h-52 overflow-hidden">
        <img
          src={property.image}
          alt={property.name}
          className="h-full w-full object-cover transition duration-500 group-hover:scale-110"
        />
      </div>

      <div className="space-y-3 p-5">
        <p className="flex items-center gap-1 text-xs text-slate-500">
          <MapPin className="h-3.5 w-3.5" />
          {property.location}
        </p>

        <h3 className="text-2xl font-bold tracking-tight text-slate-900">{property.name}</h3>

        <div className="flex items-center gap-4 text-sm text-slate-500">
          <span className="flex items-center gap-1"><BedDouble className="h-4 w-4" /> {property.beds}</span>
          <span className="flex items-center gap-1"><Bath className="h-4 w-4" /> {property.baths}</span>
        </div>

        <p className="pt-1 text-2xl font-extrabold text-ink">{property.price}</p>
      </div>
    </motion.article>
  )
}
