import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "The Diamond Sutra Project",
    template: "%s | The Diamond Sutra Project",
  },
  description:
    "Awareness, content, and education on the Diamond Sutra for beginners through advanced practitioners — podcasts, webinars, a life-feedback blog, and interactive stories.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col font-sans">
        <Nav />
        <main className="flex-1 mx-auto w-full max-w-5xl px-4 py-10">{children}</main>
        <Footer />
        <Analytics />
      </body>
    </html>
  );
}
