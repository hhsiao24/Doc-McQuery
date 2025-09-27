import { cn } from "@/lib/utils";
import type { ComponentProps, ReactNode } from "react";

export interface TextProps extends ComponentProps<"p"> {
  children?: ReactNode;
  size?: "t1" | "t2" | "h1" | "h2" | "h3" | "p" | "c";
}

export const Text = ({
  children,
  size = "p",
  className,
  ...props
}: TextProps) => {
  const sizeClasses: Record<NonNullable<TextProps["size"]>, string> = {
    t1: "text-[72px] font-[Sedan] text-[#86A9C1]",
    t2: "text-[28px] font-[Sedan_SC] text-[#D5E5EF]",
    h1: "text-[32px] font-bold font-[inter]",
    h2: "text-[28px] font-bold font-[inter]",
    h3: "text-[24px] font-medium font-[inter]",
    p: "text-[20px] font-normal font-[inter]",
    c: "text-[16px] font-normal font-[inter]",
  };

  return (
    <div
      className={cn("text-white text-left", sizeClasses[size], className)}
      {...props}
    >
      {children}
    </div>
  );
};
