/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        stripe: {
          navy: '#0a2540',
          'navy-light': '#0d2d4a',
          bg: '#f6f9fc',
          primary: '#635bff',
          'primary-hover': '#4f46e8',
          border: '#e6ebf1',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'stripe': '0 1px 3px 0 rgba(10, 37, 64, 0.08)',
        'stripe-lg': '0 4px 6px -1px rgba(10, 37, 64, 0.06), 0 2px 4px -2px rgba(10, 37, 64, 0.04)',
      },
    },
  },
  plugins: [],
}
