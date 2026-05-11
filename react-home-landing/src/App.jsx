import { motion } from 'framer-motion'
import Navbar from './components/Navbar'
import SearchBar from './components/SearchBar'
import PropertyCard from './components/PropertyCard'

const properties = [
  {
    name: 'Ocean Breeze Villa',
    location: '123 MainStreet, Anaheim, CA 92845',
    beds: 4,
    baths: 2,
    price: '€ 910.000,00',
    image: 'https://images.unsplash.com/photo-1600607687644-c7171b42498f?auto=format&fit=crop&w=1200&q=80'
  },
  {
    name: 'Jakson House',
    location: '459 Oak Avenue, New York, NY 10001',
    beds: 3,
    baths: 2,
    price: '€ 750.000,00',
    image: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80'
  },
  {
    name: 'Lakeside Cottage',
    location: '780 Main Lane, Los Angeles, 90001',
    beds: 3,
    baths: 1,
    price: '€ 540.000,00',
    image: 'https://images.unsplash.com/photo-1600566753151-384129cf4e3e?auto=format&fit=crop&w=1200&q=80'
  }
]

export default function App() {
  return (
    <main className="min-h-screen bg-[#F3F5F7] px-4 py-8 md:px-8">
      <section className="mx-auto max-w-6xl">
        <div className="relative overflow-hidden rounded-[2.1rem] shadow-premium">
          <Navbar />

          <div className="absolute inset-0 bg-gradient-to-br from-[#072647]/90 via-[#0A3B68]/70 to-[#0B2F56]/55" />

          <img
            src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=2100&q=80"
            alt="Luxury modern home"
            className="h-[590px] w-full object-cover"
          />

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="absolute left-0 top-0 z-10 flex h-full w-full max-w-2xl items-center px-6 md:px-14"
          >
            <div className="rounded-3xl border border-white/10 bg-[#051D39]/45 p-8 backdrop-blur-md md:p-10">
              <h1 className="text-4xl font-extrabold leading-tight text-white md:text-6xl">
                Finding Your New
                <br />
                Home Is Simple
              </h1>
              <p className="mt-5 max-w-lg text-sm leading-relaxed text-slate-200 md:text-base">
                RentHomes.com is your go to destination for finding the perfect rental home to suit your needs.
                With thousands of property listings across the United States, and Europe.
              </p>

              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="mt-8 inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/20 px-6 py-3 text-sm font-semibold text-white backdrop-blur-xl"
              >
                Search
                <span className="inline-block h-2 w-16 rounded-full bg-white/40" />
              </motion.button>
            </div>
          </motion.div>
        </div>

        <SearchBar />

        <section className="pb-12 pt-20">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.55 }}
            className="mx-auto max-w-3xl text-center"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Featured Collection</p>
            <h2 className="mt-4 text-4xl font-extrabold tracking-tight text-slate-900 md:text-5xl">Most Viewed</h2>
            <p className="mt-3 text-sm text-slate-500 md:text-base">
              Discover a range of vacation homes worldwide. Book securely and get support for a stress-free stay.
            </p>
          </motion.div>

          <div className="mt-12 grid gap-7 md:grid-cols-2 lg:grid-cols-3">
            {properties.map((property, index) => (
              <PropertyCard key={property.name} property={property} index={index} />
            ))}
          </div>

          <div className="mt-10 flex justify-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
            <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
            <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
          </div>
        </section>
      </section>
    </main>
  )
}
