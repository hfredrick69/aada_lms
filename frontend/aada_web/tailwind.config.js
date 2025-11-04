/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef9ff',
          100: '#d9efff',
          200: '#bce3ff',
          300: '#89d1ff',
          400: '#4cb8ff',
          500: '#1f9eff',
          600: '#0b7fe5',
          700: '#0666b8',
          800: '#085592',
          900: '#0b4675',
        },
      },
    },
  },
  plugins: [],
};

