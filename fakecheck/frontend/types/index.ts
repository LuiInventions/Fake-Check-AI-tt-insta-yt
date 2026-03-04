export interface VideoResponse {
    id: string;
    status: string;
    url: string;
    platform?: string;
    title?: string;
    analysis_result?: AnalysisResult;
    error_message?: string;
    frames_paths?: string[];
}

export interface ClaimAssessment {
    claim: string;
    assessment: 'true' | 'false' | 'unverified' | 'misleading';
    explanation: string;
}

export interface AnalysisResult {
    fake_score: number; // 0.0 to 1.0 (0=fake, 1=real)
    verdict: 'likely_fake' | 'uncertain' | 'likely_real';
    summary: string;
    claims: ClaimAssessment[];
    red_flags: string[];
    visual_text_match: boolean;
    visual_analysis: string;
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    created_at?: string;
}
