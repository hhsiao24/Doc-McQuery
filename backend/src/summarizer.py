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
For each field, you must always provide the **most specific information available in the text**, even if approximate or implied. 
Do not leave any field empty. If the text is vague, use a best-guess paraphrase.
Return the result as valid JSON in the following format where all variables return as a string:
{{
    "patient": {{
        "age": "e.g. '68-year-old', 'adult', 'mean age 70', or best estimate based on text",
        "gender": "male / female / mixed / not specified; use inferred information if not explicit"
    }},
    "situational_summary": [{{
        "event": "describe the main clinical case or event, e.g. 'presentation of chest pain with shortness of breath'",
        "characteristics": "notable features of the patient or condition, including comorbidities, demographics, or risk factors",
        "onset": "describe when/how the symptoms started, e.g. 'gradual onset over 2 weeks', 'acute onset after exertion'",
        "outcome": "describe the result or current status, e.g. 'full recovery', 'improvement with treatment', 'death', 'unknown'",
        "history": "summary of relevant medical history or past conditions, e.g. 'history of hypertension', 'no chronic conditions'",
        "treatment": "describe treatments/interventions, e.g. 'insulin therapy', 'laparoscopic surgery', 'physical therapy'"
    }}],
    "notes": "general context or additional observations relevant to the case, e.g. 'case study for a rare condition'"
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

    # Parsed input (structured)
    description = patient.get("parsed_input", {})
    conditions = description.get("conditions", [])
    symptoms = description.get("symptoms", [])
    treatments = description.get("treatments", [])
    demographics = description.get("demographics", {})

    # EMR summary (unstructured -> convert to tokens)
    emr_summary = patient.get("emr_summary", {})
    emr_conditions_text = emr_summary.get("conditions_summary", "")
    emr_symptoms_text = emr_summary.get("symptoms_and_observations_summary", "")

    # crude keyword extraction (split on words/phrases, could replace w/ GPT/NLP)
    emr_terms = []
    if emr_conditions_text:
        emr_terms.extend([f'"{phrase.strip()}"[All Fields]' 
                          for phrase in emr_conditions_text.split(",") if phrase.strip()])
    if emr_symptoms_text:
        emr_terms.extend([f'"{phrase.strip()}"[All Fields]' 
                          for phrase in emr_symptoms_text.split(",") if phrase.strip()])

    # Tier 1: conditions + symptoms + treatments + demographics + EMR terms
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
    if emr_terms:
        tier1_terms.append(" OR ".join(emr_terms))
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
    if emr_terms:
        tier2_terms.append(" OR ".join(emr_terms))
    if tier2_terms:
        queries.append(" AND ".join(tier2_terms))

    # Tier 3: drop treatments
    tier3_terms = []
    if conditions:
        tier3_terms.append(" OR ".join([f'"{c}"[MeSH Terms]' for c in conditions]))
    if symptoms:
        tier3_terms.append(" OR ".join([f'"{s}"[All Fields]' for s in symptoms]))
    if emr_terms:
        tier3_terms.append(" OR ".join(emr_terms))
    if tier3_terms:
        queries.append(" AND ".join(tier3_terms))

    # Tier 4: conditions + only first 1–2 symptoms + emr terms
    tier4_terms = []
    if conditions:
        tier4_terms.append(" OR ".join([f'"{c}"[MeSH Terms]' for c in conditions]))
    if symptoms:
        tier4_terms.append(" OR ".join([f'"{s}"[All Fields]' for s in symptoms[:2]]))
    if emr_terms:
        tier4_terms.append(" OR ".join(emr_terms))
    if tier4_terms:
        queries.append(" AND ".join(tier4_terms))

    return queries


