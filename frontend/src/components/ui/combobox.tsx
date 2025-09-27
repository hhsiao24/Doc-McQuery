import { useEffect, useState } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { Button } from "./button";
import { type ComboBoxOption } from "@/types/ComboBoxOption";
import { Check, ChevronsUpDown } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "./command";
import { cn } from "@/lib/utils";

export interface ComboBoxProps {
  options: ComboBoxOption[];
  onSelect: (v: ComboBoxOption | null) => any;
  placeholder?: string;
  disabled?: boolean;
}

export const ComboBox = ({
  options,
  onSelect,
  placeholder,
  disabled = false,
}: ComboBoxProps) => {
  const [open, setOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState<string | null>(null);
  const selected = options.find((opt) => opt.value === selectedValue);

  useEffect(() => {
    onSelect(selected ?? null);
  }, [selectedValue]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          disabled={disabled}
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
        >
          {selected?.label ?? placeholder ?? "Select option..."}
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput
            placeholder={placeholder ?? "Select option..."}
            className="h-9"
          />
          <CommandList>
            <CommandEmpty>Nothing found.</CommandEmpty>
            <CommandGroup>
              {options.map((opt) => (
                <CommandItem
                  key={opt.value}
                  value={opt.label}
                  onSelect={(currentValue) => {
                    const newSelectedValue = options.find(
                      (opt) => opt.label === currentValue,
                    )?.value;
                    setSelectedValue(
                      newSelectedValue === selectedValue || !newSelectedValue
                        ? null
                        : newSelectedValue,
                    );
                    setOpen(false);
                  }}
                >
                  {opt.label}
                  <Check
                    className={cn(
                      "ml-auto",
                      selectedValue === opt.value ? "opacity-100" : "opacity-0",
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};
