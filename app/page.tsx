'use client';

import React from 'react';
import Chat from '@/components/Chat';
import { FloatingDock } from '@/components/ui/floating-dock';
import {
  IconHome,
  IconMessage,
  IconInfoCircle,
  IconLogin,
} from '@tabler/icons-react';
import { SparklesCore } from '@/components/ui/sparkles';
import Image from 'next/image';
import UserProfile from '@/components/UserProfile';
import { supabase } from '@/lib/supabaseClient';

export default function Home() {
  const navItems = [
    {
      title: 'Home',
      href: '/',
      icon: <IconHome className="h-6 w-6 text-white" />,
    },
    {
      title: 'Chat',
      href: '#chat',
      icon: <IconMessage className="h-6 w-6 text-white" />,
    },
    {
      title: 'Login',
      href: '#',
      icon: <IconLogin className="h-6 w-6 text-white" />,
      onClick: async () => {
        await supabase.auth.signInWithOAuth({
          provider: 'spotify',
          options: {
            redirectTo: process.env.NEXT_PUBLIC_SUPABASE_REDIRECT_URL || 'https://lyraai-git-main-shrkks-projects.vercel.app/auth/callback',
            scopes: 'user-top-read user-read-recently-played playlist-read-private',
          },
        });
      },
    },
    {
      title: 'About',
      href: '/about',
      icon: <IconInfoCircle className="h-6 w-6 text-white" />,
    },
  ];

  return (
    <main className="bg-black text-white">
      <UserProfile />
      <FloatingDock
        items={navItems}
        desktopClassName="fixed top-16 left-1/2 -translate-x-1/2"
        mobileClassName="fixed top-16 right-4"
      />
      {/* Hero Page */}
      <section className="h-screen flex flex-col items-center justify-center text-center p-6">
        <p className="text-3xl font-bold text-white/80">Chat. Discover. Play.</p>
        <h1 className="text-12xl font-bold -mt-8">Lyra</h1>
        <div className="w-[40rem] h-40 relative -mt-12">
          {/* Gradients */}
          <div className="absolute inset-x-20 top-0 bg-gradient-to-r from-transparent via-indigo-500 to-transparent h-[2px] w-3/4 blur-sm" />
          <div className="absolute inset-x-20 top-0 bg-gradient-to-r from-transparent via-indigo-500 to-transparent h-px w-3/4" />
          <div className="absolute inset-x-60 top-0 bg-gradient-to-r from-transparent via-sky-500 to-transparent h-[5px] w-1/4 blur-sm" />
          <div className="absolute inset-x-60 top-0 bg-gradient-to-r from-transparent via-sky-500 to-transparent h-px w-1/4" />

          {/* Core component */}
          <SparklesCore
            background="transparent"
            minSize={0.4}
            maxSize={1}
            particleDensity={1200}
            className="w-full h-full"
            particleColor="#FFFFFF"
          />

          {/* Radial Gradient to prevent sharp edges */}
          <div className="absolute inset-0 w-full h-full bg-black [mask-image:radial-gradient(350px_200px_at_top,transparent_20%,white)]"></div>
        </div>
      </section>

      {/* Chat Page */}
      <section id="chat" className="min-h-screen flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-4xl">
          <Chat />
        </div>
      </section>
    </main>
  );
} 