/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#FFFBEB',
          100: '#FFF4C7',
          200: '#FFE083',
          300: '#FFD055',
          400: '#FFC12F',
          500: '#F5B800',
          600: '#D99F00',
          700: '#AD7A00',
          800: '#815600',
          900: '#573800',
        },
      },
    },
  },
  plugins: []
};
