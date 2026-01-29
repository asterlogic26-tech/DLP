export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: "#0f172a",
          card: "#1e293b",
          accent: "#10b981", // Emerald green for security
          danger: "#ef4444"
        }
      }
    },
  },
  plugins: [],
}
