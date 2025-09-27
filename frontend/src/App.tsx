import { BrowserRouter, Route, Routes } from "react-router";
import "./App.css";
import { NoHeader } from "./components/layout/noheader";
import { Homepage } from "./pages/home/homepage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<NoHeader />}>
          <Route path="/" element={<Homepage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
