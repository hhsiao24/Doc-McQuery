import { Button } from "@/components/ui/button";
import { ComboBox } from "@/components/ui/combobox";
import { Input } from "@/components/ui/input";
import { Text } from "@/components/ui/text";
import { cn } from "@/lib/utils";
import type { ComboBoxOption } from "@/types/ComboBoxOption";
import { useState } from "react";

export const SearchPage = () => {
  const [patient, setPatient] = useState<ComboBoxOption | null>(null);
  const [query, setQuery] = useState<string>("");
  const [searching, setSearching] = useState(false);
  const [hasContent, setHasContent] = useState(false);

  // TODO: Get users from backend
  const patients = [
    { label: "Dew", value: "0b2437a7-d3e1-4d10-8a23-e4431bfd681b" },
  ];
  const searchDisabled = searching || !(patient && query);

  const onChangePatient = (patient: ComboBoxOption | null) => {};

  return (
    <div className={cn("w-full pt-8", "flex flex-col items-center")}>
      <div className="flex flex-row w-full max-w-5xl gap-4">
        <ComboBox
          options={patients}
          onSelect={onChangePatient}
          placeholder="Select a patient..."
          disabled={searching}
        />
        <Input
          id="searchQuery"
          className="flex"
          placeholder="Enter relevant information pertaining to your patient. (Ex. Symptoms, Known Diagnoses, etc.)"
          value={query}
          onChange={(el) => setQuery(el.target.value)}
          disabled={searching}
        />
        <Button
          disabled={searchDisabled}
          className={cn(
            "hover:opacity-50",
            searchDisabled ? "cursor-not-allowed" : "cursor-pointer",
          )}
        >
          Search
        </Button>
      </div>
      {hasContent ? (
        <></>
      ) : (
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
      )}
    </div>
  );
};
