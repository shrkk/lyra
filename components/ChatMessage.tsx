import React from 'react';

interface Track {
  id: string;
  name: string;
}

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;
  tracks?: Track[];
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser, timestamp, tracks }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-lg backdrop-blur-sm ${
          isUser
            ? 'bg-white/20 text-white'
            : 'bg-white/20 text-white'
        }`}
      >
        <div className="flex items-start space-x-2">
          {!isUser && (
            <div className="flex-shrink-0 w-8 h-8 bg-lyra-primary rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">🎵</span>
            </div>
          )}
          <div className="flex-1">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
            {tracks && tracks.length > 0 && (
              <div className="mt-4 space-y-2">
                {tracks.map((track) => (
                  <div key={track.id}>
                    <p className="text-sm font-semibold mb-1">{track.name}</p>
                    <iframe
                      src={`https://open.spotify.com/embed/track/${track.id}`}
                      width="100%"
                      height="80"
                      frameBorder="0"
                      allowTransparency={true}
                      allow="encrypted-media"
                    ></iframe>
                  </div>
                ))}
              </div>
            )}
            {timestamp && (
              <p className="text-xs text-gray-500 mt-1">
                {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 