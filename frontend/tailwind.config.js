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
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
