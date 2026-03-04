'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { analyzeVideo } from '@/lib/api';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function UrlInput() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    // Handle Share Target API (receives ?url=... or ?text=...)
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const sharedUrl = params.get('url') || params.get('text');
        if (sharedUrl) {
            const extracted = sharedUrl.match(/(https?:\/\/[^\s]+)/);
            if (extracted) {
                setUrl(extracted[0]);
            } else {
                setUrl(sharedUrl);
            }
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!url) {
            toast.error('Bitte gib eine URL ein.');
            return;
        }

        const extracted = url.match(/(https?:\/\/[^\s]+)/);
        const finalUrl = extracted ? extracted[0] : url;

        try {
            new URL(finalUrl);
        } catch {
            toast.error('Ungültige URL. Bitte prüfe die Eingabe.');
            return;
        }

        const isSupported = finalUrl.includes('tiktok.com') || finalUrl.includes('instagram.com') || finalUrl.includes('youtube.com') || finalUrl.includes('youtu.be');

        if (!isSupported) {
            toast.error('Wir unterstützen aktuell nur TikTok, Instagram und YouTube.');
            return;
        }

        setLoading(true);
        try {
            const { id } = await analyzeVideo(finalUrl);
            router.push(`/analyze/${id}`);
        } catch (err: any) {
            toast.error(err.message || 'Ein Fehler ist aufgetreten.');
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="flex w-full items-center space-x-2">
                    <Input
                        autoFocus
                        type="url"
                        placeholder="TikTok, Instagram oder YouTube URL einfügen..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="flex-1 text-lg p-6 bg-gray-900 border-gray-800 text-white rounded-xl focus-visible:ring-blue-500"
                        disabled={loading}
                    />
                    <Button
                        type="submit"
                        disabled={loading}
                        className="p-6 text-lg bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
                    >
                        {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : null}
                        {loading ? 'Analysieren...' : 'Analysieren'}
                    </Button>
                </div>
            </form>
        </div>
    );
}
