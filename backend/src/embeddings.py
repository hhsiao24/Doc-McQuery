from fhirclient.models.observation import Observation
from fhirclient.models.patient import Patient
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_patient_embedding(patient: Patient) -> list[float]:
    """Generate embedding for patient demographic data"""
    patient_text_parts = []

    # Basic info
    if patient.gender:
        patient_text_parts.append(f"Gender: {patient.gender}")

    if patient.birthDate:
        patient_text_parts.append(f"Birth date: {patient.birthDate}")

    if hasattr(patient, "deceasedBoolean") and patient.deceasedBoolean is not None:
        status = "deceased" if patient.deceasedBoolean else "alive"
        patient_text_parts.append(f"Status: {status}")

    # Name
    if patient.name:
        names = []
        for n in patient.name:
            full_name = (
                " ".join(n.prefix or [])
                + " "
                + " ".join(n.given or [])
                + " "
                + (n.family or "")
            )
            names.append(full_name.strip())
        patient_text_parts.append(f"Name(s): {', '.join(names)}")

    # Race and Ethnicity
    if patient.extension:
        for ext in patient.extension:
            if "race" in ext.url.lower():
                text = next(
                    (e.valueString for e in ext.extension if hasattr(e, "valueString")),
                    None,
                )
                if text:
                    patient_text_parts.append(f"Race: {text}")
            if "ethnicity" in ext.url.lower():
                text = next(
                    (e.valueString for e in ext.extension if hasattr(e, "valueString")),
                    None,
                )
                if text:
                    patient_text_parts.append(f"Ethnicity: {text}")
            if "birthsex" in ext.url.lower():
                if hasattr(ext, "valueCode"):
                    patient_text_parts.append(f"Birth sex: {ext.valueCode}")
            if "birthplace" in ext.url.lower() and hasattr(ext, "valueAddress"):
                addr = ext.valueAddress
                parts = [addr.city, addr.state, addr.country]
                patient_text_parts.append(
                    f"Birthplace: {', '.join(filter(None, parts))}"
                )

    # Marital status
    if hasattr(patient, "maritalStatus") and patient.maritalStatus:
        text = getattr(patient.maritalStatus, "text", None)
        if text:
            patient_text_parts.append(f"Marital status: {text}")

    # Multiple birth
    if (
        hasattr(patient, "multipleBirthBoolean")
        and patient.multipleBirthBoolean is not None
    ):
        patient_text_parts.append(f"Multiple birth: {patient.multipleBirthBoolean}")

    # Communication / languages
    if hasattr(patient, "communication") and patient.communication:
        languages = [
            c.language.text
            for c in patient.communication
            if hasattr(c.language, "text")
        ]
        if languages:
            patient_text_parts.append(f"Languages: {', '.join(languages)}")

    # Combine all patient information
    patient_text = (
        " | ".join(patient_text_parts) if patient_text_parts else "Unknown patient"
    )

    # Generate embedding
    embedding = embedding_model.encode(patient_text)
    return embedding.tolist()


def generate_observation_embedding(observation: Observation) -> list[float]:
    """Generate embedding for observation data"""
    obs_text = observation_to_string(observation)

    # Generate embedding
    embedding = embedding_model.encode(obs_text)
    return embedding.tolist()

def observation_to_string(observation: Observation) -> str:
    """Converts an Observation data type into a string"""
    # Create a text representation of observation data
    obs_text_parts = []

    if observation.code and observation.code.text:
        obs_text_parts.append(f"Observation: {observation.code.text}")

    # Handle different value types
    if hasattr(observation, "valueQuantity") and observation.valueQuantity:
        value = getattr(observation.valueQuantity, "value", None)
        unit = getattr(observation.valueQuantity, "unit", None)
        if value is not None:
            value_text = f"Value: {value}"
            if unit:
                value_text += f" {unit}"
            obs_text_parts.append(value_text)
    elif hasattr(observation, "valueString") and observation.valueString:
        obs_text_parts.append(f"Value: {observation.valueString}")
    elif hasattr(observation, "valueBoolean") and observation.valueBoolean is not None:
        obs_text_parts.append(f"Value: {observation.valueBoolean}")

    if hasattr(observation, "effectiveDateTime") and observation.effectiveDateTime:
        obs_text_parts.append(f"Date: {observation.effectiveDateTime}")

    # Combine all observation information
    obs_text = " | ".join(obs_text_parts) if obs_text_parts else "Unknown observation"
    return obs_text
