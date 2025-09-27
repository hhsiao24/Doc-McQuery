import { cn } from "@/lib/utils";
import { Outlet, useNavigate, useSearchParams } from "react-router";
import { Logo } from "../ui/logo";
import { hospitals } from "@/lib/hospitals";
import { CircleUserRound, LogOut } from "lucide-react";

export const WithHeader = () => {
  const [searchParams] = useSearchParams();
  const hospital = searchParams.get("h");
  const hospitalName = hospitals.find((h) => h.value === hospital)?.label;
  const nav = useNavigate();

  const handleLogout = () => {
    nav("/");
  };

  return (
    <div
      className={cn(
        "fixed p-6 w-screen h-screen top-0 left-0 bg-[#303234] overflow-y-scroll",
      )}
    >
      <div className="flex flex-row justify-between items-start">
        <Logo />
        <div className="flex flex-row items-center gap-4">
          {hospital && (
            <div
              className="bg-[#3B3D3F] rounded-lg px-4 py-2 cursor-pointer"
              onClick={handleLogout}
            >
              {hospitalName}
            </div>
          )}
          <CircleUserRound />
          <LogOut className="cursor-pointer" onClick={handleLogout} />
        </div>
      </div>
      <Outlet />
    </div>
  );
};
