export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        clinic: {
          page: '#F4F7FA',
          ink: '#102A43',
          muted: '#52616B',
          border: '#D8E2EA',
          lilac: '#FACEFF',
          pink: '#FFFACE',
          rose: '#CEFFFA',
          violet: '#6F3A78',
          blue: '#0F766E',
          cream: '#FFFACE',
          mint: '#CEFFFA',
          navy: '#17324D',
          teal: '#0F766E',
        },
        success: '#16A34A',
        danger: '#DC2626',
      },
      boxShadow: {
        soft: '0 18px 45px rgba(32, 48, 71, 0.10)',
        lift: '0 14px 34px rgba(124, 92, 203, 0.18)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.03)', opacity: '0.82' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 360ms ease-out both',
        'slide-up': 'slideUp 420ms ease-out both',
        'pulse-soft': 'pulseSoft 2.8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
