/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "media",
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"] },
      colors: {
        brand: { 50: "#eef5fd", 100: "#cde2fb", 500: "#2a78d6", 600: "#256abf", 700: "#1c5cab" },
      },
    },
  },
  plugins: [],
};
