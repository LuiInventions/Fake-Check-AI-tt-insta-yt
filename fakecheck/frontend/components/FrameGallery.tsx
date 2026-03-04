'use client';
import { useState } from 'react';

export default function FrameGallery({ frames }: { frames: string[] }) {
    const [selectedFrame, setSelectedFrame] = useState<string | null>(null);

    if (!frames || frames.length === 0) return null;

    return (
        <div className="mt-8">
            <h3 className="text-lg font-medium text-white mb-4">Extrahierte Video Frames</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {frames.map((frame, idx) => (
                    <div
                        key={idx}
                        className="relative aspect-video rounded-lg overflow-hidden cursor-pointer border border-gray-800 hover:border-blue-500 transition-colors group"
                        onClick={() => setSelectedFrame(frame)}
                    >
                        {/* Rewrite path assuming server provides /app/data/frames/xyz.jpg to /data/frames/xyz.jpg which nginx serves */}
                        <img src={frame.replace('/app', '')} alt={`Frame ${idx + 1}`} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                        <div className="absolute bottom-1 right-1 bg-black/70 px-1.5 py-0.5 rounded text-xs text-white">
                            #{idx + 1}
                        </div>
                    </div>
                ))}
            </div>

            {selectedFrame && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" onClick={() => setSelectedFrame(null)}>
                    <div className="relative max-w-5xl w-full flex flex-col items-end">
                        <button className="text-white hover:text-gray-300 mb-2 font-medium" onClick={() => setSelectedFrame(null)}>Schließen</button>
                        <img src={selectedFrame.replace('/app', '')} alt="Selected Frame" className="w-full h-auto rounded-xl shadow-2xl border border-gray-800" />
                    </div>
                </div>
            )}
        </div>
    );
}
