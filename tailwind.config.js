import colors from 'tailwindcss/colors'

export default {
  content: ["./templates/**/*.html"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        ...colors,
        obsidian: '#050508',
        smoke: '#12121a',
        amber: '#F59E0B',
        ochre: '#B45309',
      },
      boxShadow: {
        glow: '0 0 20px rgba(245, 158, 11, 0.2)',
        panel: '0 24px 80px rgba(0, 0, 0, 0.45)',
      },
    },
  },
  plugins: [],
};