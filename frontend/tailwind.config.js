/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EBF5FF',
          100: '#E1EFFE',
          200: '#C3DDFD',
          300: '#A4CAFE',
          400: '#76A9FA',
          500: '#3F83F8',
          600: '#1C64F2',
          700: '#1A56DB',
          800: '#1E429F',
          900: '#233876',
        },
        secondary: {
          50: '#F7F8FA',
          100: '#EEF0F5',
          200: '#E2E6EF',
          300: '#CED3E0',
          400: '#A2AABE',
          500: '#76809B',
          600: '#5E6783',
          700: '#4A516B',
          800: '#373F53',
          900: '#252D40',
        },
      },
    },
  },
  plugins: [],
} 