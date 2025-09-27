import { cn } from "@/lib/utils";
import type { ComponentProps } from "react";

export interface CardProps extends ComponentProps<"div"> {}

export const Card = ({ children, className, ...props }: CardProps) => {
  return (
    <div
      className={cn("p-4 rounded-lg shadow-lg bg-[#343639]", className)}
      {...props}
    >
      {children}
    </div>
  );
};
