import os, json, uuid
from openai import OpenAI
from fhir.resources.observation import Observation

from .embeddings import (
    observation_to_string,
)

from .db import (
    Database
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
max_per_symptom = 5
max_patients_returned = 5

def text_to_observation(text: str) -> Observation:
    """
    Convert clinical free text into a minimal FHIR R4 Observation via LLM,
    then coerce into a typed Observation object.
    """
    schema = """
    Return ONLY a single JSON object with these fields (no prose):

    {
    "resourceType": "Observation",
    "status": "final",
    "code": { "text": "<short description>" },
    "effectiveDateTime": "<ISO-8601>",               // optional
    "valueQuantity": { "value": <number>, "unit": "<UCUM>" }  // prefer when numeric present
    OR
    "valueString": "<string>"
    OR
    "valueBoolean": true/false
    }
    Rules:
    - resourceType MUST be "Observation".
    - status MUST be "final".
    - Prefer valueQuantity when a number+unit is present; else valueString; else valueBoolean.
    - No extra fields.
    """

    prompt = f"""Convert the following clinical note into an FHIR R4 Observation.

    Free text:
    \"\"\"{text}\"\"\"

    {schema}
    """

    resp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.choices[0].message.content.strip()

    # Robust JSON extraction (handles stray prose/backticks)
    try:
        data = json.loads(raw)
    except Exception:
        i, j = raw.find("{"), raw.rfind("}")
        if i != -1 and j != -1 and j > i:
            data = json.loads(raw[i:j+1])
        else:
            raise ValueError(f"LLM did not return valid JSON:\n{raw}")

    # Harden minimal fields & defaults
    data.setdefault("resourceType", "Observation")
    data.setdefault("status", "final")
    if not isinstance(data.get("code"), dict) or not data["code"].get("text"):
        data["code"] = {"text": "Clinical observation"}
    if not any(k in data for k in ("valueQuantity", "valueString", "valueBoolean")):
        data["valueString"] = data["code"]["text"]
    data.setdefault("id", str(uuid.uuid4()))

    # Return a typed FHIR Observation (raises if invalid)
    return Observation(**data)

def split_symptoms(input:str) -> list[str]:
    prompt = f"""
    You are a clinical text segmenter.

    TASK:
    Split the INPUT into a list of individual symptom phrases.

    RULES:
    - Preserve the original wording
    - Do NOT add or remove information. Do NOT add synonyms.
    - Keep negations with the symptom (e.g., "no fever" stays as one item).
    - If the input begins with a leading verb like "has", "has a", "reports", etc., and it directly attaches to the first symptom, include it in the first item (e.g., "has bloody urine").
    - Consider separators such as commas, semicolons, slashes, pipes, line breaks, and coordinator words like "and", "with". If none are present, infer minimal, natural symptom phrase boundaries.
    - Output MUST be ONLY a valid JSON array of strings (no prose, no markdown, no trailing commas).

    INPUT:
    \"\"\"{input}\"\"\"
    """

    resp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.choices[0].message.content.strip()

    # Expect a pure JSON array (e.g., ["has bloody urine", "headaches", "diharrea", "anxiety", "cancer"])
    return json.loads(text)


def find_similar_emr(patient_id: str, obs_input: str, db: Database) -> list[tuple[str, str, float]]:
    #creates string list of each symptom described
    symptoms = split_symptoms(obs_input)

    #stores list of 3 element tuples [patient_id, code, similarity]
    results = []

    #store top patients
    final_results = []

    #for each symptom we add most similar patients to results
    for symptom in symptoms:
        obs = text_to_observation(symptom)
        obs_text = observation_to_string(obs)

        #Adds max_per_symptom more patients
        results = results + db.find_similar_observations(obs_text, max_per_symptom)

    # patient_ids: list[str] = [
    #     item[0]                   # patient_id
    #     for result in results
    #     for item in result
    # ]

    patient_ids = [pid for (pid, _code, _sim) in results]

    final_results = db.find_similar_patients_from_list(patient_id, patient_ids, max_patients_returned)

    return final_results


