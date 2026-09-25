/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand colors (brown/tan)
        brand: {
          50: '#f8f7f5',
          100: '#f1ede7',
          200: '#e2dcd0',
          300: '#d2cab8',
          400: '#a0826d',
          500: '#8b5a3c', // Secondary brown
          600: '#6b4423', // Dark brown
          700: '#5a3a1f', // Darker brown
          800: '#4a2c18',
          900: '#3a2010',
        },
        cream: '#FFF8F0',
        tan: {
          50: '#fffbf7',
          100: '#fff8f0',
          200: '#f5e6d3',
          300: '#e2dcd0',
          400: '#d2b48c',
          500: '#bfa08f',
          600: '#a0826d',
        },
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
        },
      },
      spacing: {
        gutter: '1.5rem',
      },
      fontSize: {
        // Body: 16px/24px (default)
        // Labels: 14px/20px
        'label': ['14px', '20px'],
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        spin: 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
