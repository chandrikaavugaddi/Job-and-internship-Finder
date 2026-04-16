import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Internships from "./pages/Internships";
import Jobs from "./pages/Jobs";
import SearchPage from "./pages/SearchPage";

import "./App.css";

function App() {
  return (

    <BrowserRouter>

      <Navbar />

      <Routes>

        <Route path="/" element={<Home />} />

        <Route path="/internships" element={<Internships />} />

        <Route path="/jobs" element={<Jobs />} />

        <Route path="/search" element={<SearchPage />} />

      </Routes>

    </BrowserRouter>

  );
}

export default App;