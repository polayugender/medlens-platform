/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        clinical: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#b9ddfd',
          300: '#7cc2fb',
          400: '#36a2f7',
          500: '#0c84e4',
          600: '#0267c1',
          700: '#03529d',
          800: '#074681',
          900: '#0c3b6c',
          950: '#082548',
        },
        flag: {
          low: '#d97706',      // amber for low
          normal: '#059669',   // emerald for normal
          high: '#dc2626',     // ruby for high
          unavail: '#64748b',  // slate for unavailable
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
