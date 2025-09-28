import { cn } from "@/lib/utils";
import { Text } from "./text";
import { useNavigate } from "react-router";

interface LogoProps {
  large?: boolean;
}

export const Logo = ({ large = false }: LogoProps) => {
  const nav = useNavigate();

  const handleToHome = () => {
    nav("/");
  };

  return (
    <div
      className={cn(
        "flex flex-row items-center gap-4 cursor-pointer",
        large ? "h-48" : "h-32",
      )}
      onClick={handleToHome}
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
