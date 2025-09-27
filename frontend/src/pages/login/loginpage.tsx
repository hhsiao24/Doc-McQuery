import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Logo } from "@/components/ui/logo";
import { hospitals } from "@/lib/hospitals";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { toast } from "sonner";

export const Loginpage = () => {
  const params = useParams();
  const nav = useNavigate();
  const [hospital, setHospital] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (!params.h) {
      // navigate back to home page
      nav("/");
    } else {
      const hospitalName = hospitals.find((h) => h.value === params.h)?.label;
      if (!hospitalName) {
        nav("/");
      } else {
        setHospital(hospitalName);
      }
    }
  }, [params.h]);

  const checkLogin = () => {
    if (!username || !password) {
      toast.error("Please enter both your username and password");
    } else {
      if (password !== "query") {
        toast.error("Incorrect password. Please try again.");
      } else {
        nav("/search");
      }
    }
  };

  return (
    <div className="w-screen h-screen p-8">
      <Logo />
      <div
        className={cn(
          "absolute top-0 left-0 w-screen h-screen",
          "flex items-center justify-center",
        )}
      >
        <div
          className={cn(
            "w-lg p-8",
            "flex flex-col items-center",
            "bg-[#292B2D] rounded-xl shadow-lg",
          )}
        >
          <Button className="w-full p-6 bg-[#3B3D3F] text-white text-lg hover:bg-[#3B3D3F]">
            {hospital}
          </Button>
          <div className="w-sm flex flex-col items-center justify-around py-8 gap-4">
            <div className="w-full">
              <label htmlFor="login-username">Username</label>
              <Input
                id="login-username"
                name="username"
                type="email"
                onChange={(v) => setUsername(v.target.value)}
                value={username}
              />
            </div>
            <div className="w-full">
              <label htmlFor="login-username">Password</label>
              <Input
                id="login-password"
                name="password"
                type="password"
                onChange={(v) => setPassword(v.target.value)}
                value={password}
              />
            </div>
            <Button onClick={checkLogin}>Login</Button>
          </div>
        </div>
      </div>
    </div>
  );
};
