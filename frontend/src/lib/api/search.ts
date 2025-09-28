import axios from "axios";

export interface SituationalSummary {
  characteristics: string;
  event: string;
  history: string;
  onset: string;
  outcome: string;
  treatment: string;
}

export interface CaseStudyData {
  name: string;
  pubmed_id: string;
  summary: {
    notes: string;
    patient: {
      age: string;
      gender: string;
    };
    situational_summary: SituationalSummary[];
  };
}

export interface SimilarPatientData {
  id: string;
  summary: {
    conditions_summary: string;
    patient: {
      age: string;
      gender: string;
    };
    symptoms_and_observations_summary: string;
  };
}

export interface SearchData {
  case_study: {
    patient: {
      emr_summary: {
        conditions_summary: string;
        patient: {
          age: string;
          gender: string;
        };
      };
      parsed_input: {
        patient_id: string;
        conditions: string[];
        diagnosis: string[];
        medications: string[];
        symptoms: string[];
        treatments: string[];
      };
    };
    results: {
      query: string;
      summaries: CaseStudyData[];
    };
  };
  similar_patients: SimilarPatientData[];
}

export const querySearch = async (
  patientId: string,
  query: string,
): Promise<SearchData> => {
  const res = await axios.post("http://localhost:5001/all_requests", {
    patient_id: patientId,
    patient_info: query,
  });
  return res.data;
};
