from duckduckgo_search import DDGS
import json

queries = ['Joseph James DeAngelo arrest BBC', 'Joseph DeAngelo ABC News']
results = []
try:
    with DDGS() as ddgs:
        for q in queries:
            results.extend(list(ddgs.text(q, safesearch='off', max_results=3)))
    print(json.dumps(results, indent=2))
except Exception as e:
    print('ERROR:', e)
