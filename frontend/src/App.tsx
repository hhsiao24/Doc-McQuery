import { BrowserRouter, Route, Routes } from "react-router";
import { NoHeader } from "./components/layout/noheader";
import { Homepage as HomePage } from "./pages/home/homepage";
import { LoginPage } from "./pages/login/loginpage";
import { WithHeader } from "./components/layout/withheader";
import { SearchPage } from "./pages/search/searchpage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<NoHeader />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/login/:h?" element={<LoginPage />} />
        </Route>
        <Route element={<WithHeader />}>
          <Route path="/search/:h?" element={<SearchPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
