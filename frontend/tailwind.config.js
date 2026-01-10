/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // 核心背景色
                'tissue-base': '#0d0d0f',
                'tissue-elevated': '#141416',
                'tissue-container': '#1a1a1d',
                'tissue-spotlight': '#222226',

                // 金色系
                'gold': {
                    DEFAULT: '#d4a852',
                    light: '#e8c780',
                    dark: '#b08d3e',
                    glow: 'rgba(212, 168, 82, 0.15)',
                },

                // 文字色
                'tissue-text': {
                    DEFAULT: '#f0f0f2',
                    secondary: '#a0a0a8',
                    tertiary: '#6a6a72',
                },

                // 边框色
                'tissue-border': {
                    DEFAULT: 'rgba(255, 255, 255, 0.08)',
                    secondary: 'rgba(255, 255, 255, 0.04)',
                    gold: 'rgba(212, 168, 82, 0.3)',
                },
            },
            borderRadius: {
                'tissue-sm': '6px',
                'tissue-md': '10px',
                'tissue-lg': '14px',
                'tissue-xl': '20px',
            },
            boxShadow: {
                'tissue-sm': '0 2px 8px rgba(0, 0, 0, 0.3)',
                'tissue-md': '0 4px 16px rgba(0, 0, 0, 0.4)',
                'tissue-lg': '0 8px 32px rgba(0, 0, 0, 0.5)',
                'tissue-gold': '0 0 20px rgba(212, 168, 82, 0.15)',
            },
            animation: {
                'tissue-fade-in': 'tissue-fade-in 250ms ease-out forwards',
                'tissue-scale-in': 'tissue-scale-in 250ms ease-out forwards',
                'tissue-shimmer': 'tissue-shimmer 1.5s infinite',
                'tissue-glow': 'tissue-glow-pulse 2s ease-in-out infinite',
            },
            keyframes: {
                'tissue-fade-in': {
                    from: { opacity: '0', transform: 'translateY(10px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                'tissue-scale-in': {
                    from: { opacity: '0', transform: 'scale(0.95)' },
                    to: { opacity: '1', transform: 'scale(1)' },
                },
                'tissue-shimmer': {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
                'tissue-glow-pulse': {
                    '0%, 100%': { boxShadow: '0 0 20px rgba(212, 168, 82, 0.1)' },
                    '50%': { boxShadow: '0 0 30px rgba(212, 168, 82, 0.25)' },
                },
            },
            fontFamily: {
                display: ['SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
                body: ['SF Pro Text', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
                mono: ['SF Mono', 'Fira Code', 'monospace'],
            },
            transitionTimingFunction: {
                'tissue': 'cubic-bezier(0.4, 0, 0.2, 1)',
            },
            transitionDuration: {
                'tissue-fast': '150ms',
                'tissue-base': '250ms',
                'tissue-slow': '400ms',
            },
            backdropBlur: {
                'tissue': '20px',
            },
        },
    },
    plugins: [],
    corePlugins: {
        preflight: false,
    },
}
