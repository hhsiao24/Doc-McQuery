import json

from config.db import DbInitializer
from fhir.resources.bundle import Bundle
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from pydantic import create_model

db = DbInitializer()
connection = db.get_connection()


Bundle.model_config["extra"] = "ignore"


def process_file(file: str):
    with open(file) as f:
        bundle_json = json.load(f)

    bundle = Bundle(**bundle_json)

    for entry in bundle.entry:
        resource = entry.resource
        if resource.resource_type == "Patient":
            # Access Patient fields as attributes
            patient_id = resource.id
            first_name = resource.name[0].given[0]
            last_name = resource.name[0].family
            gender = resource.gender
            birth_date = resource.birthDate
            # store in DB
        elif resource.resource_type == "Observation":
            obs_id = resource.id
            patient_ref = resource.subject.reference.split("/")[
                -1
            ]  # still need to resolve manually
            code = resource.code.text
            value = resource.valueQuantity.value if resource.valueQuantity else None
            date = resource.effectiveDateTime
            # store in DB


def main():
    process_file(
        "output/fhir/Aaron697_Kunde533_2d2d790d-4ec3-e383-e483-66df15fe87c5.json"
    )


if __name__ == "__main__":
    main()
