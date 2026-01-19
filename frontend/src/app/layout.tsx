import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Waste Classification System',
  description: 'Classify waste items for Hong Kong waste management',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
