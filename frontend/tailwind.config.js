/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'bin-blue': '#0066CC',
        'bin-yellow': '#FFCC00',
        'bin-brown': '#8B4513',
        'bin-green': '#00AA44',
      },
    },
  },
  plugins: [],
}
