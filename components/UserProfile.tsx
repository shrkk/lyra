'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';

export default function UserProfile() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data?.user));
  }, []);

  if (!user) return null;

  const avatar = user.user_metadata?.avatar_url;
  const name = user.user_metadata?.full_name || user.user_metadata?.name || user.email;

  return (
    <div className="fixed top-16 right-24 z-[101] flex items-center gap-3 bg-neutral-900 px-4 py-2 rounded-full shadow-lg border border-neutral-700">
      {avatar && (
        <img src={avatar} alt="Profile" className="w-8 h-8 rounded-full object-cover" />
      )}
      <span className="font-medium text-white text-sm">{name}</span>
    </div>
  );
} 