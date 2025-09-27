import { Card } from "@/components/ui/card";
import { Text } from "@/components/ui/text";
import type { CaseStudyData } from "@/lib/api/search";
import { useState } from "react";
import { CaseStudyPopup } from "./caseStudyPopup";

export interface CaseStudyCardProps {
  caseStudy: CaseStudyData;
}

export const CaseStudyCard = ({ caseStudy }: CaseStudyCardProps) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Card
        className="flex flex-col items-stretch gap-2 cursor-pointer hover:shadow-2xl transition-all"
        onClick={() => setOpen(true)}
      >
        <Text size="p" className="font-bold">
          {caseStudy.name}
        </Text>
        <div className="bg-[#86A9C1] w-fit px-2 rounded shadow-sm">
          <Text size="c">PMID: {caseStudy.pubmed_id}</Text>
        </div>
        <Text size="c">{caseStudy.summary.notes}</Text>
      </Card>
      <CaseStudyPopup
        open={open}
        onClose={() => setOpen(false)}
        caseStudy={caseStudy}
      />
    </>
  );
};
