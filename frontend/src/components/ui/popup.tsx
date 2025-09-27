import { X } from "lucide-react";
import { Card, type CardProps } from "./card";
import { cn } from "@/lib/utils";

export interface PopupProps extends CardProps {
  open: boolean;
  onClose: () => any;
}

export const Popup = ({
  open,
  onClose,
  className,
  children,
  ...props
}: PopupProps) => {
  return (
    open && (
      <div
        className={cn(
          "fixed w-screen h-screen top-0 left-0 z-1000",
          "flex items-center justify-center backdrop-blur-sm bg-black/40",
        )}
        onClick={onClose}
      >
        <Card
          className={cn(
            "relative py-8 px-4 min-w-2xl max-h-[90vh] overflow-scroll",
            className,
          )}
          {...props}
          onClick={(e) => e.stopPropagation()}
        >
          {children}
          <X
            className={cn("absolute top-4 right-4 cursor-pointer")}
            onClick={onClose}
          />
        </Card>
      </div>
    )
  );
};
