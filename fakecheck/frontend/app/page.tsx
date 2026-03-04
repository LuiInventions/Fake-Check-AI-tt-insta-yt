'use client';

import { motion } from 'framer-motion';
import UrlInput from '@/components/UrlInput';
import { Badge } from '@/components/ui/badge';
import { Share2, Link as LinkIcon } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center pt-20 pb-32">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center max-w-3xl mb-12"
      >
        <Badge variant="outline" className="mb-6 border-blue-600/30 text-blue-400 bg-blue-900/10 px-4 py-1.5 text-sm uppercase tracking-wider rounded-full">
          BETA VERSION
        </Badge>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Fake News erkennen mit KI.
        </h1>
        <p className="text-xl text-gray-400 mb-8 font-light">
          Schütze dich vor Manipulation. Analysiere Social-Media-Videos sekundenschnell auf ihren Wahrheitsgehalt.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="w-full relative z-10"
      >
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-20"></div>
        <div className="relative bg-gray-900/80 backdrop-blur-xl border border-gray-800 p-8 rounded-2xl shadow-2xl">
          <UrlInput />

          <div className="mt-8 flex flex-col items-center gap-4">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-widest">
              Unterstützte Plattformen
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Badge variant="secondary" className="bg-gray-800 text-gray-300 hover:bg-gray-700">TikTok</Badge>
              <Badge variant="secondary" className="bg-gray-800 text-gray-300 hover:bg-gray-700">Instagram</Badge>
              <Badge variant="secondary" className="bg-gray-800 text-gray-300 hover:bg-gray-700">YouTube</Badge>
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="mt-16 text-center"
      >
        <h3 className="text-lg font-medium text-gray-300 mb-6 border-b border-gray-800 pb-2 inline-block">Wie es funktioniert</h3>
        <div className="grid md:grid-cols-3 gap-8 mt-4 text-center">
          <div className="flex flex-col items-center">
            <div className="h-12 w-12 rounded-full bg-blue-900/40 text-blue-500 flex items-center justify-center mb-4">
              <Share2 className="w-5 h-5" />
            </div>
            <p className="text-sm text-gray-400 max-w-[250px]">Teile ein Video direkt aus deiner App über "Teilen an FakeCheck".</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="h-12 w-12 rounded-full bg-blue-900/40 text-blue-500 flex items-center justify-center mb-4">
              <LinkIcon className="w-5 h-5" />
            </div>
            <p className="text-sm text-gray-400 max-w-[250px]">Oder kopiere den Link und füge ihn manuell in das Suchfeld oben ein.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="h-12 w-12 rounded-full bg-blue-900/40 text-blue-500 flex items-center justify-center mb-4">
              <span className="text-xl">🤖</span>
            </div>
            <p className="text-sm text-gray-400 max-w-[250px]">Unsere KI kombiniert Transkripte und visuelle Daten zur Bewertung.</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
