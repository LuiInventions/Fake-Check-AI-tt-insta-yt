import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FakeCheck – KI-gestützter Fake News Detector",
  description: "Fake News erkennen mit KI. Überprüfe Videos auf Falschinformationen.",
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de" className="dark">
      <body className={`${inter.className} bg-gray-950 text-white antialiased min-h-screen flex flex-col`}>
        <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 h-16 flex items-center">
            <a href="/" className="text-xl font-bold flex items-center gap-2">
              <span className="text-2xl">🛡️</span> FakeCheck
            </a>
          </div>
        </header>
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
          {children}
        </main>
        <Toaster position="top-center" theme="dark" />
      </body>
    </html>
  );
}
