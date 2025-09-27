import os
from typing import Final, Optional

import psycopg2
from fhirclient.models.condition import Condition
from fhirclient.models.fhirdatetime import FHIRDateTime
from fhirclient.models.observation import Observation
from fhirclient.models.patient import Patient

from .embeddings import (
    embedding_model,
    generate_observation_embedding,
    generate_patient_embedding,
)


def extract_patient_id(reference: str | None) -> Optional[str]:
    """Extract patient ID from various reference formats"""
    if not reference:
        return None

    # Handle urn:uuid: format
    if reference.startswith("urn:uuid:"):
        return reference.replace("urn:uuid:", "")

    # Handle Patient/id format
    if "/" in reference:
        return reference.split("/")[-1]

    # Return as-is if it's already just an ID
    return reference


class Database:
    def __init__(
        self,
        dbname: str | None = None,
        user: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: int | None = None,
    ):
        # Use environment variables if provided, otherwise fallback
        self.dbname: Final[str] = dbname or os.environ.get("DB_NAME", "data")
        self.user: Final[str] = user or os.environ.get("DB_USERNAME", "username")
        self.password: Final[str] = password or os.environ.get(
            "DB_PASSWORD", "password"
        )
        self.host: Final[str] = host or os.environ.get("DB_HOST", "localhost")
        self.port: Final[int] = port or int(os.environ.get("DB_PORT", 5432))

        # Create db connection
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.cursor = self.connection.cursor()

        # Initialize tables if not exists
        self.init_tables()

    def __del__(self):
        self.cursor.close()

    def init_tables(self):
        """Create the necessary tables with pgvector support"""
        # Enable pgvector extension
        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create patients table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id VARCHAR PRIMARY KEY,
                first_name VARCHAR,
                last_name VARCHAR,
                gender VARCHAR,
                birth_date DATE,
                deceased BOOLEAN,
                embedding vector(384),  -- 384 dimensions for all-MiniLM-L6-v2
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )

        # Create observations table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                id VARCHAR PRIMARY KEY,
                patient_id VARCHAR,
                code TEXT,
                value FLOAT,
                unit VARCHAR,
                date TIMESTAMP,
                embedding vector(384),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );
        """
        )

        # Create conditions table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conditions (
                id VARCHAR PRIMARY KEY,
                patient_id VARCHAR,
                code TEXT,
                onset TIMESTAMP,
                abatement TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );
        """
        )

        self.commit_connection()

    def get_connection(self):
        return self.connection

    def commit_connection(self):
        self.connection.commit()

    def rollback_commit(self):
        self.connection.rollback()

    def save_patient(self, patient: Patient) -> bool:
        """Save patient data to database with embedding"""
        try:
            patient_id = patient.id
            first_name = (
                patient.name[0].given[0]
                if patient.name and patient.name[0].given
                else ""
            )
            last_name = (
                patient.name[0].family
                if patient.name and patient.name[0].family
                else ""
            )
            gender = patient.gender
            birth_date = patient.birthDate.isostring if patient.birthDate else None
            deceased = getattr(patient, "deceasedBoolean", None)

            # Generate embedding
            embedding = generate_patient_embedding(patient)

            self.cursor.execute(
                """
                INSERT INTO patients (id, first_name, last_name, gender, birth_date, deceased, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    gender = EXCLUDED.gender,
                    birth_date = EXCLUDED.birth_date,
                    deceased = EXCLUDED.deceased,
                    embedding = EXCLUDED.embedding
                """,
                (
                    patient_id,
                    first_name,
                    last_name,
                    gender,
                    birth_date,
                    deceased,
                    embedding,
                ),
            )
            return True
        except Exception as e:
            print(f"Error saving patient {patient.id}: {e}")
            return False

    def save_observation(self, observation: Observation) -> bool:
        """Save observation data to database with embedding"""
        try:
            obs_id = observation.id
            patient_ref = extract_patient_id(
                observation.subject.reference.split("/")[-1]
                if observation.subject and observation.subject.reference
                else None
            )
            code = observation.code.text if observation.code else None

            # Handle different value types
            value = None
            unit = None
            if hasattr(observation, "valueQuantity") and observation.valueQuantity:
                value = getattr(observation.valueQuantity, "value", None)
                unit = getattr(observation.valueQuantity, "unit", None)

            fhirDate: FHIRDateTime | None = getattr(
                observation, "effectiveDateTime", None
            )
            date: str | None = (
                fhirDate.isostring if isinstance(fhirDate, FHIRDateTime) else None
            )

            # Generate embedding
            embedding = generate_observation_embedding(observation)

            self.cursor.execute(
                """
                INSERT INTO observations (id, patient_id, code, value, unit, date, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    patient_id = EXCLUDED.patient_id,
                    code = EXCLUDED.code,
                    value = EXCLUDED.value,
                    unit = EXCLUDED.unit,
                    date = EXCLUDED.date,
                    embedding = EXCLUDED.embedding
                """,
                (obs_id, patient_ref, code, value, unit, date, embedding),
            )

            return True
        except Exception as e:
            print(f"Error saving observation {observation.id}: {e}")
            return False

    def save_condition(self, condition: Condition) -> bool:
        """Save condition data to database"""
        try:
            cond_id = condition.id
            patient_ref = extract_patient_id(
                condition.subject.reference.split("/")[-1]
                if condition.subject and condition.subject.reference
                else None
            )
            code = condition.code.text if condition.code else None
            onset_fhir: FHIRDateTime | None = getattr(condition, "onsetDateTime", None)
            onset = (
                onset_fhir.isostring if isinstance(onset_fhir, FHIRDateTime) else None
            )
            abatement_fhir: FHIRDateTime | None = getattr(
                condition, "abatementDateTime", None
            )
            abatement = (
                abatement_fhir.isostring
                if isinstance(abatement_fhir, FHIRDateTime)
                else None
            )

            self.cursor.execute(
                """
                INSERT INTO conditions (id, patient_id, code, onset, abatement)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    patient_id = EXCLUDED.patient_id,
                    code = EXCLUDED.code,
                    onset = EXCLUDED.onset,
                    abatement = EXCLUDED.abatement
                """,
                (cond_id, patient_ref, code, onset, abatement),
            )

            return True
        except Exception as e:
            print(f"Error saving condition {condition.id}: {e}")
            return False

    def find_similar_patients(
        self, patient_id: str, limit: int = 5
    ) -> list[tuple[str, float]]:
        """Find similar patients based on embedding similarity"""
        try:
            self.cursor.execute(
                """
                SELECT p2.id, p2.first_name, p2.last_name, 
                       1 - (p1.embedding <=> p2.embedding) as similarity
                FROM patients p1, patients p2
                WHERE p1.id = %s AND p2.id != %s AND p1.embedding IS NOT NULL AND p2.embedding IS NOT NULL
                ORDER BY p1.embedding <=> p2.embedding
                LIMIT %s
                """,
                (patient_id, patient_id, limit),
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error finding similar patients: {e}")
            return []

    def find_similar_observations(
        self, observation_text: str, limit: int = 5
    ) -> list[tuple[str, str, float]]:
        """Find similar observations based on text similarity"""
        try:
            # Generate embedding for the query text
            query_embedding = embedding_model.encode(observation_text).tolist()

            self.cursor.execute(
                """
                SELECT id, code, 1 - (embedding <=> %s) as similarity
                FROM observations
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (query_embedding, query_embedding, limit),
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error finding similar observations: {e}")
            return []
