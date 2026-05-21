import daisyui from 'daisyui';

const usiPalette = {
  navy: '#102D52',
  celeste: '#0EA5E9',
  lilac: '#C2A4CF',
  bg: '#F8FAFC',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  muted: '#64748B',
  dark: '#0F172A',
};

const healthPalette = {
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
};

const clinicPalette = {
  page: usiPalette.bg,
  surface: usiPalette.surface,
  elevated: '#F1F5F9',
  ink: usiPalette.dark,
  muted: usiPalette.muted,
  subtle: '#94A3B8',
  border: usiPalette.border,
  line: '#E8EEF5',
  navy: usiPalette.navy,
  teal: usiPalette.celeste,
  blue: usiPalette.celeste,
  indigo: usiPalette.navy,
  mint: '#E0F2FE',
  sky: '#E0F2FE',
  lilac: '#F6F0F9',
  cream: usiPalette.bg,
  rose: '#F7F1FA',
  violet: usiPalette.lilac,
};

const daisyUsiTheme = {
  primary: usiPalette.navy,
  'primary-content': '#FFFFFF',
  secondary: usiPalette.celeste,
  'secondary-content': '#FFFFFF',
  accent: usiPalette.lilac,
  'accent-content': usiPalette.dark,
  neutral: usiPalette.dark,
  'neutral-content': usiPalette.bg,
  'base-100': usiPalette.surface,
  'base-200': usiPalette.bg,
  'base-300': usiPalette.border,
  'base-content': usiPalette.dark,
  info: usiPalette.celeste,
  'info-content': '#FFFFFF',
  success: healthPalette.success,
  'success-content': '#FFFFFF',
  warning: healthPalette.warning,
  'warning-content': usiPalette.dark,
  error: healthPalette.danger,
  'error-content': '#FFFFFF',
  '--rounded-box': '0.75rem',
  '--rounded-btn': '0.5rem',
  '--rounded-badge': '999px',
  '--animation-btn': '0.18s',
  '--btn-focus-scale': '0.99',
  '--border-btn': '1px',
  '--tab-border': '1px',
  '--tab-radius': '0.5rem',
};

export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        usi: usiPalette,
        health: healthPalette,
        clinic: clinicPalette,
        success: healthPalette.success,
        danger: healthPalette.danger,
        warning: healthPalette.warning,
        info: usiPalette.celeste,
      },
      boxShadow: {
        soft: '0 12px 30px rgba(15, 23, 42, 0.08)',
        lift: '0 16px 36px rgba(15, 23, 42, 0.13)',
        focus: '0 0 0 4px rgba(14, 165, 233, 0.18)',
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
  daisyui: {
    logs: false,
    themes: [
      {
        usiTheme: daisyUsiTheme,
      },
      {
        clinic: daisyUsiTheme,
      },
    ],
    darkTheme: 'usiTheme',
  },
  plugins: [daisyui],
};
