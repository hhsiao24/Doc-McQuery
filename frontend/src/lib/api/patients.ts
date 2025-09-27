import axios from "axios";

export interface PatientData {
  first_name: string;
  last_name: string;
  id: string;
}

export const getPatients = async () => {
  const res = await axios.get("http://localhost:5001/patients_list");
  return res.data;
};
