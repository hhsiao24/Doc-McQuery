# app.py
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from openai import OpenAI

import json
import os

load_dotenv()

from .src.db import Database
from .src.summarizer import search_pubmed
from .src.summarizer import get_structured_summaries
from .src.summarizer import fetch_abstract
from .src.summarizer import summarize_structured
from .src.summarizer import build_queries

app = Flask(__name__)

db = Database()
connection = db.get_connection()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def parse_user_input(raw_input):
    """
    Uses GPT to parse unstructured input into structured fields.
    """
    prompt = f"""
    You are a medical parser. Take the following doctor input and extract:
    - patient_id
    - conditions
    - symptoms
    - medications
    - treatments
    - diagnosis

    If a field is not present, leave it empty.

    Input: "{raw_input}"
    Output in JSON format.
    """
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        parsed = response.choices[0].message.content
        return parsed
    except Exception as e:
        return {"error": str(e)}
    
@app.route("/parse_input", methods=["POST"])
def parse_input():
    data = request.json
    raw_input = data.get("input")

    if not raw_input:
        return jsonify({"error": "input is required"}), 400

    structured_output = parse_user_input(raw_input)
    return jsonify({"structured_data": structured_output})

# test method to summarize pub med articles 
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    results = get_structured_summaries(query, max_results=3)
    return jsonify(results)


# use inputs to generate a query and create the summary
@app.route("/search-patient", methods=["POST"])
def search_patient():
    data = request.json
    patient = data.get("patient", {})

    if not patient:
        return jsonify({"error": "Patient data is required"}), 400

    print("Got patient", flush=True)

    queries = build_queries(patient)
    print("Built queries:", queries, flush=True)

    tier_with_results = None
    first_query = None
    ids = []

    # Step 1 — Find first tier with results without calling OpenAI
    for tier_num, query in enumerate(queries, start=1):
        print(f"Checking Tier {tier_num} query: {query}", flush=True)
        ids = search_pubmed(query, max_results=3)
        if ids:
            tier_with_results = tier_num
            first_query = query
            print(f"Tier {tier_num} has results: {ids}", flush=True)
            break  # Stop at first tier with results

    if not tier_with_results:
        return jsonify({"error": "No results found"}), 404

    # Step 2 — Call OpenAI for the first tier with results
    summaries = []
    for pubmed_id in ids:
        abstract = fetch_abstract(pubmed_id)
        structured_summary = summarize_structured(abstract)
        try:
            structured_json = json.loads(structured_summary)
        except Exception:
            structured_json = {"raw_summary": structured_summary}
        summaries.append({
            "pubmed_id": pubmed_id,
            "summary": structured_json
        })

    results = {
        f"Tier {tier_with_results}": {
            "query": first_query,
            "summaries": summaries
        }
    }

    return jsonify({
        "patient": patient,
        "results": results
    })


@app.route("/health")
def hello():
    return "The server has been eating apples 🍎!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
