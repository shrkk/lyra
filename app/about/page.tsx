'use client';

import React from 'react';
import { FloatingDock } from '@/components/ui/floating-dock';
import {
  IconHome,
  IconMessage,
  IconInfoCircle,
  IconLogin,
} from '@tabler/icons-react';
import Image from 'next/image';
import ContactForm from '@/components/ui/contact-form';
import LyraWorkflow from '@/components/ui/LyraWorkflow';
import UserProfile from '@/components/UserProfile';

export default function AboutPage() {
  const navItems = [
    {
      title: 'Home',
      href: '/',
      icon: <IconHome className="h-6 w-6 text-white" />,
    },
    {
      title: 'Chat',
      href: '/#chat',
      icon: <IconMessage className="h-6 w-6 text-white" />,
    },
    {
      title: 'Player',
      href: 'https://open.spotify.com',
      icon: <Image src="/spotify.png" alt="Player" width={24} height={24} className="h-5.5 w-6" />,
    },
    {
      title: 'About',
      href: '/about',
      icon: <IconInfoCircle className="h-6 w-6 text-white" />,
    },
  ];

  return (
    <main className="bg-black text-white min-h-screen">
      <UserProfile />
      <FloatingDock
        items={navItems}
        desktopClassName="fixed top-16 left-1/2 -translate-x-1/2 z-[100]"
        mobileClassName="fixed top-16 right-4 z-[100]"
      />
      <section className="container mx-auto px-6 py-40">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6">Our Mission</h1>
          <p className="text-xl text-white/80 leading-relaxed">
            At Lyra, our mission is to redefine the way you connect with music. We believe that listening should be more than just a passive experience—it should be an immersive journey of discovery, emotion, and personal expression. Lyra is designed to be your intelligent music companion, learning your unique tastes and anticipating the sounds that will move you.
          </p>
          <br />
          <p className="text-xl text-white/80 leading-relaxed">
            We are committed to bridging the gap between you and the vast universe of music, using cutting-edge technology to provide recommendations that are not just accurate, but emotionally resonant. Whether you're looking for the perfect playlist to power your workout, a chill beat to help you focus, or a fresh track from an emerging artist, Lyra is here to guide you. Our goal is to make music discovery seamless, personal, and profoundly joyful.
          </p>
        </div>
      </section>
      <LyraWorkflow />
      <ContactForm />
    </main>
  );
} 