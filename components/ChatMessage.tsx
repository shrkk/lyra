import React from 'react';

interface Track {
  id: string;
  name: string;
  preview_url?: string;
  spotify_url?: string;
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
                    <p className="text-sm font-semibold mb-1 flex items-center gap-2">
                      {track.name}
                      {track.spotify_url && (
                        <a href={track.spotify_url} target="_blank" rel="noopener noreferrer" title="Open in Spotify">
                          <svg width="20" height="20" viewBox="0 0 168 168" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="84" cy="84" r="84" fill="#1ED760"/>
                            <path d="M120.1 116.3c-1.7 2.8-5.3 3.7-8.1 2-22.2-13.6-50.2-16.7-83.2-9.2-3.2.7-6.4-1.3-7.1-4.5-.7-3.2 1.3-6.4 4.5-7.1 35.5-7.9 66.2-4.4 90.5 10.4 2.8 1.7 3.7 5.3 2 8.1zm11.6-23.6c-2.1 3.4-6.5 4.5-9.9 2.4-25.4-15.6-64.2-20.1-94.2-11.1-3.8 1.1-7.8-1.1-8.9-4.9-1.1-3.8 1.1-7.8 4.9-8.9 33.7-9.8 75.1-5 103.6 12.2 3.4 2.1 4.5 6.5 2.4 9.9zm12.2-26.1c-30.1-17.9-79.7-19.6-108.2-10.8-4.4 1.3-9-1.2-10.3-5.6-1.3-4.4 1.2-9 5.6-10.3 31.8-9.5 85.1-7.6 119.7 12.1 4 2.4 5.3 7.6 2.9 11.6-2.4 4-7.6 5.3-11.6 2.9z" fill="#fff"/>
                          </svg>
                        </a>
                      )}
                    </p>
                    {track.preview_url ? (
                      <audio controls src={track.preview_url} className="w-full mt-1 rounded">
                        Your browser does not support the audio element.
                      </audio>
                    ) : (
                      <iframe
                        src={`https://open.spotify.com/embed/track/${track.id}`}
                        width="100%"
                        height="80"
                        frameBorder="0"
                        allowTransparency={true}
                        allow="encrypted-media"
                      ></iframe>
                    )}
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