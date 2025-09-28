import { cn } from "@/lib/utils";
import { Outlet } from "react-router";
import { Toaster } from "../ui/sonner";

export const NoHeader = () => {
  return (
    <div className={cn("fixed w-screen h-screen top-0 left-0 bg-[#303234]")}>
      <Toaster richColors />
      <Outlet />
    </div>
  );
};
