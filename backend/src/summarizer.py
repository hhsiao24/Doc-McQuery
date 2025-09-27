import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def search_pubmed(query, max_results=3):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
    search_resp = requests.get(search_url, params=params).json()
    return search_resp["esearchresult"].get("idlist", [])

def fetch_abstract(pubmed_id):
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": pubmed_id, "retmode": "xml"}
    resp = requests.get(efetch_url, params=params)
    root = ET.fromstring(resp.text)
    abstract = ""
    for elem in root.iter("AbstractText"):
        abstract += (elem.text or "") + " "
    return abstract.strip()

def summarize_structured(abstract):
    prompt = f"""
You are a medical data extractor.
Extract patient info, conditions, symptoms, treatments, results, and diagnosis from the following abstract.
Return the result as valid JSON in the following format where all variables return as a string: 

{{
    "patient": {{
        "age": age,
        "gender": gender
    }},
    "situational_summary": [{{
        "event": event, 
        "characteristics": characteristics,
        "onset": onset,
        "outcome": outcome,
        "history": history,
        "treatment": treatment,
    }}],
    "notes": notes,
}}

Abstract:
\"\"\"{abstract}\"\"\"
"""
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def get_structured_summaries(query, max_results=3):
    ids = search_pubmed(query, max_results=max_results)
    if not ids:
        return {"error": "No results found"}

    results = []
    for pid in ids:
        abstract = fetch_abstract(pid)
        structured_summary = summarize_structured(abstract)
        try:
            structured_json = json.loads(structured_summary)
        except:
            structured_json = {"raw_summary": structured_summary}

        results.append({
            "pubmed_id": pid,
            "summary": structured_json
        })
    return results
