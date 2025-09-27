# app.py
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from openai import OpenAI

import os

load_dotenv()

from .config.db import DbInitializer
from .src.summarizer import search_pubmed
from .src.summarizer import get_structured_summaries
from .src.summarizer import fetch_abstract
from .src.summarizer import summarize_structured

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

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    results = get_structured_summaries(query, max_results=3)
    return jsonify(results)


@app.route("/parse_input", methods=["POST"])
def parse_input():
    data = request.json
    raw_input = data.get("input")

    if not raw_input:
        return jsonify({"error": "input is required"}), 400

    structured_output = parse_user_input(raw_input)
    return jsonify({"structured_data": structured_output})



@app.route("/health")
def hello():
    return "The server has been eating apples 🍎!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
