import { BrowserRouter, Route, Routes } from "react-router";
import { NoHeader } from "./components/layout/noheader";
import { Homepage } from "./pages/home/homepage";
import { Loginpage } from "./pages/login/loginpage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<NoHeader />}>
          <Route path="/" element={<Homepage />} />
          <Route path="/login/:h" element={<Loginpage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
