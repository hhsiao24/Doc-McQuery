import { Button } from "@/components/ui/button";
import { ComboBox } from "@/components/ui/combobox";
import { Input } from "@/components/ui/input";
import { Text } from "@/components/ui/text";
import { getPatients, type PatientData } from "@/lib/api/patients";
import {
  type CaseStudyData,
  querySearch,
  type SimilarPatientData,
} from "@/lib/api/search";
import { cn } from "@/lib/utils";
import type { ComboBoxOption } from "@/types/ComboBoxOption";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { CaseStudyCard } from "./caseStudyCard";
import { PatientCard } from "./patientCard";

export const SearchPage = () => {
  const [patient, setPatient] = useState<ComboBoxOption | null>(null);
  const [query, setQuery] = useState<string>("");
  const [searchStage, setSearchStage] = useState<
    "wait" | "searching" | "fetched"
  >("wait");
  const [patients, setPatients] = useState<ComboBoxOption[]>([]);
  const [caseStudies, setCaseStudies] = useState<CaseStudyData[]>([]);
  const [similarPatients, setSimilarPatients] = useState<SimilarPatientData[]>(
    [],
  );

  const searchDisabled = searchStage === "searching" || !(patient && query);

  const onChangePatient = (patient: ComboBoxOption | null) => {
    setPatient(patient);
  };

  const handlePatientData = async () => {
    try {
      const patientData = await getPatients();
      const patients = patientData.map((p: PatientData) => {
        const name =
          p.first_name?.replace(/[0-9]/g, "") +
          " " +
          p.last_name?.replace(/[0-9]/g, "");

        return {
          value: p.id,
          label: name,
        };
      });
      setPatients(patients);
    } catch (err: any) {}
  };

  const handleSearch = async () => {
    if (!patient) {
      return;
    }

    try {
      setSearchStage("searching");
      await querySearch(patient?.value, query).then((searchData) => {
        setCaseStudies(searchData.case_study.results.summaries);
        setSimilarPatients(searchData.similar_patients);

        setSearchStage("fetched");
      });
    } catch (err: any) {
      console.error(err);
      toast("No data found!");
      setSearchStage("wait");
    }
  };

  useEffect(() => {
    handlePatientData();
  }, []);

  return (
    <div className={cn("w-full pt-8", "flex flex-col items-center")}>
      <div className="flex flex-row w-full max-w-5xl gap-4">
        <ComboBox
          options={patients}
          onSelect={onChangePatient}
          placeholder="Select a patient..."
          disabled={searchStage === "searching"}
        />
        <Input
          id="searchQuery"
          className="flex"
          placeholder="Enter relevant information pertaining to your patient. (Ex. Symptoms, Known Diagnoses, etc.)"
          value={query}
          onChange={(el) => setQuery(el.target.value)}
          disabled={searchStage === "searching"}
        />
        <Button
          disabled={searchDisabled}
          className={cn(
            "hover:opacity-50",
            searchDisabled ? "cursor-not-allowed" : "cursor-pointer",
          )}
          onClick={handleSearch}
        >
          Search
        </Button>
      </div>
      {searchStage === "searching" ? (
        <div className="w-full py-20 flex items-center justify-center">
          <div className="relative flex flex-col gap-4 w-134 h-82">
            <img
              src="/DrMcQueryAnim.gif"
              alt="Doc McQuery Logo"
              className="absolute h-64 bottom-0 left-20 object-contain"
            />
            <div className="absolute right top-0 right-0">
              <img
                src="/fb9ed5d9494b23e26c64f244c210f826.png"
                alt="text bubble"
                className="top-0 left-0 w-80 object-contain"
              />
              <Text
                size="h3"
                className="absolute w-60 top-10 left-9 text-black text-center"
              >
                Searching...
              </Text>
            </div>
          </div>
        </div>
      ) : searchStage === "wait" ? (
        <div className="w-full py-20 flex items-center justify-center">
          <div className="relative flex flex-col gap-4 w-134 h-82">
            <img
              src="/DocMcQueryTransparent.png"
              alt="Doc McQuery Logo"
              className="absolute h-64 bottom-0 left-20 object-contain"
            />
            <div className="absolute right top-0 right-0">
              <img
                src="/fb9ed5d9494b23e26c64f244c210f826.png"
                alt="text bubble"
                className="top-0 left-0 w-80 object-contain"
              />
              <Text
                size="h3"
                className="absolute w-60 top-6 left-9 text-black text-center"
              >
                Select a patient and enter symptoms to get started!
              </Text>
            </div>
          </div>
        </div>
      ) : (
        <div className="w-full grid grid-cols-2 pt-8 gap-4 gap-8">
          <div className="w-full flex flex-col items-stretch">
            <Text size="h2" className="mx-8">
              Case Studies
            </Text>
            <div className="bg-[#292B2D] m-4 p-4 shadow-lg rounded-lg flex flex-col gap-4">
              {caseStudies.length > 0 ? (
                caseStudies.map((caseStudy) => (
                  <CaseStudyCard caseStudy={caseStudy} />
                ))
              ) : (
                <Text>No related case studies found!</Text>
              )}
            </div>
          </div>
          <div className="w-full flex flex-col items-stretch">
            <Text size="h2" className="mx-8">
              Similar Patients
            </Text>
            <div className="bg-[#292B2D] m-4 p-4 shadow-lg rounded-lg flex flex-col gap-4">
              {similarPatients.length > 0 ? (
                similarPatients?.map((patient) => (
                  <PatientCard patient={patient} />
                ))
              ) : (
                <Text>No similar patients found!</Text>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
