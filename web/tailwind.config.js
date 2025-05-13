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
        dark: {
          primary: '#000000',
          secondary: '#1a1a1a',
          accent: '#2d2d2d',
          text: '#ffffff',
        }
      },
    },
  },
  plugins: [],
} 