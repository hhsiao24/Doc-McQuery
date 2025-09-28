import { Card } from "@/components/ui/card";
import { Text } from "@/components/ui/text";
import type { SimilarPatientData } from "@/lib/api/search";

export interface PatientCardProps {
  patient: SimilarPatientData;
}

export const PatientCard = ({ patient }: PatientCardProps) => {
  return (
    <>
      <Card className="flex flex-col items-stretch gap-2 hover:shadow-2xl transition-all">
        <Text size="p" className="font-bold">
          {patient.summary.patient.gender[0].toUpperCase()}
          {patient.summary.patient.gender.substring(1)},{" "}
          {patient.summary.patient.age} yrs
        </Text>
        <Text size="c">
          <b>Conditions:</b> {patient.summary.conditions_summary}
        </Text>
        <Text size="c">
          <b>Symptoms:</b> {patient.summary.symptoms_and_observations_summary}
        </Text>
      </Card>
    </>
  );
};
