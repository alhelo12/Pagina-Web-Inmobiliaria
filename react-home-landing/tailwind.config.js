/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        deepBlue: '#082B4F',
        deepBlue2: '#0E3B69',
        ink: '#0C223D'
      },
      boxShadow: {
        soft: '0 12px 30px rgba(16, 32, 56, 0.12)',
        premium: '0 28px 60px rgba(9, 24, 45, 0.35)'
      },
      borderRadius: {
        xl2: '1.25rem'
      }
    }
  },
  plugins: []
}
