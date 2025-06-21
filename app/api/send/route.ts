import { Resend } from 'resend';
import { NextResponse } from 'next/server';
import ContactFormEmail from '@/components/emails/contact-form-email';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  const { name, email, message } = await request.json();

  try {
    const data = await resend.emails.send({
      from: 'Lyra Contact Form <onboarding@resend.dev>',
      to: ['shreyank0108@gmail.com'],
      subject: 'New Message from Lyra Contact Form',
      react: ContactFormEmail({ name, email, message }),
    });

    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error });
  }
} 