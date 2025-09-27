import json
import os
import xml.etree.ElementTree as ET

import requests
from Bio import Entrez
from openai import OpenAI

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
    print(resp.text, flush=True)
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


# generates summaries based on pub med articles found from queries
def get_structured_summaries(query, max_results=3):
    ids = search_pubmed(query, max_results=max_results)
    if not ids:
        return {"error": "No results found"}

    print("Got ids", ids, flush=True)

    results = []
    for pid in ids:
        abstract = fetch_abstract(pid)
        print("Got abstract", flush=True)
        structured_summary = summarize_structured(abstract)
        print("Got summary", flush=True)
        try:
            structured_json = json.loads(structured_summary)
        except:
            structured_json = {"raw_summary": structured_summary}

        results.append({"pubmed_id": pid, "summary": structured_json})
    return results


def conditions_to_string(conditions):
    """
    Convert a list of condition dicts into a readable string.
    """
    if not conditions:
        return "No known conditions."

    def conditions_to_string(conditions):
        if not conditions:
            return "No known conditions."
        parts = []
        for c in conditions:
            s = c["code"]
            if c.get("onset"):
                s += f" (onset: {c['onset']})"
            if c.get("abatement"):
                s += f", resolved: {c['abatement']}"
            parts.append(s)
        return "; ".join(parts)


def observations_to_string(observations):
    if not observations:
        return "No past observations recorded."
    parts = []
    for o in observations:
        s = o["code"]
        if o.get("value") is not None:
            s += f": {o['value']}"
            if o.get("unit"):
                s += f" {o['unit']}"
        if o.get("date"):
            s += f" (date: {o['date']})"
        parts.append(s)
    return "; ".join(parts)


def summarize_patient_info(patient_records):
    conditions_text = conditions_to_string(patient_records["conditions"])

    # Take the 10 most recent observations
    recent_obs = sorted(
        patient_records["observations"], key=lambda x: x.get("date") or "", reverse=True
    )[:10]

    # Collapse observations into a concise string
    obs_summary_list = []
    for o in recent_obs:
        s = o["code"]
        if o.get("value"):
            s += f": {o['value']}"
        obs_summary_list.append(s)

    observations_text = "; ".join(obs_summary_list)
    if len(obs_summary_list) > 10:
        observations_text += "; ... (and more)"

    # Patient info
    gender = patient_records.get("gender", "unknown")
    age = patient_records.get("age", "unknown")

    # GPT prompt
    prompt = f"""
You are a medical summarizer.
Summarize the following patient information into a structured JSON format. 
Focus only on **key, clinically important details (I don't need specific values)**. The summary must be **concise**:
- Conditions summary: 1-2 sentences maximum
- Symptoms and observations summary: no more than 3 sentences
Do not include every observation or minor detail.

{{
    "patient": {{
        "age": "{age}",
        "gender": "{gender}"
    }},
    "conditions_summary": "...",
    "symptoms_and_observations_summary": "..."
}}

Patient conditions:
{conditions_text}

Patient past observations:
{observations_text}
"""

    # Call GPT
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse JSON safely
    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"raw_summary": response.choices[0].message.content}


# building the queries to parse pubmed
Entrez.email = "your_email@example.com"


# MeSH = Medical Subject Headings -> Searching with [MeSH Terms] means PubMed will look for articles specifically tagged with that subject heading
# [All Fields] tells PubMed to search for the term anywhere in the record: title, abstract, keywords, authors, etc
def build_queries(patient):
    queries = []

    conditions = patient.get("conditions", [])
    symptoms = patient.get("symptoms", [])
    treatments = patient.get("treatments", [])
    demographics = patient.get("demographics", {})

    # Tier 1: conditions + symptoms + treatments + demographics
    tier1_terms = []
    if conditions:
        tier1_terms.append(" OR ".join([f'"{c}"[MeSH Terms]' for c in conditions]))
    if symptoms:
        tier1_terms.append(" OR ".join([f'"{s}"[All Fields]' for s in symptoms]))
    if treatments:
        tier1_terms.append(" OR ".join([f'"{t}"[All Fields]' for t in treatments]))
    if "age" in demographics:
        age = demographics["age"]
        lower = age - 10
        upper = age + 10
        tier1_terms.append(f'"aged {lower}-{upper}"')
    if "sex" in demographics:
        tier1_terms.append(f'"{demographics["sex"]}"')
    if tier1_terms:
        queries.append(" AND ".join(tier1_terms))

    # Tier 2: drop demographics
    tier2_terms = []
    if conditions:
        tier2_terms.append(" OR ".join([f'"{c}"[MeSH Terms]' for c in conditions]))
    if symptoms:
        tier2_terms.append(" OR ".join([f'"{s}"[All Fields]' for s in symptoms]))
    if treatments:
        tier2_terms.append(" OR ".join([f'"{t}"[All Fields]' for t in treatments]))
    if tier2_terms:
        queries.append(" AND ".join(tier2_terms))

    # Tier 3: drop treatments
    tier3_terms = []
    if conditions:
        tier3_terms.append(" OR ".join([f'"{c}"[MeSH Terms]' for c in conditions]))
    if symptoms:
        tier3_terms.append(" OR ".join([f'"{s}"[All Fields]' for s in symptoms]))
    if tier3_terms:
        queries.append(" AND ".join(tier3_terms))

    # Tier 4: conditions + only first 1 or 2 symptoms
    tier4_terms = []
    if conditions:
        tier4_terms.append(" OR ".join([f'"{c}"[MeSH Terms]' for c in conditions]))
    if symptoms:
        tier4_terms.append(" OR ".join([f'"{s}"[All Fields]' for s in symptoms[:2]]))
    if tier4_terms:
        queries.append(" AND ".join(tier4_terms))

    return queries
