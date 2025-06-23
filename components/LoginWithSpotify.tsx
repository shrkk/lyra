"use client";
import { supabase } from '@/lib/supabaseClient';

export default function LoginWithSpotify() {
  const handleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'spotify',
      options: {
        redirectTo: process.env.NEXT_PUBLIC_SUPABASE_REDIRECT_URL || 'https://lyraai-git-main-shrkks-projects.vercel.app/auth/callback',
        scopes: 'user-read-private user-read-email user-top-read user-read-recently-played playlist-read-private offline_access',
      },
    });
  };

  return (
    <button onClick={handleLogin} className="fixed top-16 right-24 bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-full shadow">
      Sign in with Spotify
    </button>
  );
} 