import os, json, uuid
from openai import OpenAI
from fhir.resources.observation import Observation

from datetime import date

from .embeddings import (
    observation_to_string,
)

from .db import (
    Database
)

from .summarizer import (
    summarize_patient_info
)

#CHECK
db = Database()
connection = db.get_connection()


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
max_per_symptom = 5
max_patients_returned = 2


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

def patient_summary(patient_id, first_name = None, last_name = None) -> dict:
    records = get_patient_records(patient_id, first_name, last_name)
    if not records:
        return {}

    summary = summarize_patient_info(records)

    return summary


#Main Function
def find_similar_emr(patient_id: str, obs_input: str, db: Database) -> list[tuple[str, str, float]]:
    summaries = {}

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


    patient_ids = [pid for (pid, _code, _sim) in results]

    final_results = db.find_similar_patients_from_list(patient_id, patient_ids, max_patients_returned)

    for patient in final_results:
        summaries[patient[0]] = patient_summary(patient[0])

    return summaries


