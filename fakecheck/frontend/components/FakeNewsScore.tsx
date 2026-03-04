'use client';
import { motion } from 'framer-motion';

export default function FakeNewsScore({ score }: { score: number }) {
    // score is 0.0 to 1.0 (0=fake, 1=real)
    let colorClass = 'text-green-500';
    let strokeClass = 'stroke-green-500';

    if (score < 0.3) {
        colorClass = 'text-red-500';
        strokeClass = 'stroke-red-500';
    } else if (score < 0.7) {
        colorClass = 'text-yellow-500';
        strokeClass = 'stroke-yellow-500';
    }

    const percentage = Math.round(score * 100);
    const circumference = 2 * Math.PI * 45; // r=45
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
        <div className="relative flex items-center justify-center w-48 h-48 mx-auto my-6">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="8"
                    className="text-gray-800"
                />
                <motion.circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="8"
                    strokeLinecap="round"
                    className={strokeClass}
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-4xl font-bold ${colorClass}`}>{percentage}%</span>
                <span className="text-gray-400 text-sm mt-1">Echt-Score</span>
            </div>
        </div>
    );
}
