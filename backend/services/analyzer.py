import base64
import json
import logging
from openai import AsyncOpenAI
from models.schemas import AnalysisResult
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an expert in media analysis and fact-checking.
You receive the transcript of a social media video, screenshots from it, and the latest search results from an internet search engine (DuckDuckGo) regarding the claims.

MOST IMPORTANT RULE: You MUST always use the provided 'Search results from the internet' as your absolute source of truth to determine if current events in the video are true or false. Never rely solely on your training knowledge!

The task:
1. Analyze the content for misinformation. IMPORTANT: If the transcript is empty or contains no meaningful statements (e.g., only music), you MUST read the text from the provided screenshots and use this screen text as the primary basis for your analysis!
2. Rate the credibility on a scale from 0.0 (definitely fake) to 1.0 (credible).
3. List specific claims in a strictly bulleted format and evaluate each one individually by cross-referencing with the search results. Keep descriptions very short.
4. If the video is "likely_fake" or "uncertain", you must explain what actually happened in the 'what_actually_happened' field in a maximum of 2-3 extremely short sentences (according to the search results).
5. VERY IMPORTANT REGARDING SOURCES: Only include the EXACT URLs that were provided to you in the 'Search results from the internet' block within the parentheses (...).
NEVER INVENT YOUR OWN URLs! Do not make up BBC or NYT links! If no suitable link is found in the search results, leave the 'sources' list completely empty. Ignore social media links.


IF the video/image obviously has no real, verifiable informational content (e.g., dance videos, lip-syncs, people just moving to music, generic life wisdom, memes, fun videos, or non-serious AI material), you MUST set 'verdict' to exactly the string "joke". Use the text: "This video is not serious, it is a meme or pure entertainment material without facts." as the 'summary'. Set 'claims' to an empty list [] and 'what_actually_happened' to "".

IF the provided text or images are obviously just song lyrics, a musical performance, or a dance clip to music (without anyone making clear factual statements), you MUST set 'verdict' to exactly the string "music". Use the text: "This video contains only music, dance, or song lyrics. A fact-check is not possible/meaningful here." as the 'summary'. Set 'claims' to an empty list [] and 'what_actually_happened' to "".

MOST IMPORTANT DECISION RULE: If no one in the video makes a clear historical, political, scientific, or news-related claim, you MUST choose "joke" or "music" as the verdict. NEVER invent claims from feelings, lifestyle-statements or music lyrics!

ALWAYS respond as JSON in this format. Keep all texts extremely short. Never invent claims for "joke" or "music"!:
{
  "fake_score": 0.0,
  "verdict": "likely_fake | uncertain | likely_real | joke | music",
  "summary": "Very short conclusion of the analysis (1 sentence)",
  "what_actually_happened": "Explanation of the true events including refutation of false statements (only for likely_fake/uncertain).",
  "claims": [
    {
      "claim": "Claim from the video",
      "assessment": "true | false | unverified | misleading",
      "explanation": "Why this rating"
    }
  ],
  "red_flags": ["List of warning signs"],
  "visual_text_match": true,
  "visual_analysis": "Description of what is visible in the frames"
}
"""

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def analyze_video(transcript: str, frame_paths: list[str], force_factual: bool = False) -> AnalysisResult:
    if settings.MOCK_MODE:
        logger.info("[MOCK_MODE] Returning dummy analysis result")
        return AnalysisResult(
            fake_score=0.1,
            verdict="likely_fake",
            summary="MOCK: This video is filled with falsehoods.",
            claims=[
                {"claim": "The earth is flat", "assessment": "false", "explanation": "Scientific consensus."}
            ],
            sources=["https://wikipedia.org/wiki/Earth"],
            red_flags=["emotional language", "no sources"],
            visual_text_match=False,
            visual_analysis="MOCK: The video shows unrelated space imagery."
        )

    # Pre-check circuitry for joke/music without searching
    if not force_factual:
        try:
            pre_content = [{"type": "text", "text": f"Classify this social media post. If it contains ONLY song lyrics, music descriptions like [Music], or if it clearly lacks verifiable factual claims (like dance videos, memes, jokes, lifestyle vibes, lip-syncs), reply with 'music' or 'joke'. Otherwise, reply with 'factual'. Transcript:\n{transcript}"}]
            
            if len(transcript.strip()) < 50 and frame_paths:
                pre_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(frame_paths[0])}", "detail": "low"}})
                
            pre_check = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a fast classifier. Reply ONLY with the exact word 'music', 'joke', or 'factual'."},
                    {"role": "user", "content": pre_content}
                ],
                max_tokens=10
            )
            classification = pre_check.choices[0].message.content.strip().lower()
            logger.info(f"Pre-check classification: {classification}")
            
            if "music" in classification or "joke" in classification:
                verdict_choice = "music" if "music" in classification else "joke"
                summary_text = "This video contains only music, dance, or song lyrics." if verdict_choice == "music" else "This video is a meme or non-serious entertainment material."
                return AnalysisResult(
                    fake_score=0.0,
                    verdict=verdict_choice,
                    summary=f"{summary_text} A fact-check is not possible/meaningful here.",
                    what_actually_happened="",
                    claims=[],
                    sources=[],
                    red_flags=["irrelevant content detected in pre-check"],
                    visual_text_match=False,
                    visual_analysis="Skipped due to pre-check"
                )
        except Exception as e:
            logger.warning(f"Pre-check failed, continuing to full analysis: {e}")
    else:
        logger.info("force_factual=True: Skipping pre-check classification.")

    # Use LLM to generate search queries from transcript
    try:
        from duckduckgo_search import DDGS
        import asyncio
        search_query_response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{
                "role": "system", 
                "content": "Generate up to 5 brief keyword search queries to fact-check distinct claims in this text (e.g. names, events, locations). Return ONLY a JSON object with a 'queries' list of strings."
            }, {"role": "user", "content": transcript}],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        queries_dict = json.loads(search_query_response.choices[0].message.content)
        search_queries = queries_dict.get("queries", [])[:5]
        
        # Fallback if the LLM generated 0 queries (e.g. very short transcript)
        if not search_queries and len(transcript.strip()) > 5:
            logger.info("GPT returned empty queries, defaulting to transcript start.")
            # Use the first 80 characters realistically as a fallback search
            search_queries = [transcript[:80].replace('\n', ' ')]
            
        logger.info(f"Using web search queries: {search_queries}")
        
        def run_searches(queries):
            results = []
            with DDGS() as ddgs:
                for q in queries:
                    try:
                        # fetch top 3 general web results
                        res_text = list(ddgs.text(q, safesearch='off', max_results=3))
                        results.extend(res_text)
                    except Exception as e:
                        logger.warning(f"DDGS text search err for '{q}': {e}")
                    
                    try:
                        # fetch top 3 breaking news results globally
                        res_news = list(ddgs.news(q, safesearch='off', max_results=3))
                        results.extend(res_news)
                    except Exception as e:
                        logger.warning(f"DDGS news search err for '{q}': {e}")
                        
                # 2. RapidAPI News API (news-api14)
                import requests
                for q in queries:
                    try:
                        url = "https://news-api14.p.rapidapi.com/v2/search/articles"
                        querystring = {"query": q, "language": "en"}
                        headers = {
                            "x-rapidapi-host": "news-api14.p.rapidapi.com",
                            "x-rapidapi-key": settings.RAPIDAPI_KEY
                        }
                        res = requests.get(url, headers=headers, params=querystring, timeout=10)
                        if res.status_code == 200:
                            data = res.json()
                            if data.get("success") and "data" in data:
                                # Fetch top 3 results from News API
                                for item in data["data"][:3]:
                                    results.append({
                                        "title": item.get("title", ""),
                                        "url": item.get("url", ""),
                                        "body": item.get("excerpt", "")
                                    })
                        else:
                            logger.warning(f"News API returned {res.status_code} for '{q}'")
                    except Exception as e:
                        logger.warning(f"News API err for '{q}': {e}")
                            
            return results

        search_results = await asyncio.to_thread(run_searches, search_queries)
        
        # Deduplicate
        unique_results = []
        seen_urls = set()
        for r in search_results:
            # text results use 'href', news results use 'url'
            url = r.get('href') or r.get('url') or ''
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)
                
        search_context = "\n".join([f"- [{res.get('title', '')}]({res.get('href') or res.get('url')}): {res.get('body', '')}" for res in unique_results])
    except Exception as e:
        logger.error(f"Failed to fetch search results: {e}")
        search_context = "No internet search results available."

    context_prompt = f"Search results from the internet:\n{search_context}\n\nTranscript:\n{transcript}"
    content = [{"type": "text", "text": context_prompt}]
    
    for path in frame_paths:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}", "detail": "low"}
        })
        
    active_system_prompt = SYSTEM_PROMPT
    if force_factual:
        active_system_prompt += "\n\n🚨 IMPORTANT SPECIAL RULE 🚨: The user has explicitly requested a strict fact-check! Ignore all the above exceptions regarding 'joke' or 'music'. You MUST NOT set the 'verdict' to 'joke' or 'music' under any circumstances. You MUST evaluate the text as 'likely_fake', 'uncertain', or 'likely_real'. Treat every statement in the text (regardless of whether it is obviously song lyrics, a meme, or a dance) literally as a factual statement and cross-check it rigorously with the search results. You MUST generate claims!"
        
    response = await client.beta.chat.completions.parse(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "system", "content": active_system_prompt}, {"role": "user", "content": content}],
        response_format=AnalysisResult,
        max_tokens=2500
    )
    return response.choices[0].message.parsed
