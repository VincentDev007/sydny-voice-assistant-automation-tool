/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hal-red': '#FF0000',
        'hal-green': '#00FF00',
      }
    },
  },
  plugins: [],
}
