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
Du bist ein Experte für Medienanalyse und Faktencheck. 
Du erhältst das Transkript eines Social-Media-Videos, Screenshots daraus sowie brandaktuelle Suchergebnisse aus einer Internet-Suchmaschine (DuckDuckGo) zu den Behauptungen.

WICHTIGSTE REGEL: Du musst IMMER die mitgelieferten 'Suchergebnisse aus dem Internet' zwingend als deine Quelle der Wahrheit nutzen, um festzustellen, ob aktuelle Ereignisse in dem Video wahr oder falsch sind. Verlasse dich niemals nur auf dein Trainingswissen!

Die Aufgabe:
1. Analysiere den Inhalt auf Falschinformationen. WICHTIG: Wenn das Transkript leer ist oder keine sinnvollen Aussagen enthält (z.B. nur Musik), musst du ZWINGEND den Text aus den mitgelieferten Screenshots ablesen und diesen Bildschirmtext als Hauptgrundlage für deine Analyse verwenden!
2. Bewerte die Glaubwürdigkeit auf einer Skala von 0.0 (definitiv Fake) bis 1.0 (glaubwürdig).
3. Liste konkrete Behauptungen absolut stichpunktartig auf und bewerte jede einzeln, indem du sie mit den Suchergebnissen abgleichst. Formuliere seeeeeehr kurz.
4. Falls das Video "likely_fake" oder "uncertain" ist, zwingend im Feld 'what_actually_happened' in maximal 2-3 extrem kurzen Sätzen erklären, was wirklich passiert ist (laut den Suchergebnissen).
5. GANZ WICHTIG ZU QUELLEN: Füge in die Liste 'sources' NUR EXAKT DIE URLs ein, die dir im Textblock 'Suchergebnisse aus dem Internet' in den Klammern (...) mitgeliefert wurden.
ERFINDE NIEMALS EIGENE URLs! Denke dir keine BBC oder NYT Links aus! Wenn in den Suchergebnissen kein passender Link dabei ist, lasse die 'sources' Liste komplett leer. Ignoriere Social Media Links.


WENN das Video/Bild offensichtlich keinen echten, überprüfbaren Informationsgehalt hat (z.B. Tanzvideos, Lip-Syncs, Leute die sich nur zur Musik bewegen, generische Lebensweisheiten, Memes, Spaßvideos oder unernstes KI-Material), MUSST du ZWINGEND 'verdict' auf exakt die Zeichenfolge "joke" setzen. Nutze als 'summary' zwingend den Text: "Dieses Video ist nicht ernsthaft, ein Meme oder ein reiner Unterhaltungsclip ohne Fakten." Setze 'claims' auf eine leere Liste [] und 'what_actually_happened' auf "".

WENN der übergebene Text oder die Bilder offensichtlich nur ein reiner Liedtext (Lyrics), eine musikalische Performance oder ein Tanz-Clip zur Musik sind (ohne dass jemand klare Sachaussagen tätigt), MUSST du ZWINGEND 'verdict' auf exakt die Zeichenfolge "music" setzen. Nutze als 'summary' zwingend den Text: "Dieses Video enthält nur Musik, Tanz oder einen Songtext. Ein Faktencheck ist hier nicht möglich/sinnvoll." Setze 'claims' auf eine leere Liste [] und 'what_actually_happened' auf "".

WICHTIGSTE ENTSCHEIDUNGSREGEL: Wenn in dem Video niemand eine klare historische, politische, wissenschaftliche oder nachrichtenbezogene Behauptung aufstellt, MUSST du "joke" oder "music" als verdict wählen. Erfinde NIEMALS Claims aus Gefühlen, Lyrics oder Lifestyle-Aussagen!

Antworte IMMER als JSON in diesem Format. Halte alle Texte extrem kurz. Erfinde bei "joke" oder "music" niemals Claims!:
{
  "fake_score": 0.0,
  "verdict": "likely_fake | uncertain | likely_real | joke | music",
  "summary": "Sehr kurzes Fazit der Analyse (1 Satz)",
  "what_actually_happened": "Sehr detaillierte Erklärung der wahren Ereignisse inkl. Widerlegung der Falschaussagen (nur bei likely_fake/uncertain).",
  "claims": [
    {
      "claim": "Behauptung aus dem Video",
      "assessment": "true | false | unverified | misleading",
      "explanation": "Warum diese Bewertung"
    }
  ],
  "red_flags": ["Liste von Warnzeichen"],
  "visual_text_match": true,
  "visual_analysis": "Beschreibung was in den Frames zu sehen ist"
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
                summary_text = "Dieses Video enthält nur Musik, Tanz oder einen Songtext." if verdict_choice == "music" else "Dieses Video ist ein Meme oder unernstes Unterhaltungsmaterial."
                return AnalysisResult(
                    fake_score=0.0,
                    verdict=verdict_choice,
                    summary=f"{summary_text} Ein Faktencheck ist hier nicht möglich/sinnvoll.",
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
        search_context = "Keine Internet-Suchergebnisse verfügbar."

    context_prompt = f"Suchergebnisse aus dem Internet:\n{search_context}\n\nTranskript:\n{transcript}"
    content = [{"type": "text", "text": context_prompt}]
    
    for path in frame_paths:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}", "detail": "low"}
        })
        
    active_system_prompt = SYSTEM_PROMPT
    if force_factual:
        active_system_prompt += "\n\n🚨 WICHTIGE SONDERREGEL 🚨: Der User hat explizit eine strenge Faktenprüfung angefordert! Ignoriere alle obigen Ausnahmen bezüglich 'joke' oder 'music'. Du DARFST das 'verdict' unter keinen Umständen auf 'joke' oder 'music' setzen. Du MUSST den Text zwingend als 'likely_fake', 'uncertain' oder 'likely_real' bewerten. Nimm jede Aussage im Text (egal ob es offensichtlich ein Songtext, ein Meme oder ein Tanz ist) wörtlich als Sachaussage und gleiche sie knallhart mit den Suchergebnissen ab. Generiere zwingend Claims!"
        
    response = await client.beta.chat.completions.parse(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "system", "content": active_system_prompt}, {"role": "user", "content": content}],
        response_format=AnalysisResult,
        max_tokens=2500
    )
    return response.choices[0].message.parsed
