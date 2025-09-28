import { Card } from "@/components/ui/card";
import { Popup } from "@/components/ui/popup";
import { Text } from "@/components/ui/text";
import { type CaseStudyData, type SituationalSummary } from "@/lib/api/search";
import { cn } from "@/lib/utils";

export interface CaseStudyPopupProps {
  open: boolean;
  onClose: () => any;
  caseStudy: CaseStudyData;
}

export const CaseStudyPopup = ({
  open,
  onClose,
  caseStudy,
}: CaseStudyPopupProps) => {
  const url = `https://pubmed.ncbi.nlm.nih.gov/${caseStudy.pubmed_id}/`;

  return (
    <Popup
      open={open}
      onClose={onClose}
      className={cn("max-w-3xl p-8 flex flex-col gap-2", "bg-[#292B2D]")}
    >
      <Text size="h2">{caseStudy.name}</Text>
      <a href={url} target="_blank" className="w-fit">
        <div className="bg-[#86A9C1] px-2 rounded shadow-sm">
          <Text size="c">PMID: {caseStudy.pubmed_id}</Text>
        </div>
      </a>
      <Text>{caseStudy.summary.notes}</Text>
      <Text className="font-bold pt-8 pb-4">Case Study Key Situations</Text>
      <div className="pb-4 flex flex-col items-stretch gap-4">
        {caseStudy.summary.situational_summary.map((summary) => (
          <SituationCard summary={summary} />
        ))}
      </div>
    </Popup>
  );
};

export interface SituationCardProps {
  summary: SituationalSummary;
}

export const SituationCard = ({ summary }: SituationCardProps) => {
  return (
    <Card className="bg-[#343639] flex flex-col items-stretch gap-2">
      <Text>
        <b>Characteristics:</b> {summary.characteristics}
      </Text>
      <Text>
        <b>Event:</b> {summary.event}
      </Text>
      <Text>
        <b>History:</b> {summary.history}
      </Text>
      <Text>
        <b>Onset:</b> {summary.onset}
      </Text>
      <Text>
        <b>Outcome:</b> {summary.outcome}
      </Text>
      <Text>
        <b>Treatment:</b> {summary.treatment}
      </Text>
    </Card>
  );
};
