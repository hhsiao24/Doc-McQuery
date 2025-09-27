import { ComboBox } from "@/components/ui/combobox";
import { Logo } from "@/components/ui/logo";
import { Text } from "@/components/ui/text";
import { hospitals } from "@/lib/hospitals";
import { cn } from "@/lib/utils";
import type { ComboBoxOption } from "@/types/ComboBoxOption";
import { useNavigate } from "react-router";

export const Homepage = () => {
  const nav = useNavigate();

  const onSelect = (hospital: ComboBoxOption | null) => {
    if (hospital) nav(`login/${hospital.value}`);
  };

  return (
    <div
      className={cn(
        "relative w-screen min-h-screen -z-10 overflow-hidden",
        "flex flex-col items-center justify-center gap-16",
      )}
    >
      <Logo large />
      <div className="w-11/12 max-w-3xl flex flex-col items-center gap-6">
        <Text size="h3" className="w-xl text-center">
          We deliver fast and relevant medical insights so you can deliver
          personalized and informed medical care.
        </Text>
        <Text size="h3" className="w-xl text-center">
          Before we begin, please select your hospital.
        </Text>
        <ComboBox options={hospitals} onSelect={onSelect} />
      </div>
      <div className="w-screen h-screen absolute -z-1" />
      <img
        src="/360_F_238084232_5XhGUddDZezzJxybvVXzfPp8cOKAuqRp.png"
        alt="image of stethoscope"
        className={cn(
          "w-screen h-screen absolute -z-2 object-cover",
          "opacity-10",
        )}
      />
    </div>
  );
};
