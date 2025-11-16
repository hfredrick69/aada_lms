/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#FBF8F0',   // AADA Brand Gold palette
          100: '#F5EDD8',
          200: '#E9D9B0',
          300: '#DDC588',
          400: '#D1AD54',  // AADA Brand Gold (main)
          500: '#D1AD54',  // AADA Brand Gold
          600: '#B8964A',
          700: '#9A7D3D',
          800: '#7C6431',
          900: '#5E4B25',
        },
      },
      fontFamily: {
        heading: ["'Georgia Pro'", 'Georgia', 'serif'],
      },
    },
  },
  plugins: []
};
