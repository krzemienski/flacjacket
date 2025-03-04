import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e3f2fd',
          100: '#bbdefb',
          200: '#90caf9',
          300: '#64b5f6',
          400: '#42a5f5',
          500: '#2196f3',
          600: '#1e88e5',
          700: '#1976d2',
          800: '#1565c0',
          900: '#0d47a1',
        },
        secondary: {
          50: '#fce4ec',
          100: '#f8bbd0',
          200: '#f48fb1',
          300: '#f06292',
          400: '#ec407a',
          500: '#e91e63',
          600: '#d81b60',
          700: '#c2185b',
          800: '#ad1457',
          900: '#880e4f',
        },
        background: {
          light: '#ffffff',
          dark: '#121212',
        },
        surface: {
          light: '#ffffff',
          dark: '#1e1e1e',
        },
        card: {
          light: '#ffffff',
          dark: '#242424',
        },
        error: {
          light: '#f44336',
          dark: '#e57373',
        },
        success: {
          light: '#4caf50',
          dark: '#81c784',
        },
        warning: {
          light: '#ff9800',
          dark: '#ffb74d',
        },
        info: {
          light: '#2196f3',
          dark: '#64b5f6',
        },
        text: {
          primary: {
            light: 'rgba(0, 0, 0, 0.87)',
            dark: 'rgba(255, 255, 255, 0.87)',
          },
          secondary: {
            light: 'rgba(0, 0, 0, 0.6)',
            dark: 'rgba(255, 255, 255, 0.6)',
          },
          disabled: {
            light: 'rgba(0, 0, 0, 0.38)',
            dark: 'rgba(255, 255, 255, 0.38)',
          },
        },
      },
    },
  },
  plugins: [],
}

export default config
