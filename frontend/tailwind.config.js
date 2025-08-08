module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'black-mineral': '#0f0f11',
        'graphite-soft': '#1a1b1e',
        'goblin-green': '#5cc585',
        'spectral-cyan': '#4dd0e1',
        'warm-yellow': '#f6c453',
        'muted-red': '#e57373',
        'warm-white': '#f1f1f1',
        'light-gray': '#d6d6d6'
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
