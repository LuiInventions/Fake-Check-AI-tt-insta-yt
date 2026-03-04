'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getVideoStatus, getVideoFrames } from '@/lib/api';
import { VideoResponse } from '@/types';
import { Badge } from '@/components/ui/badge';
import LoadingPipeline from '@/components/LoadingPipeline';
import FakeNewsScore from '@/components/FakeNewsScore';
import FrameGallery from '@/components/FrameGallery';
import ChatInterface from '@/components/ChatInterface';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle, CheckCircle2, ChevronRight, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function AnalyzePage() {
    const { id } = useParams() as { id: string };
    const [video, setVideo] = useState<VideoResponse | null>(null);
    const [frames, setFrames] = useState<string[]>([]);
    const [error, setError] = useState('');
    const [elapsedTime, setElapsedTime] = useState(0);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        const startTime = Date.now();

        const poll = async () => {
            try {
                const now = Date.now();
                const secondsPassed = Math.floor((now - startTime) / 1000);
                setElapsedTime(secondsPassed);

                if (secondsPassed > 180) { // 3 minutes timeout
                    setError('Die Verarbeitung dauert länger als erwartet. Bitte versuche es später noch einmal.');
                    clearInterval(interval);
                    return;
                }

                const data = await getVideoStatus(id);
                setVideo(data);

                if (data.frames_paths && data.frames_paths.length > 0) {
                    setFrames(data.frames_paths);
                } else if (data.status === 'done' || data.status === 'processing') {
                    try {
                        const fData = await getVideoFrames(id);
                        setFrames(fData.frames || []);
                    } catch { }
                }

                if (data.status === 'done' || data.status === 'error') {
                    clearInterval(interval);
                }
            } catch (err: any) {
                setError(err.message || 'Fehler beim Laden des Videos');
                clearInterval(interval);
            }
        };

        poll(); // initial check
        interval = setInterval(poll, 2000); // poll every 2 seconds

        return () => clearInterval(interval);
    }, [id]);

    if (error) {
        return (
            <div className="max-w-2xl mx-auto pt-20">
                <Alert variant="destructive" className="bg-red-950/50 border-red-900 text-white">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Fehler</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            </div>
        );
    }

    if (!video) {
        return (
            <div className="pt-20 flex justify-center">
                <LoadingPipeline status="pending" />
            </div>
        );
    }

    const isProcessing = video.status !== 'done';
    const result = video.analysis_result;

    return (
        <div className="grid lg:grid-cols-12 gap-6 pt-6">
            <div className="lg:col-span-3 space-y-6">
                <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 shadow-sm min-h-[140px]">
                    {isProcessing && !video.title ? (
                        <div className="space-y-3">
                            <Skeleton className="h-6 w-3/4 bg-gray-800" />
                            <Skeleton className="h-4 w-1/4 bg-gray-800" />
                            <Skeleton className="h-4 w-full bg-gray-800 mt-4" />
                        </div>
                    ) : (
                        <>
                            <h2 className="text-xl font-semibold mb-2 line-clamp-2" title={video.title}>{video.title || 'Mysterium Video'}</h2>
                            <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
                                <Badge variant="outline" className="text-gray-300 border-gray-700 bg-gray-800 capitalize">
                                    {video.platform || 'Unbekannt'}
                                </Badge>
                            </div>
                            <div className="text-xs text-gray-500 break-all bg-gray-950 p-2 rounded">
                                {video.url}
                            </div>
                        </>
                    )}
                </div>

                <FrameGallery frames={frames} />
            </div>

            <div className="lg:col-span-5 space-y-6">
                {isProcessing ? (
                    <div className="flex flex-col items-center justify-center p-8 bg-gray-900/30 border border-gray-800 rounded-xl min-h-[500px]">
                        <LoadingPipeline status={video.status} />
                        <div className="mt-12 w-full space-y-4 px-6 opacity-30">
                            <Skeleton className="h-[200px] w-[200px] rounded-full mx-auto bg-gray-700" />
                            <Skeleton className="h-8 w-1/2 mx-auto bg-gray-700" />
                            <Skeleton className="h-24 w-full bg-gray-700" />
                            <Skeleton className="h-20 w-full bg-gray-700 mt-8" />
                        </div>
                    </div>
                ) : result ? (
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <span className="bg-blue-600 w-2 h-8 rounded-full inline-block"></span>
                            Analyse-Ergebnis
                        </h2>

                        <FakeNewsScore score={result.fake_score} />

                        <div className="my-6 flex justify-center">
                            <Badge
                                className={`text-sm px-4 py-1 flex items-center gap-2 border ${result.verdict === 'likely_fake' ? 'bg-red-950/50 text-red-500 border-red-900' :
                                    result.verdict === 'uncertain' ? 'bg-yellow-950/50 text-yellow-500 border-yellow-900' :
                                        'bg-green-950/50 text-green-500 border-green-900'
                                    }`}
                            >
                                {result.verdict === 'likely_fake' && <AlertCircle className="w-4 h-4" />}
                                {result.verdict === 'uncertain' && <AlertTriangle className="w-4 h-4" />}
                                {result.verdict === 'likely_real' && <CheckCircle2 className="w-4 h-4" />}
                                {result.verdict === 'likely_fake' ? 'Wahrscheinlich Fake' :
                                    result.verdict === 'uncertain' ? 'Unsicher' : 'Wahrscheinlich Echt'}
                            </Badge>
                        </div>

                        <p className="text-gray-300 text-base leading-relaxed mb-8 bg-gray-950 p-4 rounded-lg border border-gray-800">
                            {result.summary}
                        </p>

                        {result.red_flags && result.red_flags.length > 0 && (
                            <div className="mb-8">
                                <h3 className="text-sm font-semibold text-red-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4" /> Warnzeichen (Red Flags)
                                </h3>
                                <ul className="space-y-2">
                                    {result.red_flags.map((flag, idx) => (
                                        <li key={idx} className="flex gap-2 text-sm text-gray-400">
                                            <ChevronRight className="w-4 h-4 text-gray-600 shrink-0 mt-0.5" />
                                            <span>{flag}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <div>
                            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Überprüfte Behauptungen</h3>
                            <div className="space-y-4">
                                {result.claims.map((claim, idx) => (
                                    <div key={idx} className="bg-gray-900/50 border border-gray-800 p-4 rounded-lg">
                                        <p className="font-medium text-white mb-2 leading-snug">"{claim.claim}"</p>
                                        <div className="flex items-start gap-2 text-sm mt-2">
                                            {claim.assessment === 'true' && <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />}
                                            {claim.assessment === 'false' && <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />}
                                            {(claim.assessment === 'unverified' || claim.assessment === 'misleading') && <AlertTriangle className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />}

                                            <span className="text-gray-400">{claim.explanation}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>
                ) : (
                    <Alert className="bg-gray-900 border-gray-800">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Keine Analyse</AlertTitle>
                        <AlertDescription>Das Video wurde verarbeitet, aber es liegt kein Analyse-Ergebnis vor.</AlertDescription>
                    </Alert>
                )}
            </div>

            <div className="lg:col-span-4 h-full">
                <div className="sticky top-20">
                    <ChatInterface videoId={id} />
                </div>
            </div>
        </div>
    );
}
