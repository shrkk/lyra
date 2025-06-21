import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-lyra-lyraBubble px-4 py-3 rounded-2xl shadow-sm">
        <div className="flex items-center space-x-2">
          <div className="flex-shrink-0 w-8 h-8 bg-lyra-primary rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">🎵</span>
          </div>
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-typing"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-typing" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-typing" style={{ animationDelay: '0.4s' }}></div>
          </div>
          <span className="text-sm text-gray-600 ml-2">Lyra is thinking...</span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator; 