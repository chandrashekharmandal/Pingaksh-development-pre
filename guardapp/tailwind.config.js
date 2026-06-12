/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: "#6C63FF",
        secondary: "#1E1E2E",
        accent: "#00D4AA",
        surface: "#2A2A3E",
        danger: "#FF4757",
        warning: "#FFA502",
        earn: "#4CD137",
      },
      fontFamily: {
        sans: ["System"],
      },
    },
  },
  plugins: [],
};
