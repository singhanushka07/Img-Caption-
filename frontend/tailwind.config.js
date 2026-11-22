/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#2563eb', hover: '#1d4ed8', bg: 'rgba(37,99,235,.06)' },
        success: { DEFAULT: '#059669', bg: 'rgba(5,150,105,.06)' },
        warning: { DEFAULT: '#d97706', bg: 'rgba(217,119,6,.06)' },
        danger: { DEFAULT: '#dc2626', bg: 'rgba(220,38,38,.06)' },
        purple: { DEFAULT: '#7c3aed', bg: 'rgba(124,58,237,.06)' },
        surface: '#ffffff',
        bg: '#f8fafc',
        border: '#e2e8f0',
        'border-hover': '#cbd5e1',
        text: { DEFAULT: '#0f172a', secondary: '#475569', muted: '#94a3b8' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '12px',
        sm: '8px',
        xs: '6px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(0,0,0,.04)',
        md: '0 4px 12px rgba(0,0,0,.06)',
        lg: '0 8px 24px rgba(0,0,0,.08)',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0', transform: 'translateY(6px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        logIn: { from: { opacity: '0', transform: 'translateX(-4px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
        pulseDot: { '0%,100%': { opacity: '1' }, '50%': { opacity: '.4' } },
      },
      animation: {
        fadeIn: 'fadeIn .25s ease both',
        logIn: 'logIn .2s ease forwards',
        shimmer: 'shimmer 1.4s infinite',
        pulseDot: 'pulseDot 2s ease infinite',
      },
    },
  },
  plugins: [],
}
