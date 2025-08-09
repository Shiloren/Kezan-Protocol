export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'black-mineral': '#0f0f11',
        'graphite-soft': '#1a1b1e',
        'goblin-green': '#5cc585',
        'deep-emerald': '#2a6041', // Verde oscuro complementario
        'spectral-cyan': '#4dd0e1',
        'golden-glow': '#f9b531', // Amarillo dorado para riqueza
        'muted-red': '#e57373',
        'warm-white': '#f1f1f1',
        'light-gray': '#d6d6d6',
        'steel-gray': '#7a8a99', // Metálico para tecnología
        'bronze': '#cd7f32' // Bronce para maquinaria
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        alt: ['Be Vietnam Pro', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Monaco', 'monospace']
      }
    }
  },
  plugins: []
};
