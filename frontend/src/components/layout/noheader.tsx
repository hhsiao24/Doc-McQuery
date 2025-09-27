import { cn } from "@/lib/utils";
import { Outlet } from "react-router";

export const NoHeader = () => {
  return (
    <div className={cn("fixed w-screen h-screen top-0 left-0 bg-[#242526]")}>
      <Outlet />
    </div>
  );
};
