import { cn } from "@/lib/utils";
import { Text } from "./text";

interface LogoProps {
  large?: boolean;
}

export const Logo = ({ large = false }: LogoProps) => {
  return (
    <div
      className={cn(
        "flex flex-row items-center gap-4",
        large ? "h-48" : "h-32",
      )}
    >
      <img
        src="/DocMcQueryTransparent.png"
        className={large ? "h-56" : "h-32"}
        alt="Doc McQuery Logo"
      />
      <div className="flex flex-col -top-4">
        <Text
          size="t1"
          className={cn(
            large ? "text-[108px] leading-[1.2] -mb-2" : "leading-none",
          )}
        >
          Doc McQuery
        </Text>
        <Text
          size="t2"
          className={cn(large ? "text-[48px] leading-tight" : "-top-1")}
        >
          Smarter searches, better care.
        </Text>
      </div>
    </div>
  );
};
