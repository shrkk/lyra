# Lyra UI - Your Personal Music Companion

A beautiful, responsive chat interface for Lyra, your intelligent music insight companion powered by Spotify data and Groq LLM.

## Features

- 🎵 **Real-time Chat**: Natural conversation with Lyra about your music taste
- 🎨 **Beautiful UI**: Clean, modern design with music-inspired aesthetics
- 📱 **Responsive**: Works perfectly on desktop and mobile devices
- 🔄 **Real-time Updates**: Typing indicators and smooth animations
- 🎯 **Smart Recommendations**: Lyra uses your Spotify data for personalized insights

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Backend**: Flask API (separate repository)
- **LLM**: Groq API integration
- **Music Data**: Spotify Web API

## Getting Started

### Prerequisites

- Node.js 18+ 
- Your Lyra backend server running on `http://localhost:8888`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
lyra-ui/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main chat page
├── components/            # React components
│   ├── ChatInput.tsx      # Message input component
│   ├── ChatMessage.tsx    # Individual message display
│   └── TypingIndicator.tsx # Loading animation
├── tailwind.config.js     # Tailwind configuration
└── package.json           # Dependencies and scripts
```

## Usage

1. **Start your Lyra backend server** (Flask API)
2. **Open the UI** in your browser
3. **Chat with Lyra** about your music taste, ask for recommendations, or explore your listening habits

## Customization

### Colors
Edit `tailwind.config.js` to customize the color scheme:
```javascript
colors: {
  lyra: {
    background: '#fafafa',
    lyraBubble: '#f3f4f6',
    userBubble: '#e0f2fe',
    primary: '#8b5cf6',
    secondary: '#06b6d4',
  }
}
```

### Backend URL
Update the API endpoint in `app/page.tsx`:
```typescript
const response = await fetch('http://localhost:8888/lyra/chat', {
  // ... configuration
});
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details