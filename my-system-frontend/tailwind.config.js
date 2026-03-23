/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        darkbg: "#0A1A2F",
        darkpanel: "#11263F",
        darkborder: "#1E3A5F",
        darktext: "#E2E8F0",
        accent: "#FF7A00"
      }
    }
  },
  plugins: []
};
