import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const code = req.nextUrl.searchParams.get('code');
  if (!code) {
    return NextResponse.json({ error: 'No code provided' }, { status: 400 });
  }

  const clientId = process.env.SPOTIPY_CLIENT_ID!;
  const clientSecret = process.env.SPOTIPY_CLIENT_SECRET!;
  const redirectUri = process.env.SPOTIPY_REDIRECT_URI!;

  const basicAuth = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

  const tokenRes = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${basicAuth}`,
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
    }),
  });

  const tokenData = await tokenRes.json();

  // Redirect to a frontend route to set the token in localStorage and then go to homepage
  if (tokenData.access_token) {
    const params = new URLSearchParams({ access_token: tokenData.access_token });
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/auth/spotify/set-token?${params.toString()}`);
  }

  return NextResponse.json(tokenData);
} 