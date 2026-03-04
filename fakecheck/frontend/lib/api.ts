import { VideoResponse, ChatMessage } from '@/types';

// The Nginx proxy routes /api/ to the backend on port 8000
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://lui-inventions.com').replace(/\/+$/, '');

export async function analyzeVideo(url: string): Promise<{ id: string }> {
    const res = await fetch(`${API_BASE}/api/video/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error('Failed to analyze video');
    const data = await res.json();
    // Backend returns a VideoResponse object where "id" is the ID.
    return { id: data.id };
}

export async function getVideoStatus(id: string): Promise<VideoResponse> {
    const res = await fetch(`${API_BASE}/api/video/${id}`);
    if (!res.ok) throw new Error('Failed to fetch video status');
    return res.json();
}

export async function getVideoFrames(id: string): Promise<{ frames: string[] }> {
    const res = await fetch(`${API_BASE}/api/video/${id}/frames`);
    if (!res.ok) throw new Error('Failed to fetch video frames');
    return res.json();
}

export async function sendChatMessage(videoId: string, message: string): Promise<{ reply: string }> {
    const res = await fetch(`${API_BASE}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId, message }),
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
}

export async function getChatHistory(videoId: string): Promise<{ history: ChatMessage[] }> {
    const res = await fetch(`${API_BASE}/api/chat/${videoId}/history`);
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
}
