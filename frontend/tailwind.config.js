/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#1a1f36',
          50: '#eef0f7',
          100: '#d4d8eb',
          200: '#a9b1d7',
          300: '#7e8ac3',
          400: '#5363af',
          500: '#2d3880',
          600: '#272d54',
          700: '#1a1f36',
          800: '#131729',
          900: '#0c0f1c',
        },
      },
    },
  },
  safelist: [
    // Color theme presets for stock rise/fall
    'text-emerald-600', 'text-sky-600', 'text-violet-600',
    'text-red-600', 'text-orange-600', 'text-pink-600',
    'bg-emerald-100', 'bg-sky-100', 'bg-violet-100',
    'bg-red-100', 'bg-orange-100', 'bg-pink-100',
    'text-emerald-700', 'text-sky-700', 'text-violet-700',
    'text-red-700', 'text-orange-700', 'text-pink-700',
  ],
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
