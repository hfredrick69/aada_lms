/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5faff",
          100: "#e6f4ff",
          200: "#bfdfff",
          300: "#99cbff",
          400: "#66afff",
          500: "#338fff",
          600: "#1876e6",
          700: "#0f5cb3",
          800: "#0a4080",
          900: "#06264d"
        }
      }
    }
  },
  plugins: []
};
