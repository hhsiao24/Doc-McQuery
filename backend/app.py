# app.py
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from openai import OpenAI

import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI

load_dotenv()

from datetime import date

from .src.db import Database
from .src.summarizer import (
    build_queries,
    fetch_abstract,
    get_structured_summaries,
    search_pubmed,
    summarize_patient_info,
    summarize_structured,
)

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


@app.route("/all_requests", methods=["POST"])
def all_requests():
    """
    Main request to get all data
    """
    data = request.json
    patient_id = data.get("patient_id")
    patient_info = data.get("patient_info")

    patient_info = parse_input(patient_info)

    # add valerias data

    # ritika's stuff

    case_study = search_patient(patient_info)

    return jsonify({"case_study": case_study})


@app.route("/parse_input", methods=["POST"])
def parse_input_route():
    data = request.json
    raw_input = data.get("input")
    return parse_input(raw_input)


def parse_input(raw_input: str):
    if not raw_input:
        return jsonify({"error": "input is required"}), 400

    structured_output = json.loads(parse_user_input(raw_input))
    return structured_output


# test method to summarize pub med articles
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    results = get_structured_summaries(query, max_results=3)
    return jsonify(results)


# @app.route("/search-patient", methods=["POST"])
# def search_patient_request():
#     data = request.json
#     patient = data.get("patient", {})
#     return search_patient(patient)


# use inputs to generate a query and call methods to create the summary
def search_patient(patient):
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
        summaries.append({"pubmed_id": pubmed_id, "summary": structured_json})

    results = {
        f"Tier {tier_with_results}": {"query": first_query, "summaries": summaries}
    }

    return {"patient": patient, "results": results}


def get_patient_records(patient_id, first_name=None, last_name=None):
    cursor = connection.cursor()

    # Base query (patient_id required)
    query = "SELECT id, first_name, last_name, gender, birth_date, deceased FROM patients WHERE id = %s"
    params = [patient_id]

    if first_name:
        query += " AND first_name = %s"
        params.append(first_name)
    if last_name:
        query += " AND last_name = %s"
        params.append(last_name)

    cursor.execute(query, tuple(params))
    patient = cursor.fetchone()
    if not patient:
        return None

    # Calculate age
    birth_date = patient[4]
    age = None
    if birth_date:
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

    # Fetch conditions
    cursor.execute(
        "SELECT id, code, onset, abatement FROM conditions WHERE patient_id = %s",
        (patient_id,),
    )
    conditions = cursor.fetchall()
    conditions_list = [
        {
            "id": str(c[0]),
            "code": str(c[1]),
            "onset": str(c[2]) if c[2] else None,
            "abatement": str(c[3]) if c[3] else None,
        }
        for c in conditions
    ]

    # Fetch observations
    cursor.execute(
        "SELECT id, code, value, unit, date FROM observations WHERE patient_id = %s",
        (patient_id,),
    )
    observations = cursor.fetchall()
    observations_list = [
        {
            "id": str(o[0]),
            "code": str(o[1]),
            "value": str(o[2]) if o[2] is not None else None,
            "unit": str(o[3]) if o[3] is not None else None,
            "date": str(o[4]) if o[4] else None,
        }
        for o in observations
    ]

    return {
        "id": str(patient[0]),
        "first_name": str(patient[1]),
        "last_name": str(patient[2]),
        "gender": str(patient[3]) if patient[3] else "unknown",
        "age": age,
        "deceased": patient[5],
        "conditions": conditions_list,
        "observations": observations_list,
    }


@app.route("/patient_summary/<patient_id>", methods=["GET"])
def patient_summary(patient_id):
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")

    records = get_patient_records(patient_id, first_name, last_name)
    if not records:
        return jsonify({"error": "Patient not found"}), 404

    summary = summarize_patient_info(records)

    return jsonify(
        {
            # "patient_records": records,
            "summary": summary
        }
    )


@app.route("/health")
def hello():
    return "The server has been eating apples 🍎!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
