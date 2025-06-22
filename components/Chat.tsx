'use client';

import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { PlaceholdersAndVanishInput } from './ui/placeholders-and-vanish-input';
import TypingIndicator from './TypingIndicator';
import LoginWithSpotify from './LoginWithSpotify';
import { supabase } from '@/lib/supabaseClient';

interface Track {
  id: string;
  name: string;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  tracks?: Track[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi, I'm Lyra 🎶 Your personal music companion. Ask me anything about your taste, favorite genres, or what to listen to next!",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [user, setUser] = useState<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    supabase.auth.getUser().then(({ data }) => setUser(data?.user));
  }, [messages, isTyping]);

  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (inputValue.trim()) {
      sendMessage(inputValue.trim());
      setInputValue(''); 
    }
  };

  const sendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date(),
    };

    const historyPayload = messages.slice(1).map(msg => ({
      role: msg.isUser ? 'user' : 'assistant',
      content: msg.text,
    }));

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8888/lyra/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: text,
          history: historyPayload
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from Lyra');
      }

      const data = await response.json();
      
      const lyraMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        tracks: data.tracks || [],
      };

      setMessages(prev => [...prev, lyraMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Oops! I couldn't reach the music library right now. Try again in a moment.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const placeholders = [
    "Recommend a chill lofi playlist",
    "What are my top artists?",
    "Find some high-energy workout music",
    "Any new music from my favorite genre?",
    "Create a playlist for a rainy day",
  ];

  if (!user) {
    return null;
  }

  return (
    <div className="bg-white/5 backdrop-blur-md rounded-2xl shadow-lg flex flex-col h-[70vh]">
      {/* Chat Window */}
      <div className="flex-1 overflow-y-auto chat-scrollbar px-6 py-4">
        <div className="max-w-4xl mx-auto">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message.text}
              isUser={message.isUser}
              timestamp={message.timestamp}
              tracks={message.tracks}
            />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-white/10">
         <PlaceholdersAndVanishInput 
            placeholders={placeholders}
            onChange={handleInputChange}
            onSubmit={handleSubmit}
          />
      </div>
    </div>
  );
} 