/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      fontSize: {
        '10xl': '10rem',
        '11xl': '11rem',
        '12xl': '12rem',
      },
      colors: {
        'lyra-primary': '#9E00FF',
        'lyra-secondary': '#2EB9DF',
        lyra: {
          background: '#fafafa',
          lyraBubble: '#f3f4f6',
          userBubble: '#e0f2fe',
          primary: '#8b5cf6',
          secondary: '#06b6d4',
        }
      },
      animation: {
        typing: "typing 2s steps(20, end), blink .75s step-end infinite"
      },
      keyframes: {
        typing: {
          "from": { width: "0" },
          "to": { width: "100%" }
        },
        "blink": {
          "from, to": { borderColor: "transparent" },
          "50%": { borderColor: "white" }
        }
      },
    },
  },
  plugins: [],
} 