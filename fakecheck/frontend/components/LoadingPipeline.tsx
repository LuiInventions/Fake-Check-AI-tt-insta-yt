'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

interface LoadingPipelineProps {
    status: string;
}

export default function LoadingPipeline({ status }: LoadingPipelineProps) {
    // We infer the step based on "status" or standard timing (if status=processing)
    // Since FastAPI returns "pending", "processing", "done", "error"
    // Here we mock a pipeline animation if processing

    const steps = [
        { label: 'Video wird heruntergeladen...', activeState: 'pending' },
        { label: 'Audio wird transkribiert...', activeState: 'processing_audio' },
        { label: 'Frames werden extrahiert...', activeState: 'processing_frames' },
        { label: 'KI analysiert den Inhalt...', activeState: 'analyzing' },
    ];

    // Assuming status is "processing", we can show a generic "Verarbeitung..." or animate through steps.
    // For simplicity since the backend just gives 'processing', we'll animate them fake-progressively if status is 'processing'.

    return (
        <div className="w-full max-w-md mx-auto bg-gray-900/50 p-6 rounded-xl border border-gray-800">
            <h3 className="text-lg font-medium text-white mb-6">Analyse läuft...</h3>

            <div className="space-y-6">
                {steps.map((step, idx) => (
                    <div key={idx} className="flex items-center gap-4">
                        <div className="relative">
                            {status === 'error' ? (
                                <Circle className="h-6 w-6 text-red-500" />
                            ) : status === 'done' ? (
                                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                                </motion.div>
                            ) : (
                                <Loader2 className="h-6 w-6 text-blue-500 animate-spin" />
                            )}
                        </div>
                        <span className="text-gray-300 font-medium">{step.label}</span>
                    </div>
                ))}
            </div>

            <p className="mt-8 text-sm text-gray-500 text-center">Dies kann bis zu einer Minute dauern</p>
        </div>
    );
}
