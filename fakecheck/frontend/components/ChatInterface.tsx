'use client';

import { useState, useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { getChatHistory, sendChatMessage } from '@/lib/api';
import { ChatMessage } from '@/types';
import { Loader2, Send } from 'lucide-react';

export default function ChatInterface({ videoId }: { videoId: string }) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        async function fetchHistory() {
            try {
                const data = await getChatHistory(videoId);
                if (data.history) {
                    setMessages(data.history);
                }
            } catch (err) {
                console.error('Failed to load chat history', err);
            }
        }
        fetchHistory();
    }, [videoId]);

    useEffect(() => {
        // Scroll to bottom
        const scrollContainer = document.querySelector('[data-radix-scroll-area-viewport]');
        if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
    }, [messages, loading]);

    const handleSend = async (messageText = input) => {
        if (!messageText.trim()) return;

        setInput('');
        const newMsg: ChatMessage = { role: 'user', content: messageText };
        setMessages(prev => [...prev, newMsg]);
        setLoading(true);

        try {
            const { reply } = await sendChatMessage(videoId, messageText);
            setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Es gab ein Problem beim Abrufen der Antwort. Bitte versuche es noch einmal.' }]);
        } finally {
            setLoading(false);
        }
    };

    const suggestions = [
        "Ist das Video manipuliert?",
        "Welche Quellen werden genannt?",
        "Was stimmt an den Behauptungen nicht?"
    ];

    return (
        <div className="flex flex-col h-[600px] bg-gray-900 border border-gray-800 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-gray-800 bg-gray-950 flex items-center justify-between">
                <h3 className="font-semibold text-white">FakeCheck KI-Assistent</h3>
            </div>

            <ScrollArea className="flex-1 p-4 bg-gray-900/50">
                <div className="space-y-4">
                    {messages.length === 0 && !loading && (
                        <div className="text-center text-gray-500 my-10 text-sm">
                            Stelle der KI Fragen über die Analyse des Videos.
                        </div>
                    )}
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <Avatar className="h-8 w-8 shrink-0">
                                {msg.role === 'assistant' || msg.role === 'system' ? (
                                    <AvatarFallback className="bg-blue-600 text-white text-xs">AI</AvatarFallback>
                                ) : (
                                    <AvatarFallback className="bg-gray-700 text-white text-xs">U</AvatarFallback>
                                )}
                            </Avatar>
                            <div className={`p-3 rounded-lg max-w-[85%] text-sm leading-relaxed whitespace-pre-wrap ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-200'
                                }`}>
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex gap-3">
                            <Avatar className="h-8 w-8 shrink-0">
                                <AvatarFallback className="bg-blue-600 text-white text-xs">AI</AvatarFallback>
                            </Avatar>
                            <div className="p-3 rounded-lg bg-gray-800 text-gray-200 flex items-center">
                                <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                            </div>
                        </div>
                    )}
                </div>
            </ScrollArea>

            <div className="p-4 border-t border-gray-800 bg-gray-950">
                <div className="flex flex-wrap gap-2 mb-3">
                    {suggestions.map((s, i) => (
                        <button
                            key={i}
                            onClick={() => handleSend(s)}
                            className="text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-full transition-colors border border-gray-700"
                        >
                            {s}
                        </button>
                    ))}
                </div>
                <div className="flex gap-2">
                    <Input
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSend()}
                        placeholder="Frag etwas zum Video..."
                        className="bg-gray-900 border-gray-700 text-white focus-visible:ring-blue-500"
                        autoComplete="off"
                        disabled={loading}
                    />
                    <Button
                        onClick={() => handleSend()}
                        size="icon"
                        className="bg-blue-600 hover:bg-blue-700 shrink-0 text-white"
                        disabled={loading || !input.trim()}
                    >
                        <Send className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}
