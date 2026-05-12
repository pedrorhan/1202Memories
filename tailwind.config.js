/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',
    './**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        // Minimalist dark mode colors
        dark: {
          bg: '#0f172a',    // slate-900
          surface: '#1e293b', // slate-800
          border: '#334155',  // slate-700
          text: '#f8fafc',    // slate-50
          muted: '#94a3b8',   // slate-400
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
