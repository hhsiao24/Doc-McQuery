import glob
import json
import os

from fhirclient.models.bundle import Bundle
from src.db import Database
from tqdm import tqdm

db = Database()


def process_file(file: str):
    """Process FHIR bundle file and save to database with embeddings"""
    try:
        with open(file, "r") as f:
            bundle_json = json.load(f)

        # Load the bundle
        bundle = Bundle(bundle_json)

        # First pass: Process and commit all patients
        for entry in bundle.entry or []:
            resource = entry.resource
            if resource is None:
                continue

            rtype = resource.resource_type
            if rtype == "Patient":
                db.save_patient(resource)

        db.commit_connection()

        # Second pass: Process observations and conditions
        for entry in bundle.entry or []:
            resource = entry.resource
            if resource is None:
                continue

            rtype = resource.resource_type
            if rtype == "Observation":
                db.save_observation(resource)
            elif rtype == "Condition":
                db.save_condition(resource)

        # Final commit for observations and conditions
        db.commit_connection()

    except Exception as e:
        print(f"Error processing file {file}: {e}")
        db.rollback_commit()


def process_directory(directory_path: str, max_files: int | None = None):
    """Process multiple FHIR files from a directory with a progress bar"""
    # Get all JSON files in the directory
    json_pattern = os.path.join(directory_path, "*.json")
    json_files = glob.glob(json_pattern)

    if not json_files:
        print(f"No JSON files found in {directory_path}")
        return

    # Sort files for consistent processing order
    json_files.sort()

    # Limit to max_files if specified
    if max_files:
        json_files = json_files[:max_files]

    print(f"Processing {len(json_files)} files from {directory_path}")

    successful_files = 0
    failed_files = 0

    # Use tqdm for progress bar
    for file_path in tqdm(json_files, desc="Processing files", unit="file"):
        try:
            process_file(file_path)  # Call your existing process_file function
            successful_files += 1
        except Exception as e:
            print(f"\nFailed to process {file_path}: {e}")
            failed_files += 1

    print(f"\nProcessing complete:")
    print(f"  Successfully processed: {successful_files} files")
    print(f"  Failed: {failed_files} files")


def main(max_files: int | None = None):
    # Define the directory path
    directory_path = "output/fhir/"

    # Process files based on max_files parameter
    if max_files:
        print(f"Processing first {max_files} files from {directory_path}")
        process_directory(directory_path, max_files)
    else:
        print(f"Processing all files from {directory_path}")
        process_directory(directory_path)


if __name__ == "__main__":
    main(1153)
