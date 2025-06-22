import { NextResponse } from 'next/server';

export async function GET() {
  const clientId = process.env.SPOTIPY_CLIENT_ID;
  const redirectUri = process.env.SPOTIPY_REDIRECT_URI;
  const scopes = [
    'user-read-private',
    'user-read-email',
    'user-top-read',
    'user-read-recently-played',
    'user-read-currently-playing',
    'user-read-playback-state',
    'user-modify-playback-state',
    'playlist-read-private',
    'playlist-modify-private',
    'playlist-modify-public',
    'user-library-read',
    'user-library-modify',
    'user-follow-read',
    'user-follow-modify',
  ];
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId!,
    scope: scopes.join(' '),
    redirect_uri: redirectUri!,
    show_dialog: 'true',
  });
  return NextResponse.redirect(
    `https://accounts.spotify.com/authorize?${params.toString()}`
  );
} 