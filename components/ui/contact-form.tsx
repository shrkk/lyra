'use client';

import React, { useState } from 'react';

export default function ContactForm() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [feedbackMessage, setFeedbackMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus('loading');

    const formData = new FormData(e.target as HTMLFormElement);
    const name = formData.get('name') as string;
    const email = formData.get('email') as string;
    const message = formData.get('message') as string;

    try {
      const response = await fetch('/api/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, message }),
      });

      if (response.ok) {
        setStatus('success');
        setFeedbackMessage('Thank you for your message! I will get back to you soon.');
        (e.target as HTMLFormElement).reset();
      } else {
        throw new Error('Failed to send message.');
      }
    } catch (error) {
      setStatus('error');
      setFeedbackMessage('Something went wrong. Please try again.');
    }
  };

  return (
    <section className="py-20">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">Contact Us</h2>
        <p className="text-lg text-white/70 mb-10">
          Have questions or feedback? We'd love to hear from you.
        </p>
        <form onSubmit={handleSubmit} className="space-y-6 text-left">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-white/90 mb-2">
              Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              className="w-full bg-white/10 border border-white/20 rounded-lg py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
              disabled={status === 'loading'}
            />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-white/90 mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              className="w-full bg-white/10 border border-white/20 rounded-lg py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
              disabled={status === 'loading'}
            />
          </div>
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-white/90 mb-2">
              Message
            </label>
            <textarea
              id="message"
              name="message"
              rows={5}
              className="w-full bg-white/10 border border-white/20 rounded-lg py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
              disabled={status === 'loading'}
            ></textarea>
          </div>
          <div className="text-center">
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-full transition-colors duration-300 disabled:opacity-50"
              disabled={status === 'loading'}
            >
              {status === 'loading' ? 'Sending...' : 'Send Message'}
            </button>
          </div>
        </form>
        {status === 'success' && (
          <p className="mt-4 text-green-500">{feedbackMessage}</p>
        )}
        {status === 'error' && (
          <p className="mt-4 text-red-500">{feedbackMessage}</p>
        )}
      </div>
    </section>
  );
} 